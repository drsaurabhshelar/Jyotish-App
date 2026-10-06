# Beginner Setup & Deployment Guide

This guide will walk you step-by-step through setting up, configuring, testing, and deploying your production-ready WhatsApp Astrology Consultation Bot.

---

## STEP 1: How to Create / Prepare the GitHub Repository

1. Log in to your [GitHub](https://github.com/) account.
2. Click the **+** icon in the upper right corner and select **New repository**.
3. Name your repository (e.g. `whatsapp-astrology-bot`).
4. Set visibility to **Private** to protect configuration files.
5. In your local terminal, navigate to your project directory and run:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of WhatsApp Astrology Bot"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/whatsapp-astrology-bot.git
   git push -u origin main
   ```

---

## STEP 2: How to Configure WhatsApp Business Platform / Cloud API

1. Go to the [Meta for Developers Portal](https://developers.facebook.com/) and sign in.
2. Click **My Apps** -> **Create App**.
3. Choose **Other** -> **Business** app type, name your app, and click **Create App**.
4. In the App Dashboard, scroll down to **WhatsApp** and click **Set up**.
5. Select or create a Meta Business Account.
6. Under WhatsApp -> **API Setup**, you will see:
   - Temporary Access Token
   - Phone Number ID
   - WhatsApp Business Account ID
7. Add a recipient phone number under "To" to send test WhatsApp messages during development.

---

## STEP 3: WhatsApp Credentials Required

To connect your application to WhatsApp Cloud API, you need:

1. `WHATSAPP_VERIFY_TOKEN`: A secret password string you create yourself (e.g., `my_custom_astrology_token_123`).
2. `WHATSAPP_ACCESS_TOKEN`: The System User / Permanent Token or Temporary Access Token from Meta Developer Portal.
3. `WHATSAPP_PHONE_NUMBER_ID`: The Phone Number ID listed under WhatsApp -> API Setup.
4. `WHATSAPP_APP_SECRET`: Found in Meta App Dashboard under **App settings** -> **Basic** -> **App Secret**.

---

## STEP 4: Where Each Credential Goes

Open your `.env` file (or set these environment variables on your production server) and paste:

```env
WHATSAPP_VERIFY_TOKEN="my_custom_astrology_token_123"
WHATSAPP_ACCESS_TOKEN="EAAG..."
WHATSAPP_PHONE_NUMBER_ID="10293847565"
WHATSAPP_APP_SECRET="a1b2c3d4e5f6..."
```

---

## STEP 5: How to Configure PhonePe Payment Integration

1. Register or log in to the [PhonePe Business Merchant Portal](https://merchant.phonepe.com/).
2. Complete your KYC requirements to activate your merchant account.
3. Navigate to **Developer Settings** / **API Keys** to retrieve your production merchant credentials.
4. For Sandbox/Testing, use PhonePe Test credentials:
   - Host URL: `https://api-preprod.phonepe.com/apis/pg-sandbox`
   - Test Merchant ID: `PGTESTPAYUAT`
   - Test Salt Key: `099eb0cd-02fe-4e0b-b08d-100494300015`
   - Test Salt Index: `1`

---

## STEP 6: PhonePe Credentials & Configuration Values Required

In your `.env` file, configure the following PhonePe variables:

```env
PHONEPE_MERCHANT_ID="YOUR_MERCHANT_ID"
PHONEPE_SALT_KEY="YOUR_SALT_KEY"
PHONEPE_SALT_INDEX="1"
PHONEPE_HOST_URL="https://api.phonepe.com/apis/hermes" # Sandbox: https://api-preprod.phonepe.com/apis/pg-sandbox
PHONEPE_REDIRECT_URL="https://your-domain.com/payment/redirect"
PHONEPE_CALLBACK_URL="https://your-domain.com/webhook/phonepe"
PHONEPE_UPI_ID="aadiyogi.rises@ybl"
```

---

## STEP 7: How to Configure Environment Variables

Create a file named `.env` in the root of the project by copying `.env.example`:

```bash
cp .env.example .env
```

Ensure all variables are populated properly without quotes around non-string values. **Never commit `.env` to Git.**

---

## STEP 8: How to Run the Application Locally

1. Install dependencies:
   ```bash
   npm install
   ```
2. Initialize SQLite database:
   ```bash
   npx prisma db push
   ```
3. Start local development server:
   ```bash
   npm run dev
   ```
4. Check health endpoint in your browser at `http://localhost:3000/health`.

---

## STEP 9: How to Expose Local Webhook for Testing

Meta and PhonePe require HTTPS public URLs to send webhook events. Use **ngrok**:

1. Install ngrok: `npm install -g ngrok` or download from [ngrok.com](https://ngrok.com/).
2. Run ngrok on port 3000:
   ```bash
   ngrok http 3000
   ```
3. Copy the HTTPS forwarding URL (e.g. `https://abc1234.ngrok-free.app`).
4. Update `APP_BASE_URL`, `PHONEPE_REDIRECT_URL`, and `PHONEPE_CALLBACK_URL` in `.env` with your ngrok URL.

---

## STEP 10: How to Deploy the Production Server

### Using Docker & Docker Compose:

1. Install Docker on your server (e.g. DigitalOcean, AWS EC2, or Linux VPS).
2. Clone your repository to the server.
3. Create `.env` file on server.
4. Run:
   ```bash
   docker-compose up -d --build
   ```

---

## STEP 11: How to Configure Production Webhook URL in Meta

1. In Meta Developer Dashboard, go to **WhatsApp** -> **Configuration**.
2. Under **Webhook**, click **Edit**.
3. Callback URL: `https://your-domain.com/webhook/whatsapp`
4. Verify Token: Enter the value you set for `WHATSAPP_VERIFY_TOKEN`.
5. Click **Verify and Save**.
6. Under **Webhook fields**, click **Manage** and subscribe to **messages**.

---

## STEP 12: How to Test the Entire Customer Journey

1. Open WhatsApp and send "Hello" to your WhatsApp Business Number.
2. Bot responds: *"Would you like to book an Astrology Consultation?"* [Yes] [No]
3. Test selecting "No" -> flow stops gracefully.
4. Send "Hello" again and select "Yes".
5. Choose question count: [1 Question] or [Multiple Questions].
6. Enter Full Name, Date of Birth (`DD/MM/YYYY`), Birth Time (`HH:MM AM/PM`), and Birth Place.
7. Confirm details or test editing incorrect details.
8. Click the payment link generated.
9. Verify that typing "I paid" does NOT mark payment successful unless verified by PhonePe API.
10. Complete test payment via PhonePe link or test webhook payload.
11. Confirm customer receives automated payment success confirmation on WhatsApp.

---

## STEP 13: How to Access Admin Dashboard

1. Open browser to `http://localhost:3000/admin` (or `https://your-domain.com/admin`).
2. Log in with initial credentials:
   - **Username**: `admin`
   - **Password**: `admin` (or password configured on initial creation)
3. View stats, list consultation requests, search customers, update consultation fee, and schedule appointments.

---

## STEP 14: How to Change Consultation Fee from ₹1,500

You can change the consultation fee in two ways:
1. **Via Admin Panel**: Log in to Admin Dashboard, change "Current Fee" field, and click **Update Fee**.
2. **Via `.env`**: Update `DEFAULT_CONSULTATION_FEE=2000` and restart server.

---

## STEP 15: How to Troubleshoot Common Problems

1. **Webhook verification fails (403)**: Ensure `WHATSAPP_VERIFY_TOKEN` in `.env` matches token entered in Meta portal exactly.
2. **Messages not being received by bot**: Ensure webhook subscription field `messages` is checked in Meta portal.
3. **PhonePe API error**: Ensure `PHONEPE_MERCHANT_ID`, `PHONEPE_SALT_KEY`, and `PHONEPE_SALT_INDEX` are correct and `PHONEPE_HOST_URL` matches your environment (sandbox vs production).
4. **Database lock error**: Delete `dev.db` and run `npx prisma db push`.
