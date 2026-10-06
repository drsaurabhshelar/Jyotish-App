import express, { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import { prisma } from '../db/prisma';
import { env } from '../config/env';
import { logger } from '../config/logger';
import { WhatsAppClient } from '../whatsapp/whatsapp.client';
import { messages } from '../config/messages';

export const adminRouter = express.Router();

export interface AuthRequest extends Request {
  user?: { id: string; username: string; role: string };
}

// Middleware: Authenticate Admin JWT Token
export function authenticateAdmin(req: AuthRequest, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Unauthorized: Missing or invalid token' });
  }

  const token = authHeader.split(' ')[1];
  try {
    const decoded = jwt.verify(token, env.JWT_SECRET) as { id: string; username: string; role: string };
    req.user = decoded;
    next();
  } catch (err) {
    return res.status(401).json({ error: 'Unauthorized: Invalid or expired token' });
  }
}

// POST /api/admin/login
adminRouter.post('/login', async (req: Request, res: Response) => {
  const { username, password } = req.body;
  if (!username || !password) {
    return res.status(400).json({ error: 'Username and password are required' });
  }

  // Find or auto-seed admin if none exists in dev
  let admin = await prisma.adminUser.findUnique({ where: { username } });
  if (!admin) {
    const adminCount = await prisma.adminUser.count();
    if (adminCount === 0 && username === 'admin') {
      const passwordHash = await bcrypt.hash(password, 10);
      admin = await prisma.adminUser.create({
        data: {
          username: 'admin',
          passwordHash,
          role: 'ADMIN',
        },
      });
      logger.info('Created initial admin account');
    } else {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
  }

  const isPasswordValid = await bcrypt.compare(password, admin.passwordHash);
  if (!isPasswordValid) {
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  const token = jwt.sign(
    { id: admin.id, username: admin.username, role: admin.role },
    env.JWT_SECRET,
    { expiresIn: '24h' }
  );

  return res.json({ token, user: { id: admin.id, username: admin.username, role: admin.role } });
});

// GET /api/admin/consultations - List consultation requests with filtering and search
adminRouter.get('/consultations', authenticateAdmin, async (req: AuthRequest, res: Response) => {
  try {
    const { paymentStatus, appointmentStatus, search } = req.query;

    const whereClause: any = {};

    if (paymentStatus) {
      whereClause.payments = {
        some: { status: String(paymentStatus).toUpperCase() },
      };
    }

    if (appointmentStatus) {
      whereClause.appointment = {
        status: String(appointmentStatus).toUpperCase(),
      };
    }

    if (search) {
      const searchStr = String(search).trim();
      whereClause.customer = {
        OR: [
          { whatsappNumber: { contains: searchStr } },
          { fullName: { contains: searchStr } },
        ],
      };
    }

    const consultations = await prisma.consultationRequest.findMany({
      where: whereClause,
      include: {
        customer: true,
        payments: true,
        appointment: true,
      },
      orderBy: { createdAt: 'desc' },
    });

    return res.json({ consultations });
  } catch (err: any) {
    logger.error('Error fetching consultations in admin API', { error: err.message });
    return res.status(500).json({ error: 'Failed to fetch consultations' });
  }
});

// GET /api/admin/stats - Basic statistics
adminRouter.get('/stats', authenticateAdmin, async (req: AuthRequest, res: Response) => {
  try {
    const totalRequests = await prisma.consultationRequest.count();
    const successfulPayments = await prisma.payment.count({ where: { status: 'SUCCESS' } });
    const pendingAppointments = await prisma.appointment.count({ where: { status: 'PENDING_SCHEDULING' } });
    const scheduledAppointments = await prisma.appointment.count({ where: { status: 'SCHEDULED' } });

    const totalRevenueResult = await prisma.payment.aggregate({
      where: { status: 'SUCCESS' },
      _sum: { amount: true },
    });

    return res.json({
      totalRequests,
      successfulPayments,
      pendingAppointments,
      scheduledAppointments,
      totalRevenue: totalRevenueResult._sum.amount || 0,
    });
  } catch (err: any) {
    logger.error('Error fetching admin stats', { error: err.message });
    return res.status(500).json({ error: 'Failed to fetch statistics' });
  }
});

// GET /api/admin/config/fee - Get current consultation fee
adminRouter.get('/config/fee', authenticateAdmin, async (req: AuthRequest, res: Response) => {
  const config = await prisma.systemConfig.findUnique({ where: { key: 'CONSULTATION_FEE' } });
  const fee = config ? parseInt(config.value, 10) : env.DEFAULT_CONSULTATION_FEE;
  return res.json({ fee });
});

// POST /api/admin/config/fee - Update consultation fee
adminRouter.post('/config/fee', authenticateAdmin, async (req: AuthRequest, res: Response) => {
  const { fee } = req.body;
  if (!fee || isNaN(parseInt(fee, 10)) || parseInt(fee, 10) <= 0) {
    return res.status(400).json({ error: 'Valid positive integer fee is required' });
  }

  const numericFee = parseInt(fee, 10);
  await prisma.systemConfig.upsert({
    where: { key: 'CONSULTATION_FEE' },
    create: {
      key: 'CONSULTATION_FEE',
      value: numericFee.toString(),
      description: 'Default consultation fee in INR',
    },
    update: {
      value: numericFee.toString(),
    },
  });

  return res.json({ message: 'Consultation fee updated successfully', fee: numericFee });
});

// POST /api/admin/appointments/schedule - Schedule appointment and optionally send WhatsApp confirmation
adminRouter.post('/appointments/schedule', authenticateAdmin, async (req: AuthRequest, res: Response) => {
  const { consultationId, appointmentDate, appointmentTime, notes, sendWhatsAppNotice } = req.body;

  if (!consultationId || !appointmentDate || !appointmentTime) {
    return res.status(400).json({ error: 'consultationId, appointmentDate, and appointmentTime are required' });
  }

  const consultation = await prisma.consultationRequest.findUnique({
    where: { id: consultationId },
    include: { customer: true, appointment: true },
  });

  if (!consultation) {
    return res.status(404).json({ error: 'Consultation request not found' });
  }

  // Update or Create Appointment
  const appointment = await prisma.appointment.upsert({
    where: { consultationId },
    create: {
      consultationId,
      status: 'SCHEDULED',
      appointmentDate,
      appointmentTime,
      notes,
    },
    update: {
      status: 'SCHEDULED',
      appointmentDate,
      appointmentTime,
      notes,
    },
  });

  // Update Consultation status
  await prisma.consultationRequest.update({
    where: { id: consultationId },
    data: { status: 'SCHEDULED' },
  });

  // Send WhatsApp confirmation if requested
  let whatsappSent = false;
  if (sendWhatsAppNotice && consultation.customer.whatsappNumber) {
    const whatsappClient = new WhatsAppClient();
    const noticeText = messages.APPOINTMENT_SCHEDULED_NOTIFICATION
      .replace('{date}', appointmentDate)
      .replace('{time}', appointmentTime);

    await whatsappClient.sendTextMessage(consultation.customer.whatsappNumber, noticeText);
    whatsappSent = true;
  }

  return res.json({
    message: 'Appointment scheduled successfully',
    appointment,
    whatsappSent,
  });
});

// POST /api/admin/appointments/status - Update appointment status (e.g. COMPLETED / CANCELLED)
adminRouter.post('/appointments/status', authenticateAdmin, async (req: AuthRequest, res: Response) => {
  const { consultationId, status } = req.body;
  if (!consultationId || !status) {
    return res.status(400).json({ error: 'consultationId and status are required' });
  }

  const validStatuses = ['PENDING_SCHEDULING', 'SCHEDULED', 'COMPLETED', 'CANCELLED'];
  if (!validStatuses.includes(status)) {
    return res.status(400).json({ error: `Invalid status. Must be one of ${validStatuses.join(', ')}` });
  }

  const appointment = await prisma.appointment.update({
    where: { consultationId },
    data: { status },
  });

  await prisma.consultationRequest.update({
    where: { id: consultationId },
    data: { status },
  });

  return res.json({ message: 'Appointment status updated successfully', appointment });
});
