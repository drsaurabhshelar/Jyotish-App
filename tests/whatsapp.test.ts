import { WhatsAppClient } from '../src/whatsapp/whatsapp.client';
import crypto from 'crypto';

describe('WhatsAppClient', () => {
  const appSecret = 'test_app_secret';
  const client = new WhatsAppClient({
    accessToken: 'test_token',
    phoneNumberId: '123456789',
    appSecret: appSecret,
  });

  test('should verify valid HMAC signature', () => {
    const rawBody = JSON.stringify({ object: 'whatsapp_business_account' });
    const hmac = crypto.createHmac('sha256', appSecret);
    const expectedSig = hmac.update(rawBody).digest('hex');
    const header = `sha256=${expectedSig}`;

    expect(client.verifySignature(rawBody, header)).toBe(true);
    expect(client.verifySignature(rawBody, 'sha256=invalid')).toBe(false);
  });

  test('should throw error if sending more than 3 interactive buttons', async () => {
    const buttons = [
      { id: '1', title: 'Btn 1' },
      { id: '2', title: 'Btn 2' },
      { id: '3', title: 'Btn 3' },
      { id: '4', title: 'Btn 4' },
    ];
    await expect(client.sendInteractiveButtons('1234567890', 'Hello', buttons)).rejects.toThrow();
  });
});
