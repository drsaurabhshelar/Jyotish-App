# WhatsApp Astrology Consultation Bot

Production-ready WhatsApp Astrology Consultation booking bot built for Meta WhatsApp Business Cloud API with PhonePe payment gateway integration and a secure Admin Panel.

## Features

- **Official WhatsApp Cloud API**: Native interactive buttons and messages.
- **Strict Flow Compliance**:
  - Initial question: *"Would you like to book an Astrology Consultation?"* [Yes] [No].
  - Selecting "No" ends the flow gracefully without requesting personal information.
  - Step-by-step detail collection (Full Name, DOB, Birth Time, Birth Place) with validation and Edit summary options.
- **Genuine Payment Verification**:
  - PhonePe Payment Provider abstraction layer (Order creation, status verification API, signature verification).
  - Explicit rejection of typed messages like "I paid" - payments are verified server-side.
  - Optional support for direct UPI ID display (`PHONEPE_UPI_ID=aadiyogi.rises@ybl`).
- **Persistent State Machine**: Relational database storage ensuring conversation state survives server restarts.
- **Admin Dashboard**:
  - Filter consultations by payment status and appointment scheduling status.
  - Search customers by WhatsApp number or name.
  - Update consultation fee dynamically without touching code.
  - Manual appointment scheduling with automated WhatsApp confirmation trigger.

## Stack

- **Backend**: Node.js, TypeScript, Express.js
- **Database**: Prisma ORM with SQLite (development/testing) / PostgreSQL support
- **Testing**: Jest, Supertest

## Quick Start

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Initialize Database:
   ```bash
   npx prisma db push
   ```
4. Run in Development mode:
   ```bash
   npm run dev
   ```
5. Run Tests:
   ```bash
   npm test
   ```

For detailed step-by-step setup and credentials guide, please see [SETUP_GUIDE.md](SETUP_GUIDE.md).
