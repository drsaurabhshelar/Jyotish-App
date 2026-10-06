export interface PaymentOrderParams {
  consultationId: string;
  amount: number; // in INR
  whatsappNumber: string;
  customerName?: string;
  redirectUrl?: string;
  callbackUrl?: string;
}

export interface PaymentOrderResult {
  orderId: string;
  paymentUrl: string;
  rawResponse?: any;
}

export interface PaymentStatusResult {
  orderId: string;
  transactionId?: string;
  status: 'SUCCESS' | 'FAILED' | 'PENDING';
  amount: number;
  rawResponse?: any;
}

export interface PaymentGateway {
  providerName: string;
  createOrder(params: PaymentOrderParams): Promise<PaymentOrderResult>;
  verifyPaymentStatus(orderId: string): Promise<PaymentStatusResult>;
  verifyWebhookSignature(headers: Record<string, any>, body: any): boolean;
  parseWebhookPayload(body: any): PaymentStatusResult;
}
