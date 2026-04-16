import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Calendar, FileText, CreditCard, Pill } from 'lucide-react';
import DashboardLayout from '../../components/DashboardLayout';
import api from '../../api/client';
import { useAuthStore } from '../../store/authStore';

const NAV = [
  { icon: <Calendar size={17} />, label: 'Book Appointment', path: '/patient' },
  { icon: <FileText size={17} />, label: 'My History', path: '/patient/history' },
  { icon: <CreditCard size={17} />, label: 'My Bills', path: '/patient/bills' },
  { icon: <Pill size={17} />, label: 'Prescriptions', path: '/patient/prescriptions' },
];

export default function PatientDashboard() {
  const { user } = useAuthStore();
  const [tab, setTab] = useState<'book' | 'appointments' | 'bills' | 'prescriptions' | 'history'>('book');
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const p = location.pathname.split('/').pop();
    if (!p || p === 'patient') setTab('book');
    else if (p === 'history') setTab('prescriptions');
    else setTab(p as any);
  }, [location.pathname]);
  const [doctors, setDoctors] = useState<any[]>([]);
  const [appointments, setAppointments] = useState<any[]>([]);
  const [bills, setBills] = useState<any[]>([]);
  const [treatments, setTreatments] = useState<any[]>([]);
  const [booking, setBooking] = useState({ doctor_id: '', appointment_date: '', appointment_time: '' });
  const [bookMsg, setBookMsg] = useState('');
  const [bookErr, setBookErr] = useState('');
  const [saving, setSaving] = useState(false);
  const patientId = user?.linked_id;

  useEffect(() => {
    api.get('/doctors/').then(r => setDoctors(r.data));
    api.get('/appointments/').then(r => setAppointments(r.data));
    if (patientId) {
      api.get('/bills/').then(r => setBills(r.data));
      api.get('/treatments/').then(r => setTreatments(r.data));
    }
  }, [patientId]);

  const handleBook = async (e: React.FormEvent) => {
    e.preventDefault(); setSaving(true); setBookMsg(''); setBookErr('');
    try {
      const dateObj = new Date(booking.appointment_date);
      await api.post('/appointments/', {
        patient_id: patientId,
        doctor_id: parseInt(booking.doctor_id),
        appointment_date: dateObj.toISOString().split('T')[0],
        appointment_time: booking.appointment_time,
      });
      setBookMsg('Appointment booked successfully!');
      setBooking({ doctor_id: '', appointment_date: '', appointment_time: '' });
      const res = await api.get('/appointments/');
      setAppointments(res.data);
    } catch (err: any) {
      setBookErr(err.response?.data?.detail || 'Booking failed. Doctor may be unavailable at this time.');
    } finally { setSaving(false); }
  };

  const upcomingAppts = appointments.filter(a => new Date(a.appointment_date) > new Date());
  const totalBilled = bills.reduce((s, b) => s + b.total_amount, 0);
  const totalPaid = bills.filter(b => b.payment_status === 'Paid').reduce((s, b) => s + b.total_amount, 0);

  return (
    <DashboardLayout navItems={NAV} roleLabel="Patient Portal" roleColor="#10b981">
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        {([
          { id: 'book', label: 'Book Appointment' },
          { id: 'appointments', label: 'My Appointments' },
          { id: 'bills', label: 'My Bills' },
          { id: 'prescriptions', label: 'Prescriptions & History' },
        ] as const).map(t => (
          <button key={t.id} onClick={() => navigate(t.id === 'book' ? '/patient' : `/patient/${t.id}`)}
            style={{ padding: '0.4rem 0.875rem', borderRadius: 6, border: 'none', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600,
              background: tab === t.id ? 'linear-gradient(135deg, #10b981, #06b6d4)' : '#111827',
              color: tab === t.id ? 'white' : '#6b7280', transition: 'all 0.15s' }}>
            {t.label}
          </button>
        ))}
      </div>

      <div className="animate-slide-up">
        {/* Summary stats */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
          <div className="stat-card" style={{ borderTopWidth: 3, borderTopColor: '#06b6d4' }}>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>Upcoming Appointments</div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: '#f1f5f9' }}>{upcomingAppts.length}</div>
          </div>
          <div className="stat-card" style={{ borderTopWidth: 3, borderTopColor: '#f59e0b' }}>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>Total Billed</div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: '#f1f5f9' }}>₹{totalBilled.toLocaleString('en-IN')}</div>
          </div>
          <div className="stat-card" style={{ borderTopWidth: 3, borderTopColor: '#10b981' }}>
            <div style={{ fontSize: '0.75rem', color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>Prescription Records</div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: '#f1f5f9' }}>{treatments.length}</div>
          </div>
        </div>

        {tab === 'book' && (
          <div className="card" style={{ maxWidth: 600 }}>
            <div style={{ fontSize: '1rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '1.25rem' }}>Book New Appointment</div>
            {bookMsg && (
              <div style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: 8,
                padding: '0.75rem', marginBottom: '1rem', color: '#10b981', fontSize: '0.85rem' }}>
                {bookMsg}
              </div>
            )}
            {bookErr && (
              <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 8,
                padding: '0.75rem', marginBottom: '1rem', color: '#f87171', fontSize: '0.85rem' }}>
                {bookErr}
              </div>
            )}
            <form onSubmit={handleBook} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Select Doctor *</label>
                <select className="input-field" required value={booking.doctor_id} onChange={e => setBooking({ ...booking, doctor_id: e.target.value })}>
                  <option value="">-- Choose a Doctor --</option>
                  {doctors.filter(d => d.available).map(d => (
                    <option key={d.doctor_id} value={d.doctor_id}>{d.name} · {d.specialization} (₹{d.consultation_fee})</option>
                  ))}
                </select>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Date *</label>
                  <input className="input-field" type="date" required value={booking.appointment_date}
                    onChange={e => setBooking({ ...booking, appointment_date: e.target.value })} />
                </div>
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Time *</label>
                  <input className="input-field" type="time" required value={booking.appointment_time}
                    onChange={e => setBooking({ ...booking, appointment_time: e.target.value })} />
                </div>
              </div>
              <button type="submit" className="btn-primary" disabled={saving || !patientId}
                style={{ alignSelf: 'flex-start', padding: '0.625rem 1.5rem' }}>
                {saving ? 'Booking...' : 'Confirm Appointment'}
              </button>
              {!patientId && <div style={{ fontSize: '0.75rem', color: '#f59e0b' }}>Note: Your patient profile is not linked. Contact reception.</div>}
            </form>
          </div>
        )}

        {tab === 'appointments' && (
          <div className="card">
            <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '1rem' }}>My Appointments</div>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #1e2d45' }}>
                  {['Doctor', 'Date', 'Time', 'Status'].map(h =>
                    <th key={h} style={{ textAlign: 'left', padding: '0.5rem 0.75rem', fontSize: '0.75rem', color: '#4b5563', fontWeight: 600 }}>{h}</th>)}
                </tr>
              </thead>
              <tbody>
                {appointments.map((a: any) => (
                  <tr key={a.appointment_id} className="table-row">
                    <td style={{ padding: '0.625rem 0.75rem', fontWeight: 600, color: '#e2e8f0', fontSize: '0.85rem' }}>{a.doctor_name}</td>
                    <td style={{ padding: '0.625rem 0.75rem', color: '#6b7280', fontSize: '0.8rem' }}>
                      {new Date(a.appointment_date).toLocaleDateString('en-IN', { dateStyle: 'medium' })}
                    </td>
                    <td style={{ padding: '0.625rem 0.75rem', color: '#6b7280', fontSize: '0.8rem' }}>{a.appointment_time}</td>
                    <td style={{ padding: '0.625rem 0.75rem' }}>
                      <span className={`badge-${a.status === 'completed' ? 'success' : a.status === 'cancelled' ? 'danger' : 'info'}`}
                        style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', borderRadius: 4, display: 'inline-block', fontWeight: 600 }}>
                        {a.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {tab === 'bills' && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
              <div className="card" style={{ borderLeft: '3px solid #f59e0b' }}>
                <div style={{ fontSize: '0.75rem', color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>Total Outstanding</div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f59e0b' }}>₹{(totalBilled - totalPaid).toLocaleString('en-IN')}</div>
              </div>
              <div className="card" style={{ borderLeft: '3px solid #10b981' }}>
                <div style={{ fontSize: '0.75rem', color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>Total Paid</div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#10b981' }}>₹{totalPaid.toLocaleString('en-IN')}</div>
              </div>
            </div>
            <div className="card">
              <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '1rem' }}>Billing History</div>
              {bills.length === 0 ? (
                <div style={{ color: '#4b5563', textAlign: 'center', padding: '1.5rem' }}>No bills found.</div>
              ) : bills.map((b: any) => (
                <div key={b.bill_id} style={{ padding: '1rem', borderBottom: '1px solid #1a2235', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ fontWeight: 600, color: '#e2e8f0', marginBottom: '0.25rem' }}>Bill #{b.bill_id}</div>
                    <div style={{ fontSize: '0.75rem', color: '#4b5563' }}>{new Date(b.bill_date).toLocaleDateString('en-IN', { dateStyle: 'long' })}</div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280', marginTop: '0.25rem' }}>
                      Status: {b.payment_status}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.1rem', fontWeight: 800, color: '#e2e8f0' }}>₹{b.total_amount.toLocaleString('en-IN')}</div>
                    <span className={b.payment_status === 'Paid' ? 'badge-success' : 'badge-warning'}
                      style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', borderRadius: 4, display: 'inline-block', fontWeight: 600, marginTop: '0.25rem' }}>
                      {b.payment_status?.toUpperCase()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {tab === 'prescriptions' && (
          <div>
            <h1 style={{ fontSize: '1.125rem', fontWeight: 800, color: '#f1f5f9', marginBottom: '1rem' }}>My Prescriptions & Treatment Records</h1>
            {treatments.length === 0 ? (
              <div style={{ color: '#4b5563', textAlign: 'center', padding: '2rem', background: '#111827', borderRadius: 12, border: '1px solid #1e2d45' }}>
                No prescription records found.
              </div>
            ) : treatments.map((t: any) => (
                  <div key={t.diagnosis_id} className="card" style={{ marginBottom: '0.75rem', borderLeft: '3px solid #6366f1' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                      <div style={{ fontSize: '0.75rem', color: '#4b5563' }}>
                        {new Date(t.diagnosis_date).toLocaleDateString('en-IN', { dateStyle: 'medium' })} · Dr. {t.doctor_name}
                      </div>
                    </div>
                    {t.diagnosis_details && <p style={{ color: '#94a3b8', fontSize: '0.8rem', marginBottom: '0.75rem', lineHeight: 1.6 }}>{t.diagnosis_details}</p>}
                  </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
