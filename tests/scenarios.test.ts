import request from 'supertest';
import { app } from '../src/index';
import { prisma } from '../src/db/prisma';

describe('Comprehensive End-to-End Scenarios', () => {
  const testNumber = '919876543210';

  beforeEach(async () => {
    // Clear test database tables before each scenario
    await prisma.webhookEvent.deleteMany({});
    await prisma.appointment.deleteMany({});
    await prisma.payment.deleteMany({});
    await prisma.consultationRequest.deleteMany({});
    await prisma.conversationState.deleteMany({});
    await prisma.customer.deleteMany({});
  });

  afterAll(async () => {
    await prisma.$disconnect();
  });

  // Helper to simulate incoming WhatsApp message
  const sendWhatsAppWebhook = async (from: string, text: string, buttonId?: string) => {
    const messageObj: any = {
      from,
      id: `wamid.test.${Date.now()}.${Math.random()}`,
    };

    if (buttonId) {
      messageObj.type = 'interactive';
      messageObj.interactive = {
        type: 'button_reply',
        button_reply: { id: buttonId, title: text },
      };
    } else {
      messageObj.type = 'text';
      messageObj.text = { body: text };
    }

    const payload = {
      object: 'whatsapp_business_account',
      entry: [
        {
          changes: [
            {
              value: {
                messages: [messageObj],
              },
            },
          ],
        },
      ],
    };

    return request(app).post('/webhook/whatsapp').send(payload);
  };

  test('Scenario 1: Customer sends first message -> Consultation Yes/No question appears & state is ASKING_CONSULTATION', async () => {
    const res = await sendWhatsAppWebhook(testNumber, 'Hello');
    expect(res.status).toBe(200);

    const customer = await prisma.customer.findUnique({
      where: { whatsappNumber: testNumber },
      include: { conversation: true },
    });

    expect(customer).not.toBeNull();
    expect(customer?.conversation?.state).toBe('ASKING_CONSULTATION');
  });

  test('Scenario 2: Customer selects No -> Flow ends gracefully (state = CONSULTATION_DECLINED) without asking personal details', async () => {
    await sendWhatsAppWebhook(testNumber, 'Hi');
    const res = await sendWhatsAppWebhook(testNumber, 'No', 'CONSULTATION_NO');
    expect(res.status).toBe(200);

    const customer = await prisma.customer.findUnique({
      where: { whatsappNumber: testNumber },
      include: { conversation: true },
    });

    expect(customer?.conversation?.state).toBe('CONSULTATION_DECLINED');
    expect(customer?.fullName).toBeNull();
    expect(customer?.dateOfBirth).toBeNull();
  });

  test('Scenario 3 & 4: Customer selects Yes -> question count prompt appears and customer selects 1 Question', async () => {
    await sendWhatsAppWebhook(testNumber, 'Hi');
    await sendWhatsAppWebhook(testNumber, 'Yes', 'CONSULTATION_YES');

    let customer = await prisma.customer.findUnique({
      where: { whatsappNumber: testNumber },
      include: { conversation: true },
    });
    expect(customer?.conversation?.state).toBe('ASKING_QUESTION_COUNT');

    await sendWhatsAppWebhook(testNumber, '1 Question', 'QUESTION_1');
    customer = await prisma.customer.findUnique({
      where: { whatsappNumber: testNumber },
      include: { conversation: true },
    });
    expect(customer?.conversation?.state).toBe('ASKING_FULL_NAME');
  });

  test('Scenario 5: Customer enters all four personal details step-by-step', async () => {
    await sendWhatsAppWebhook(testNumber, 'Hi');
    await sendWhatsAppWebhook(testNumber, 'Yes', 'CONSULTATION_YES');
    await sendWhatsAppWebhook(testNumber, '1 Question', 'QUESTION_1');

    // Enter Full Name
    await sendWhatsAppWebhook(testNumber, 'Rahul Sharma');
    let customer = await prisma.customer.findUnique({ where: { whatsappNumber: testNumber }, include: { conversation: true } });
    expect(customer?.fullName).toBe('Rahul Sharma');
    expect(customer?.conversation?.state).toBe('ASKING_DOB');

    // Enter Date of Birth
    await sendWhatsAppWebhook(testNumber, '12/05/1990');
    customer = await prisma.customer.findUnique({ where: { whatsappNumber: testNumber }, include: { conversation: true } });
    expect(customer?.dateOfBirth).toBe('12/05/1990');
    expect(customer?.conversation?.state).toBe('ASKING_BIRTH_TIME');

    // Enter Birth Time
    await sendWhatsAppWebhook(testNumber, '08:35 PM');
    customer = await prisma.customer.findUnique({ where: { whatsappNumber: testNumber }, include: { conversation: true } });
    expect(customer?.birthTime).toBe('08:35 PM');
    expect(customer?.conversation?.state).toBe('ASKING_BIRTH_PLACE');

    // Enter Birth Place
    await sendWhatsAppWebhook(testNumber, 'Pune, Maharashtra');
    customer = await prisma.customer.findUnique({ where: { whatsappNumber: testNumber }, include: { conversation: true } });
    expect(customer?.birthPlace).toBe('Pune, Maharashtra');
    expect(customer?.conversation?.state).toBe('CONFIRMING_DETAILS');
  });

  test('Scenario 6: Customer edits incorrect details', async () => {
    // Get to confirmation state
    await sendWhatsAppWebhook(testNumber, 'Hi');
    await sendWhatsAppWebhook(testNumber, 'Yes', 'CONSULTATION_YES');
    await sendWhatsAppWebhook(testNumber, '1 Question', 'QUESTION_1');
    await sendWhatsAppWebhook(testNumber, 'Rahul Sharma');
    await sendWhatsAppWebhook(testNumber, '12/05/1990');
    await sendWhatsAppWebhook(testNumber, '08:35 PM');
    await sendWhatsAppWebhook(testNumber, 'Pune');

    // Select Edit -> Edit Name
    await sendWhatsAppWebhook(testNumber, 'Edit', 'DETAILS_EDIT');
    await sendWhatsAppWebhook(testNumber, 'Full Name', 'EDIT_FULL_NAME');

    let customer = await prisma.customer.findUnique({ where: { whatsappNumber: testNumber }, include: { conversation: true } });
    expect(customer?.conversation?.state).toBe('ASKING_FULL_NAME');

    // Provide corrected name
    await sendWhatsAppWebhook(testNumber, 'Rahul V. Sharma');
    customer = await prisma.customer.findUnique({ where: { whatsappNumber: testNumber }, include: { conversation: true } });
    expect(customer?.fullName).toBe('Rahul V. Sharma');
  });

  test('Scenario 7: Payment link/checkout order is generated after confirming details', async () => {
    await sendWhatsAppWebhook(testNumber, 'Hi');
    await sendWhatsAppWebhook(testNumber, 'Yes', 'CONSULTATION_YES');
    await sendWhatsAppWebhook(testNumber, '1 Question', 'QUESTION_1');
    await sendWhatsAppWebhook(testNumber, 'Rahul Sharma');
    await sendWhatsAppWebhook(testNumber, '12/05/1990');
    await sendWhatsAppWebhook(testNumber, '08:35 PM');
    await sendWhatsAppWebhook(testNumber, 'Pune');

    // Confirm details
    await sendWhatsAppWebhook(testNumber, 'Confirm', 'DETAILS_CONFIRM');

    const customer = await prisma.customer.findUnique({ where: { whatsappNumber: testNumber }, include: { conversation: true } });
    expect(customer?.conversation?.state).toBe('AWAITING_PAYMENT');

    const consultation = await prisma.consultationRequest.findFirst({
      where: { customerId: customer?.id },
      include: { payments: true },
    });

    expect(consultation).not.toBeNull();
    expect(consultation?.fee).toBe(1500);
    expect(consultation?.payments.length).toBe(1);
    expect(consultation?.payments[0].status).toBe('PENDING');
  });

  test('Scenario 8 & 9: Fake "I paid" message does NOT mark payment successful, genuine payment DOES', async () => {
    await sendWhatsAppWebhook(testNumber, 'Hi');
    await sendWhatsAppWebhook(testNumber, 'Yes', 'CONSULTATION_YES');
    await sendWhatsAppWebhook(testNumber, '1 Question', 'QUESTION_1');
    await sendWhatsAppWebhook(testNumber, 'Rahul Sharma');
    await sendWhatsAppWebhook(testNumber, '12/05/1990');
    await sendWhatsAppWebhook(testNumber, '08:35 PM');
    await sendWhatsAppWebhook(testNumber, 'Pune');
    await sendWhatsAppWebhook(testNumber, 'Confirm', 'DETAILS_CONFIRM');

    // Customer types fake "I paid" text
    await sendWhatsAppWebhook(testNumber, 'I paid via UPI');

    let consultation = await prisma.consultationRequest.findFirst({ where: { customer: { whatsappNumber: testNumber } } });
    expect(consultation?.status).toBe('PENDING_PAYMENT'); // Unchanged!

    // Now send genuine verified webhook
    const payment = await prisma.payment.findFirst({ where: { consultationId: consultation?.id } });
    const phonepePayload = {
      response: Buffer.from(
        JSON.stringify({
          code: 'PAYMENT_SUCCESS',
          data: {
            merchantTransactionId: payment?.orderId,
            transactionId: 'TXN_VERIFIED_123',
            amount: 150000,
          },
        })
      ).toString('base64'),
    };

    await request(app).post('/webhook/phonepe').send(phonepePayload);

    consultation = await prisma.consultationRequest.findUnique({ where: { id: consultation?.id } });
    expect(consultation?.status).toBe('PENDING_SCHEDULING');

    const updatedPayment = await prisma.payment.findUnique({ where: { id: payment?.id } });
    expect(updatedPayment?.status).toBe('SUCCESS');
    expect(updatedPayment?.transactionId).toBe('TXN_VERIFIED_123');
  });

  test('Scenario 10: Duplicate payment callback does not create duplicate payment records', async () => {
    await sendWhatsAppWebhook(testNumber, 'Hi');
    await sendWhatsAppWebhook(testNumber, 'Yes', 'CONSULTATION_YES');
    await sendWhatsAppWebhook(testNumber, '1 Question', 'QUESTION_1');
    await sendWhatsAppWebhook(testNumber, 'Rahul Sharma');
    await sendWhatsAppWebhook(testNumber, '12/05/1990');
    await sendWhatsAppWebhook(testNumber, '08:35 PM');
    await sendWhatsAppWebhook(testNumber, 'Pune');
    await sendWhatsAppWebhook(testNumber, 'Confirm', 'DETAILS_CONFIRM');

    const consultation = await prisma.consultationRequest.findFirst({ where: { customer: { whatsappNumber: testNumber } } });
    const payment = await prisma.payment.findFirst({ where: { consultationId: consultation?.id } });

    const phonepePayload = {
      response: Buffer.from(
        JSON.stringify({
          code: 'PAYMENT_SUCCESS',
          data: {
            merchantTransactionId: payment?.orderId,
            transactionId: 'TXN_VERIFIED_123',
            amount: 150000,
          },
        })
      ).toString('base64'),
    };

    // Send twice
    await request(app).post('/webhook/phonepe').send(phonepePayload);
    await request(app).post('/webhook/phonepe').send(phonepePayload);

    const paymentCount = await prisma.payment.count({ where: { consultationId: consultation?.id } });
    expect(paymentCount).toBe(1);
  });

  test('Scenario 11: Server restart preserves conversation state', async () => {
    await sendWhatsAppWebhook(testNumber, 'Hi');
    await sendWhatsAppWebhook(testNumber, 'Yes', 'CONSULTATION_YES');

    // Read directly from DB simulating server restart
    const customer = await prisma.customer.findUnique({
      where: { whatsappNumber: testNumber },
      include: { conversation: true },
    });
    expect(customer?.conversation?.state).toBe('ASKING_QUESTION_COUNT');

    // Continue conversation after simulated restart
    await sendWhatsAppWebhook(testNumber, '1 Question', 'QUESTION_1');
    const updatedCustomer = await prisma.customer.findUnique({
      where: { whatsappNumber: testNumber },
      include: { conversation: true },
    });
    expect(updatedCustomer?.conversation?.state).toBe('ASKING_FULL_NAME');
  });

  test('Scenario 12 & 13: Admin can schedule appointment and send WhatsApp confirmation', async () => {
    // Setup verified consultation
    await sendWhatsAppWebhook(testNumber, 'Hi');
    await sendWhatsAppWebhook(testNumber, 'Yes', 'CONSULTATION_YES');
    await sendWhatsAppWebhook(testNumber, '1 Question', 'QUESTION_1');
    await sendWhatsAppWebhook(testNumber, 'Rahul Sharma');
    await sendWhatsAppWebhook(testNumber, '12/05/1990');
    await sendWhatsAppWebhook(testNumber, '08:35 PM');
    await sendWhatsAppWebhook(testNumber, 'Pune');
    await sendWhatsAppWebhook(testNumber, 'Confirm', 'DETAILS_CONFIRM');

    const consultation = await prisma.consultationRequest.findFirst({ where: { customer: { whatsappNumber: testNumber } } });
    const payment = await prisma.payment.findFirst({ where: { consultationId: consultation?.id } });

    await request(app).post('/webhook/phonepe').send({
      response: Buffer.from(
        JSON.stringify({
          code: 'PAYMENT_SUCCESS',
          data: { merchantTransactionId: payment?.orderId, transactionId: 'TXN_123', amount: 150000 },
        })
      ).toString('base64'),
    });

    // Login as Admin
    const loginRes = await request(app).post('/api/admin/login').send({ username: 'admin', password: 'password123' });
    const token = loginRes.body.token;

    // Schedule appointment via Admin API
    const scheduleRes = await request(app)
      .post('/api/admin/appointments/schedule')
      .set('Authorization', `Bearer ${token}`)
      .send({
        consultationId: consultation?.id,
        appointmentDate: '25/12/2024',
        appointmentTime: '05:00 PM',
        sendWhatsAppNotice: true,
      });

    expect(scheduleRes.status).toBe(200);
    expect(scheduleRes.body.appointment.status).toBe('SCHEDULED');
    expect(scheduleRes.body.appointment.appointmentDate).toBe('25/12/2024');
    expect(scheduleRes.body.whatsappSent).toBe(true);
  });

  test('Scenario 14 & 15: Invalid DOB and Birth Time are rejected', async () => {
    await sendWhatsAppWebhook(testNumber, 'Hi');
    await sendWhatsAppWebhook(testNumber, 'Yes', 'CONSULTATION_YES');
    await sendWhatsAppWebhook(testNumber, '1 Question', 'QUESTION_1');
    await sendWhatsAppWebhook(testNumber, 'Rahul Sharma');

    // Invalid DOB
    await sendWhatsAppWebhook(testNumber, '31/02/1990');
    let customer = await prisma.customer.findUnique({ where: { whatsappNumber: testNumber }, include: { conversation: true } });
    expect(customer?.conversation?.state).toBe('ASKING_DOB'); // Stays on ASKING_DOB

    // Valid DOB
    await sendWhatsAppWebhook(testNumber, '12/05/1990');
    customer = await prisma.customer.findUnique({ where: { whatsappNumber: testNumber }, include: { conversation: true } });
    expect(customer?.conversation?.state).toBe('ASKING_BIRTH_TIME');

    // Invalid Birth Time
    await sendWhatsAppWebhook(testNumber, '25:00 PM');
    customer = await prisma.customer.findUnique({ where: { whatsappNumber: testNumber }, include: { conversation: true } });
    expect(customer?.conversation?.state).toBe('ASKING_BIRTH_TIME'); // Stays on ASKING_BIRTH_TIME
  });
});
