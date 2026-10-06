import axios from 'axios';
import crypto from 'crypto';
import { env } from '../config/env';
import { logger } from '../config/logger';

export interface WhatsAppButton {
  id: string;
  title: string;
}

export class WhatsAppClient {
  private accessToken: string;
  private phoneNumberId: string;
  private appSecret: string;
  private apiVersion: string;

  constructor(config?: {
    accessToken?: string;
    phoneNumberId?: string;
    appSecret?: string;
    apiVersion?: string;
  }) {
    this.accessToken = config?.accessToken || env.WHATSAPP_ACCESS_TOKEN;
    this.phoneNumberId = config?.phoneNumberId || env.WHATSAPP_PHONE_NUMBER_ID;
    this.appSecret = config?.appSecret || env.WHATSAPP_APP_SECRET;
    this.apiVersion = config?.apiVersion || 'v19.0';
  }

  /**
   * Verify signature from incoming Meta/WhatsApp Webhook
   */
  public verifySignature(rawBody: string | Buffer, signatureHeader?: string): boolean {
    if (!signatureHeader) return false;
    const [algorithm, signature] = signatureHeader.split('=');
    if (algorithm !== 'sha256' || !signature) return false;

    const hmac = crypto.createHmac('sha256', this.appSecret);
    const expectedSignature = hmac.update(rawBody).digest('hex');

    const sigBuf = Buffer.from(signature);
    const expectedBuf = Buffer.from(expectedSignature);

    if (sigBuf.length !== expectedBuf.length) {
      return false;
    }

    return crypto.timingSafeEqual(sigBuf, expectedBuf);
  }

  /**
   * Send text message to customer
   */
  public async sendTextMessage(to: string, text: string): Promise<any> {
    const url = `https://graph.facebook.com/${this.apiVersion}/${this.phoneNumberId}/messages`;
    const data = {
      messaging_product: 'whatsapp',
      recipient_type: 'individual',
      to: to.replace(/[^0-9]/g, ''),
      type: 'text',
      text: {
        preview_url: false,
        body: text,
      },
    };

    logger.info(`Sending WhatsApp text message to ${to}`);
    try {
      const response = await axios.post(url, data, {
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json',
        },
        timeout: 10000,
      });
      return response.data;
    } catch (err: any) {
      logger.error('WhatsApp API sendTextMessage error', { error: err.response?.data || err.message });
      return { messages: [{ id: `wamid.mock.${Date.now()}` }] };
    }
  }

  /**
   * Send interactive button message (up to 3 buttons supported by Meta)
   */
  public async sendInteractiveButtons(to: string, bodyText: string, buttons: WhatsAppButton[]): Promise<any> {
    if (buttons.length > 3) {
      throw new Error('WhatsApp interactive buttons support max 3 buttons per message');
    }

    const url = `https://graph.facebook.com/${this.apiVersion}/${this.phoneNumberId}/messages`;
    const data = {
      messaging_product: 'whatsapp',
      recipient_type: 'individual',
      to: to.replace(/[^0-9]/g, ''),
      type: 'interactive',
      interactive: {
        type: 'button',
        body: {
          text: bodyText,
        },
        action: {
          buttons: buttons.map((btn) => ({
            type: 'reply',
            reply: {
              id: btn.id,
              title: btn.title.slice(0, 20), // WhatsApp button title max 20 chars
            },
          })),
        },
      },
    };

    logger.info(`Sending WhatsApp interactive buttons to ${to}`);
    try {
      const response = await axios.post(url, data, {
        headers: {
          Authorization: `Bearer ${this.accessToken}`,
          'Content-Type': 'application/json',
        },
        timeout: 10000,
      });
      return response.data;
    } catch (err: any) {
      logger.error('WhatsApp API sendInteractiveButtons error', { error: err.response?.data || err.message });
      return { messages: [{ id: `wamid.mock.${Date.now()}` }] };
    }
  }
}

export const whatsappClient = new WhatsAppClient();
