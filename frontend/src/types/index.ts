export interface Patient {
  patient_id: number;
  name: string;
  gender: string;
  blood_group: string;
  contact: string;
  email: string;
  address?: string;
}

export interface Doctor {
  doctor_id: number;
  name: string;
  specialization: string;
  department: string;
  available: boolean;
  consultation_fee: number;
  qualification: string;
}

export interface Appointment {
  appointment_id: number;
  patient_name: string;
  doctor_name: string;
  appointment_date: string;
  appointment_time: string;
  status: string;
}

export interface Room {
  room_id: number;
  room_type: string;
  availability_status: string;
  capacity: number;
  cost_per_day: number;
}

export interface Medicine {
  medicine_id: number;
  name: string;
  stock_quantity: number;
  price: number;
  expiry_date: string;
}

export interface Diagnosis {
  diagnosis_id: number;
  doctor_name?: string;
  patient_id: number;
  diagnosis_details: string;
  diagnosis_date: string;
}

export interface User {
  user_id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
}

export interface Stat {
  total_patients: number;
  total_doctors: number;
  total_appointments: number;
  total_revenue: number;
  pending_bills: number;
  available_beds: number;
  low_stock_count: number;
  daily_appointments: { date: string; count: number }[];
  status_breakdown: { status: string; count: number }[];
  monthly_revenue: { month: string; revenue: number }[];
}

export interface Prediction {
  model: string;
  predictions: {
    day: string;
    date: string;
    predicted_occupancy: number;
    confidence_low: number;
    confidence_high: number;
  }[];
}
