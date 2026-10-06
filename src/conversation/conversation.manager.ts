import { prisma } from '../db/prisma';
import { messages } from '../config/messages';
import { env } from '../config/env';
import { logger } from '../config/logger';
import { WhatsAppClient } from '../whatsapp/whatsapp.client';
import { PaymentGateway } from '../payments/payment-gateway.interface';
import { isValidDateFormat, isValidTimeFormat } from '../utils/validators';

export enum CustomerState {
  NEW = 'NEW',
  ASKING_CONSULTATION = 'ASKING_CONSULTATION',
  CONSULTATION_DECLINED = 'CONSULTATION_DECLINED',
  ASKING_QUESTION_COUNT = 'ASKING_QUESTION_COUNT',
  ASKING_FULL_NAME = 'ASKING_FULL_NAME',
  ASKING_DOB = 'ASKING_DOB',
  ASKING_BIRTH_TIME = 'ASKING_BIRTH_TIME',
  ASKING_BIRTH_PLACE = 'ASKING_BIRTH_PLACE',
  CONFIRMING_DETAILS = 'CONFIRMING_DETAILS',
  AWAITING_PAYMENT = 'AWAITING_PAYMENT',
  PAYMENT_PENDING = 'PAYMENT_PENDING',
  PAYMENT_FAILED = 'PAYMENT_FAILED',
  PAYMENT_SUCCESSFUL = 'PAYMENT_SUCCESSFUL',
  APPOINTMENT_PENDING = 'APPOINTMENT_PENDING',
  APPOINTMENT_SCHEDULED = 'APPOINTMENT_SCHEDULED',
  COMPLETED = 'COMPLETED',
}

export class ConversationManager {
  private whatsapp: WhatsAppClient;
  private paymentGateway: PaymentGateway;

  constructor(whatsapp: WhatsAppClient, paymentGateway: PaymentGateway) {
    this.whatsapp = whatsapp;
    this.paymentGateway = paymentGateway;
  }

  /**
   * Helper to get current consultation fee from SystemConfig or fallback to ENV default
   */
  public async getConsultationFee(): Promise<number> {
    const config = await prisma.systemConfig.findUnique({
      where: { key: 'CONSULTATION_FEE' },
    });
    if (config && !isNaN(parseInt(config.value, 10))) {
      return parseInt(config.value, 10);
    }
    return env.DEFAULT_CONSULTATION_FEE;
  }

  /**
   * Process incoming customer message
   */
  public async handleIncomingMessage(
    whatsappNumber: string,
    messageBody: string,
    buttonId?: string
  ): Promise<void> {
    logger.info(`Handling message from ${whatsappNumber}: body="${messageBody}", buttonId="${buttonId}"`);

    // 1. Get or create Customer
    let customer = await prisma.customer.findUnique({
      where: { whatsappNumber },
      include: { conversation: true },
    });

    if (!customer) {
      customer = await prisma.customer.create({
        data: {
          whatsappNumber,
          conversation: {
            create: {
              state: CustomerState.NEW,
              dataJson: JSON.stringify({}),
            },
          },
        },
        include: { conversation: true },
      });
    }

    let conversation = customer.conversation;
    if (!conversation) {
      conversation = await prisma.conversationState.create({
        data: {
          customerId: customer.id,
          state: CustomerState.NEW,
          dataJson: JSON.stringify({}),
        },
      });
    }

    const currentState = conversation.state as CustomerState;
    const conversationData = JSON.parse(conversation.dataJson || '{}');

    // Rule 9/10: If customer types "I paid" or "payment done", reject fake payment verification text
    const lowerBody = messageBody.trim().toLowerCase();
    if (
      lowerBody.includes('i paid') ||
      lowerBody.includes('payment done') ||
      lowerBody.includes('paid done') ||
      lowerBody.includes('payment successfully')
    ) {
      if (
        currentState === CustomerState.AWAITING_PAYMENT ||
        currentState === CustomerState.PAYMENT_PENDING ||
        currentState === CustomerState.PAYMENT_FAILED
      ) {
        // If there's an active consultation, double-check real status with payment provider API
        const latestConsultation = await prisma.consultationRequest.findFirst({
          where: { customerId: customer.id },
          orderBy: { createdAt: 'desc' },
          include: { payments: true },
        });

        if (latestConsultation && latestConsultation.payments.length > 0) {
          const latestPayment = latestConsultation.payments[latestConsultation.payments.length - 1];
          const verification = await this.paymentGateway.verifyPaymentStatus(latestPayment.orderId);

          if (verification.status === 'SUCCESS') {
            await this.markPaymentSuccessful(customer.id, latestConsultation.id, latestPayment.id, verification.transactionId);
            return;
          }
        }

        // Otherwise reject text claim
        await this.whatsapp.sendTextMessage(whatsappNumber, messages.TYPED_PAYMENT_REJECTED);
        return;
      }
    }

    // Process State Machine Transitions
    await this.processStateTransition(
      customer,
      conversation,
      currentState,
      conversationData,
      messageBody.trim(),
      buttonId
    );
  }

  private async updateState(
    conversationId: string,
    newState: CustomerState,
    newDataJson: object
  ): Promise<void> {
    await prisma.conversationState.update({
      where: { id: conversationId },
      data: {
        state: newState,
        dataJson: JSON.stringify(newDataJson),
      },
    });
  }

  private async processStateTransition(
    customer: any,
    conversation: any,
    currentState: CustomerState,
    data: any,
    text: string,
    buttonId?: string
  ): Promise<void> {
    const whatsappNumber = customer.whatsappNumber;

    // RULE 1 & 2: First contact / NEW state
    if (currentState === CustomerState.NEW || currentState === CustomerState.ASKING_CONSULTATION) {
      if (buttonId === 'CONSULTATION_YES' || text.toLowerCase() === 'yes') {
        // Customer selected YES -> Ask question count
        await this.updateState(conversation.id, CustomerState.ASKING_QUESTION_COUNT, data);
        await this.whatsapp.sendInteractiveButtons(whatsappNumber, messages.QUESTION_COUNT_PROMPT, [
          { id: 'QUESTION_1', title: messages.BUTTON_1_QUESTION },
          { id: 'QUESTION_MULTIPLE', title: messages.BUTTON_MULTIPLE_QUESTIONS },
        ]);
        return;
      }

      if (buttonId === 'CONSULTATION_NO' || text.toLowerCase() === 'no') {
        // RULE 3: Customer selected NO -> Stop conversation gracefully, do NOT ask personal info
        await this.updateState(conversation.id, CustomerState.CONSULTATION_DECLINED, data);
        await this.whatsapp.sendTextMessage(whatsappNumber, messages.NO_RESPONSE_END);
        return;
      }

      // If user sent initial message, show initial consultation prompt with Yes/No buttons
      await this.updateState(conversation.id, CustomerState.ASKING_CONSULTATION, data);
      await this.whatsapp.sendInteractiveButtons(whatsappNumber, messages.CONSULTATION_INITIAL_PROMPT, [
        { id: 'CONSULTATION_YES', title: messages.BUTTON_YES },
        { id: 'CONSULTATION_NO', title: messages.BUTTON_NO },
      ]);
      return;
    }

    // CONSULTATION DECLINED state - if user messages again, present option again
    if (currentState === CustomerState.CONSULTATION_DECLINED) {
      await this.updateState(conversation.id, CustomerState.ASKING_CONSULTATION, data);
      await this.whatsapp.sendInteractiveButtons(whatsappNumber, messages.CONSULTATION_INITIAL_PROMPT, [
        { id: 'CONSULTATION_YES', title: messages.BUTTON_YES },
        { id: 'CONSULTATION_NO', title: messages.BUTTON_NO },
      ]);
      return;
    }

    // RULE 4: QUESTION COUNT SELECTION
    if (currentState === CustomerState.ASKING_QUESTION_COUNT) {
      let questionType = '1_QUESTION';
      if (buttonId === 'QUESTION_MULTIPLE' || text.toLowerCase().includes('multiple')) {
        questionType = 'MULTIPLE_QUESTIONS';
      }
      data.questionType = questionType;

      // Move to ASKING_FULL_NAME
      await this.updateState(conversation.id, CustomerState.ASKING_FULL_NAME, data);
      await this.whatsapp.sendTextMessage(whatsappNumber, messages.ASK_FULL_NAME);
      return;
    }

    // RULE 6: ASKING FULL NAME
    if (currentState === CustomerState.ASKING_FULL_NAME) {
      if (!text || text.length < 2) {
        await this.whatsapp.sendTextMessage(whatsappNumber, messages.INVALID_TEXT);
        return;
      }
      data.fullName = text;
      await prisma.customer.update({
        where: { id: customer.id },
        data: { fullName: text },
      });

      await this.updateState(conversation.id, CustomerState.ASKING_DOB, data);
      await this.whatsapp.sendTextMessage(whatsappNumber, messages.ASK_DOB);
      return;
    }

    // RULE 6: ASKING DATE OF BIRTH
    if (currentState === CustomerState.ASKING_DOB) {
      if (!isValidDateFormat(text)) {
        await this.whatsapp.sendTextMessage(whatsappNumber, messages.INVALID_DOB);
        return;
      }
      data.dateOfBirth = text;
      await prisma.customer.update({
        where: { id: customer.id },
        data: { dateOfBirth: text },
      });

      await this.updateState(conversation.id, CustomerState.ASKING_BIRTH_TIME, data);
      await this.whatsapp.sendTextMessage(whatsappNumber, messages.ASK_BIRTH_TIME);
      return;
    }

    // RULE 6: ASKING BIRTH TIME
    if (currentState === CustomerState.ASKING_BIRTH_TIME) {
      if (!isValidTimeFormat(text)) {
        await this.whatsapp.sendTextMessage(whatsappNumber, messages.INVALID_BIRTH_TIME);
        return;
      }
      data.birthTime = text;
      await prisma.customer.update({
        where: { id: customer.id },
        data: { birthTime: text },
      });

      await this.updateState(conversation.id, CustomerState.ASKING_BIRTH_PLACE, data);
      await this.whatsapp.sendTextMessage(whatsappNumber, messages.ASK_BIRTH_PLACE);
      return;
    }

    // RULE 6: ASKING BIRTH PLACE
    if (currentState === CustomerState.ASKING_BIRTH_PLACE) {
      if (!text || text.length < 2) {
        await this.whatsapp.sendTextMessage(whatsappNumber, messages.INVALID_TEXT);
        return;
      }
      data.birthPlace = text;
      await prisma.customer.update({
        where: { id: customer.id },
        data: { birthPlace: text },
      });

      // RULE 7: SHOW CONFIRMATION SUMMARY
      await this.sendConfirmationSummary(customer.id, whatsappNumber, conversation.id, data);
      return;
    }

    // RULE 7: CONFIRMING DETAILS / EDIT FLOW
    if (currentState === CustomerState.CONFIRMING_DETAILS) {
      if (buttonId === 'DETAILS_CONFIRM' || text.toLowerCase() === 'confirm') {
        // Customer confirmed details -> Create ConsultationRequest & generate payment link
        await this.initiatePaymentStep(customer, conversation, data);
        return;
      }

      if (buttonId === 'DETAILS_EDIT' || text.toLowerCase() === 'edit') {
        // Show edit field options
        await this.whatsapp.sendInteractiveButtons(whatsappNumber, messages.EDIT_SELECTION_PROMPT, [
          { id: 'EDIT_FULL_NAME', title: messages.BUTTON_EDIT_NAME },
          { id: 'EDIT_DOB', title: messages.BUTTON_EDIT_DOB },
          { id: 'EDIT_BIRTH_TIME', title: messages.BUTTON_EDIT_TIME },
        ]);
        // Also send fallback text for birth place edit since max 3 buttons per WhatsApp interactive message
        await this.whatsapp.sendTextMessage(whatsappNumber, "Or reply 'Place' to edit Birth Place.");
        return;
      }

      if (buttonId === 'EDIT_FULL_NAME' || text.toLowerCase().includes('name')) {
        await this.updateState(conversation.id, CustomerState.ASKING_FULL_NAME, data);
        await this.whatsapp.sendTextMessage(whatsappNumber, messages.ASK_FULL_NAME);
        return;
      }

      if (buttonId === 'EDIT_DOB' || text.toLowerCase().includes('date') || text.toLowerCase().includes('dob')) {
        await this.updateState(conversation.id, CustomerState.ASKING_DOB, data);
        await this.whatsapp.sendTextMessage(whatsappNumber, messages.ASK_DOB);
        return;
      }

      if (buttonId === 'EDIT_BIRTH_TIME' || text.toLowerCase().includes('time')) {
        await this.updateState(conversation.id, CustomerState.ASKING_BIRTH_TIME, data);
        await this.whatsapp.sendTextMessage(whatsappNumber, messages.ASK_BIRTH_TIME);
        return;
      }

      if (text.toLowerCase().includes('place')) {
        await this.updateState(conversation.id, CustomerState.ASKING_BIRTH_PLACE, data);
        await this.whatsapp.sendTextMessage(whatsappNumber, messages.ASK_BIRTH_PLACE);
        return;
      }

      // Re-send confirmation summary
      await this.sendConfirmationSummary(customer.id, whatsappNumber, conversation.id, data);
      return;
    }

    // RULE 8 & 10: AWAITING PAYMENT / PAYMENT FAILED
    if (currentState === CustomerState.AWAITING_PAYMENT || currentState === CustomerState.PAYMENT_FAILED) {
      if (buttonId === 'TRY_PAYMENT_AGAIN' || text.toLowerCase().includes('try') || text.toLowerCase().includes('pay')) {
        await this.initiatePaymentStep(customer, conversation, data);
        return;
      }

      // Prompt for payment again
      const fee = await this.getConsultationFee();
      let promptMsg = messages.PAYMENT_PROMPT.replace('{fee}', fee.toLocaleString('en-IN'));
      if (env.PHONEPE_UPI_ID) {
        promptMsg += `\n\nOr UPI ID: ${env.PHONEPE_UPI_ID}`;
      }
      await this.whatsapp.sendTextMessage(whatsappNumber, promptMsg);
      return;
    }

    // DEFAULT FALLBACK
    await this.whatsapp.sendInteractiveButtons(whatsappNumber, messages.CONSULTATION_INITIAL_PROMPT, [
      { id: 'CONSULTATION_YES', title: messages.BUTTON_YES },
      { id: 'CONSULTATION_NO', title: messages.BUTTON_NO },
    ]);
  }

  private async sendConfirmationSummary(customerId: string, whatsappNumber: string, conversationId: string, data: any): Promise<void> {
    const customer = await prisma.customer.findUnique({ where: { id: customerId } });
    const fullName = customer?.fullName || data.fullName || '';
    const dob = customer?.dateOfBirth || data.dateOfBirth || '';
    const birthTime = customer?.birthTime || data.birthTime || '';
    const birthPlace = customer?.birthPlace || data.birthPlace || '';

    const summaryText = messages.CONFIRM_DETAILS_HEADER
      .replace('{fullName}', fullName)
      .replace('{dob}', dob)
      .replace('{birthTime}', birthTime)
      .replace('{birthPlace}', birthPlace);

    await this.updateState(conversationId, CustomerState.CONFIRMING_DETAILS, data);
    await this.whatsapp.sendInteractiveButtons(whatsappNumber, summaryText, [
      { id: 'DETAILS_CONFIRM', title: messages.BUTTON_CONFIRM },
      { id: 'DETAILS_EDIT', title: messages.BUTTON_EDIT },
    ]);
  }

  private async initiatePaymentStep(customer: any, conversation: any, data: any): Promise<void> {
    const fee = await this.getConsultationFee();

    // Create Consultation Request
    const consultation = await prisma.consultationRequest.create({
      data: {
        customerId: customer.id,
        questionType: data.questionType || '1_QUESTION',
        fee: fee,
        status: 'PENDING_PAYMENT',
      },
    });

    // Create Payment Order
    const paymentOrder = await this.paymentGateway.createOrder({
      consultationId: consultation.id,
      amount: fee,
      whatsappNumber: customer.whatsappNumber,
      customerName: customer.fullName || '',
    });

    // Save Payment Record
    await prisma.payment.create({
      data: {
        consultationId: consultation.id,
        provider: this.paymentGateway.providerName,
        orderId: paymentOrder.orderId,
        amount: fee,
        status: 'PENDING',
        rawResponse: JSON.stringify(paymentOrder.rawResponse || {}),
      },
    });

    data.consultationId = consultation.id;
    data.orderId = paymentOrder.orderId;

    await this.updateState(conversation.id, CustomerState.AWAITING_PAYMENT, data);

    let paymentPrompt = messages.PAYMENT_PROMPT.replace('{fee}', fee.toLocaleString('en-IN'));
    paymentPrompt += `\n\nPayment Link:\n${paymentOrder.paymentUrl}`;
    if (env.PHONEPE_UPI_ID) {
      paymentPrompt += `\n\nOr Pay directly via UPI ID: ${env.PHONEPE_UPI_ID}`;
    }

    await this.whatsapp.sendTextMessage(customer.whatsappNumber, paymentPrompt);
  }

  /**
   * Helper called when payment is genuinely verified as successful via Webhook or Status API
   */
  public async markPaymentSuccessful(
    customerId: string,
    consultationId: string,
    paymentId: string,
    transactionId?: string
  ): Promise<void> {
    // Prevent duplicate payment processing (Idempotency)
    const existingPayment = await prisma.payment.findUnique({
      where: { id: paymentId },
    });

    if (existingPayment?.status === 'SUCCESS') {
      logger.info(`Payment ${paymentId} already marked SUCCESS. Skipping duplicate handling.`);
      return;
    }

    // Update Payment
    await prisma.payment.update({
      where: { id: paymentId },
      data: {
        status: 'SUCCESS',
        transactionId: transactionId || existingPayment?.transactionId,
        paidAt: new Date(),
      },
    });

    // Update Consultation
    await prisma.consultationRequest.update({
      where: { id: consultationId },
      data: { status: 'PENDING_SCHEDULING' },
    });

    // Create or reset Appointment record to PENDING_SCHEDULING
    await prisma.appointment.upsert({
      where: { consultationId },
      create: {
        consultationId,
        status: 'PENDING_SCHEDULING',
      },
      update: {
        status: 'PENDING_SCHEDULING',
      },
    });

    // Update Customer Conversation State
    const customer = await prisma.customer.findUnique({
      where: { id: customerId },
      include: { conversation: true },
    });

    if (customer?.conversation) {
      await this.updateState(customer.conversation.id, CustomerState.PAYMENT_SUCCESSFUL, {
        consultationId,
        paymentId,
      });
    }

    // RULE 11: Send success message to customer
    if (customer?.whatsappNumber) {
      await this.whatsapp.sendTextMessage(customer.whatsappNumber, messages.PAYMENT_SUCCESSFUL);
    }
  }
}
