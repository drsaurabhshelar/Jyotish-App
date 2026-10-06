import { PhonePePaymentProvider } from '../src/payments/phonepe.provider';

describe('PhonePePaymentProvider', () => {
  const provider = new PhonePePaymentProvider({
    merchantId: 'TEST_MERCHANT',
    saltKey: 'test_salt_key',
    saltIndex: '1',
    hostUrl: 'https://api-preprod.phonepe.com/apis/pg-sandbox',
  });

  test('should construct provider and generate correct webhook signature verification', () => {
    expect(provider.providerName).toBe('PHONEPE');

    // Test fake webhook verification
    const body = { response: Buffer.from(JSON.stringify({ code: 'PAYMENT_SUCCESS', data: { merchantTransactionId: 'TXN123', amount: 150000 } })).toString('base64') };
    const isValid = provider.verifyWebhookSignature({}, body);
    expect(isValid).toBe(false); // No x-verify header provided
  });

  test('should parse webhook payload correctly', () => {
    const rawData = {
      code: 'PAYMENT_SUCCESS',
      data: {
        merchantTransactionId: 'TXN_12345',
        transactionId: 'T123456789',
        amount: 150000,
      },
    };
    const encoded = Buffer.from(JSON.stringify(rawData)).toString('base64');
    const parsed = provider.parseWebhookPayload({ response: encoded });

    expect(parsed.orderId).toBe('TXN_12345');
    expect(parsed.transactionId).toBe('T123456789');
    expect(parsed.status).toBe('SUCCESS');
    expect(parsed.amount).toBe(1500);
  });
});
