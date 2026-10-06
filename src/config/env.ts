import dotenv from 'dotenv';
import { z } from 'zod';

dotenv.config();

const envSchema = z.object({
  PORT: z.string().default('3000').transform((val) => parseInt(val, 10)),
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  APP_BASE_URL: z.string().default('http://localhost:3000'),
  DATABASE_URL: z.string().default('file:./dev.db'),
  JWT_SECRET: z.string().default('default_dev_jwt_secret_must_be_changed_for_prod'),
  DEFAULT_CONSULTATION_FEE: z.string().default('1500').transform((val) => parseInt(val, 10)),

  // WhatsApp
  WHATSAPP_VERIFY_TOKEN: z.string().default('dev_verify_token'),
  WHATSAPP_ACCESS_TOKEN: z.string().default('dev_access_token'),
  WHATSAPP_PHONE_NUMBER_ID: z.string().default('dev_phone_number_id'),
  WHATSAPP_APP_SECRET: z.string().default('dev_app_secret'),

  // PhonePe
  PHONEPE_MERCHANT_ID: z.string().default('PGTESTPAYUAT'),
  PHONEPE_SALT_KEY: z.string().default('099eb0cd-02fe-4e0b-b08d-100494300015'),
  PHONEPE_SALT_INDEX: z.string().default('1'),
  PHONEPE_HOST_URL: z.string().default('https://api-preprod.phonepe.com/apis/pg-sandbox'),
  PHONEPE_REDIRECT_URL: z.string().default('http://localhost:3000/payment/redirect'),
  PHONEPE_CALLBACK_URL: z.string().default('http://localhost:3000/webhook/phonepe'),
  PHONEPE_UPI_ID: z.string().optional(),
});

export const env = envSchema.parse(process.env);
