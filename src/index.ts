import express, { Request, Response } from 'express';
import path from 'path';
import cors from 'cors';
import { env } from './config/env';
import { logger } from './config/logger';
import { prisma } from './db/prisma';
import { adminRouter } from './admin/admin.router';
import { WhatsAppClient } from './whatsapp/whatsapp.client';
import { PhonePePaymentProvider } from './payments/phonepe.provider';
import { ConversationManager } from './conversation/conversation.manager';

export const app = express();

app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve Admin UI static files
app.use('/admin', express.static(path.join(__dirname, '../public/admin')));

// Admin API Routes
app.use('/api/admin', adminRouter);

// Initialize WhatsApp and PhonePe clients & Conversation Manager
const whatsappClient = new WhatsAppClient();
const phonePeProvider = new PhonePePaymentProvider();
const conversationManager = new ConversationManager(whatsappClient, phonePeProvider);

// GET /health - Health Check Endpoint
app.get('/health', async (req: Request, res: Response) => {
  try {
    await prisma.$queryRaw`SELECT 1`;
    return res.status(200).json({ status: 'OK', database: 'connected', timestamp: new Date() });
  } catch (err: any) {
    return res.status(500).json({ status: 'ERROR', database: 'disconnected', error: err.message });
  }
});

// GET /webhook/whatsapp - Meta/WhatsApp Webhook Verification
app.get('/webhook/whatsapp', (req: Request, res: Response) => {
  const mode = req.query['hub.mode'];
  const token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  if (mode === 'subscribe' && token === env.WHATSAPP_VERIFY_TOKEN) {
    logger.info('WhatsApp webhook verified successfully');
    return res.status(200).send(challenge);
  } else {
    logger.warn('WhatsApp webhook verification failed');
    return res.sendStatus(403);
  }
});

// POST /webhook/whatsapp - WhatsApp Incoming Message Handling
app.post('/webhook/whatsapp', async (req: Request, res: Response) => {
  try {
    const rawBody = JSON.stringify(req.body);
    const signature = req.headers['x-hub-signature-256'] as string;

    // Verify signature in production if appSecret provided
    if (env.NODE_ENV === 'production' && !whatsappClient.verifySignature(rawBody, signature)) {
      logger.warn('WhatsApp webhook signature verification failed');
      return res.sendStatus(401);
    }

    const body = req.body;
    if (body.object === 'whatsapp_business_account') {
      const entries = body.entry || [];
      for (const entry of entries) {
        const changes = entry.changes || [];
        for (const change of changes) {
          const value = change.value || {};
          const messages = value.messages || [];

          for (const message of messages) {
            const messageId = message.id;

            // Idempotency: Prevent processing duplicate webhooks
            if (messageId) {
              const existingEvent = await prisma.webhookEvent.findUnique({ where: { eventId: messageId } });
              if (existingEvent) {
                logger.info(`Duplicate WhatsApp webhook event ${messageId}. Skipping.`);
                continue;
              }

              await prisma.webhookEvent.create({
                data: {
                  eventId: messageId,
                  source: 'WHATSAPP',
                  payloadJson: JSON.stringify(message),
                  processed: true,
                },
              });
            }

            const from = message.from;
            let textBody = '';
            let buttonId = undefined;

            if (message.type === 'text') {
              textBody = message.text?.body || '';
            } else if (message.type === 'interactive' && message.interactive?.type === 'button_reply') {
              buttonId = message.interactive.button_reply.id;
              textBody = message.interactive.button_reply.title;
            }

            // Process message via conversation manager
            if (from) {
              await conversationManager.handleIncomingMessage(from, textBody, buttonId);
            }
          }
        }
      }
    }

    return res.status(200).send('EVENT_RECEIVED');
  } catch (err: any) {
    logger.error('Error processing WhatsApp webhook', { error: err.message });
    return res.status(200).send('EVENT_RECEIVED'); // Always return 200 to Meta to prevent retries
  }
});

// POST /webhook/phonepe - PhonePe Payment Callback Endpoint
app.post('/webhook/phonepe', async (req: Request, res: Response) => {
  try {
    const parsedPayload = phonePeProvider.parseWebhookPayload(req.body);
    const { orderId, transactionId, status } = parsedPayload;

    logger.info(`PhonePe webhook received for order ${orderId}: status=${status}`);

    const eventId = `phonepe_${orderId}_${status}`;
    const existingEvent = await prisma.webhookEvent.findUnique({ where: { eventId } });
    if (existingEvent) {
      logger.info(`Duplicate PhonePe webhook event ${eventId}. Skipping.`);
      return res.status(200).json({ status: 'SUCCESS' });
    }

    await prisma.webhookEvent.create({
      data: {
        eventId,
        source: 'PHONEPE',
        payloadJson: JSON.stringify(req.body),
        processed: true,
      },
    });

    const payment = await prisma.payment.findUnique({
      where: { orderId },
      include: { consultation: true },
    });

    if (payment) {
      if (status === 'SUCCESS') {
        await conversationManager.markPaymentSuccessful(
          payment.consultation.customerId,
          payment.consultationId,
          payment.id,
          transactionId
        );
      } else if (status === 'FAILED') {
        await prisma.payment.update({
          where: { id: payment.id },
          data: { status: 'FAILED' },
        });
      }
    }

    return res.status(200).json({ status: 'SUCCESS' });
  } catch (err: any) {
    logger.error('Error processing PhonePe webhook', { error: err.message });
    return res.status(200).json({ status: 'SUCCESS' });
  }
});

// GET /payment/redirect - User Payment Redirect Endpoint
app.get('/payment/redirect', async (req: Request, res: Response) => {
  const merchantTransactionId = (req.query.merchantTransactionId || req.query.transactionId) as string;

  if (merchantTransactionId) {
    const payment = await prisma.payment.findUnique({
      where: { orderId: merchantTransactionId },
      include: { consultation: true },
    });

    if (payment) {
      // Verify payment status with PhonePe API directly upon redirect
      const verification = await phonePeProvider.verifyPaymentStatus(merchantTransactionId);
      if (verification.status === 'SUCCESS') {
        await conversationManager.markPaymentSuccessful(
          payment.consultation.customerId,
          payment.consultationId,
          payment.id,
          verification.transactionId
        );
        return res.send('<h2>Payment Successful! You can close this page and return to WhatsApp.</h2>');
      }
    }
  }

  return res.send('<h2>Payment status is being processed. Please check WhatsApp for updates.</h2>');
});

if (process.env.NODE_ENV !== 'test') {
  app.listen(env.PORT, () => {
    logger.info(`Server running on port ${env.PORT}`);
    logger.info(`Admin Dashboard available at http://localhost:${env.PORT}/admin`);
  });
}
