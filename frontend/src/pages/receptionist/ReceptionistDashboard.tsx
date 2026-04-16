import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { CheckCircle, Calendar, Search, BedDouble } from 'lucide-react';
import DashboardLayout from '../../components/DashboardLayout';
import api from '../../api/client';

const NAV = [
  { icon: <CheckCircle size={17} />, label: 'Check-In', path: '/receptionist' },
  { icon: <Calendar size={17} />, label: 'Schedule', path: '/receptionist/schedule' },
  { icon: <BedDouble size={17} />, label: 'Rooms', path: '/receptionist/rooms' },
  { icon: <Search size={17} />, label: 'Find Patient', path: '/receptionist/search' },
];

export default function ReceptionistDashboard() {
  const [tab, setTab] = useState<'checkin' | 'schedule' | 'rooms' | 'search'>('checkin');
  const location = useLocation();
  const navigate = useNavigate();

  useEffect(() => {
    const p = location.pathname.split('/').pop();
    if (!p || p === 'receptionist') setTab('checkin');
    else setTab(p as any);
  }, [location.pathname]);
  const [patients, setPatients] = useState<any[]>([]);
  const [doctors, setDoctors] = useState<any[]>([]);
  const [appointments, setAppointments] = useState<any[]>([]);
  const [rooms, setRooms] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [booking, setBooking] = useState({ patient_id: '', doctor_id: '', appointment_date: '', appointment_time: '' });
  const [bookMsg, setBookMsg] = useState('');
  const [bookErr, setBookErr] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    Promise.all([
      api.get('/patients/?limit=100').then(r => setPatients(r.data)),
      api.get('/doctors/').then(r => setDoctors(r.data)),
      api.get('/appointments/?limit=50').then(r => setAppointments(r.data)),
      api.get('/rooms/').then(r => setRooms(r.data)),
    ]);
  }, []);

  const today = new Date().toDateString();
  const todayAppts = appointments.filter(a => new Date(a.appointment_date).toDateString() === today);
  const confirmedToday = todayAppts.filter(a => a.status === 'confirmed' || a.status === 'scheduled');

  const handleBook = async (e: React.FormEvent) => {
    e.preventDefault(); setSaving(true); setBookMsg(''); setBookErr('');
    try {
      const dateObj = new Date(booking.appointment_date);
      await api.post('/appointments/', {
        patient_id: parseInt(booking.patient_id),
        doctor_id: parseInt(booking.doctor_id),
        appointment_date: dateObj.toISOString().split('T')[0],
        appointment_time: booking.appointment_time,
      });
      setBookMsg('Appointment scheduled successfully!');
      setBooking({ patient_id: '', doctor_id: '', appointment_date: '', appointment_time: '' });
      const res = await api.get('/appointments/?limit=50');
      setAppointments(res.data);
    } catch (err: any) {
      setBookErr(err.response?.data?.detail || 'Scheduling failed. Check for conflicts.');
    } finally { setSaving(false); }
  };

  const handleStatusUpdate = async (id: number, status: string) => {
    await api.put(`/appointments/${id}`, { status });
    const res = await api.get('/appointments/?limit=50');
    setAppointments(res.data);
  };

  const filteredPatients = patients.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) || p.email?.includes(search) || p.contact?.includes(search)
  );

  const availableRooms = rooms.filter(r => r.availability_status?.toLowerCase() === 'available');
  const occupiedRooms = rooms.filter(r => r.availability_status?.toLowerCase() === 'occupied');

  return (
    <DashboardLayout navItems={NAV} roleLabel="Receptionist" roleColor="#f59e0b">
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
        {(['checkin', 'schedule', 'rooms', 'search'] as const).map(t => (
          <button key={t} onClick={() => navigate(t === 'checkin' ? '/receptionist' : `/receptionist/${t}`)}
            style={{ padding: '0.4rem 0.875rem', borderRadius: 6, border: 'none', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600, textTransform: 'capitalize',
              background: tab === t ? 'linear-gradient(135deg, #f59e0b, #ef4444)' : '#111827',
              color: tab === t ? 'white' : '#6b7280', transition: 'all 0.15s' }}>
            {t === 'checkin' ? 'Check-In & Today' : t === 'schedule' ? 'Schedule Appointment' : t === 'rooms' ? 'Room Management' : 'Find Patient'}
          </button>
        ))}
      </div>

      <div className="animate-slide-up">
        {tab === 'checkin' && (
          <>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
              {[
                { label: "Today's Appointments", value: todayAppts.length, color: '#06b6d4' },
                { label: 'Pending Check-In', value: confirmedToday.length, color: '#f59e0b' },
                { label: 'Total Patients', value: patients.length, color: '#10b981' },
                { label: 'Available Rooms', value: availableRooms.length, color: '#6366f1' },
              ].map(s => (
                <div key={s.label} className="stat-card" style={{ borderTopWidth: 3, borderTopColor: s.color }}>
                  <div style={{ fontSize: '0.72rem', color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>{s.label}</div>
                  <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f1f5f9' }}>{s.value}</div>
                </div>
              ))}
            </div>

            {/* Patient search */}
            <div className="card" style={{ marginBottom: '1rem' }}>
              <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.75rem' }}>Quick Patient Lookup</div>
              <input className="input-field" placeholder="Search by name, email, or phone..." value={search}
                onChange={e => setSearch(e.target.value)} style={{ marginBottom: '0.75rem' }} />
              {search && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', maxHeight: 200, overflowY: 'auto' }}>
                  {filteredPatients.slice(0, 10).map((p: any) => (
                    <div key={p.patient_id} style={{ padding: '0.5rem 0.75rem', background: '#0a0f1e', borderRadius: 6,
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div>
                        <div style={{ fontWeight: 600, color: '#e2e8f0', fontSize: '0.85rem' }}>{p.name}</div>
                        <div style={{ fontSize: '0.72rem', color: '#4b5563' }}>{p.contact} · {p.blood_group}</div>
                      </div>
                      <button onClick={() => setBooking({ ...booking, patient_id: String(p.patient_id) })}
                        style={{ fontSize: '0.72rem', color: '#f59e0b', background: 'none', border: '1px solid rgba(245,158,11,0.3)',
                          borderRadius: 4, padding: '0.2rem 0.5rem', cursor: 'pointer' }}>
                        Select
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Today's appointments for check-in */}
            <div className="card">
              <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '1rem' }}>Today's Schedule</div>
              {todayAppts.length === 0 ? (
                <div style={{ color: '#4b5563', textAlign: 'center', padding: '1.5rem' }}>No appointments today.</div>
              ) : (
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #1e2d45' }}>
                      {['Time', 'Patient', 'Doctor', 'Reason', 'Status', 'Action'].map(h =>
                        <th key={h} style={{ textAlign: 'left', padding: '0.5rem 0.75rem', fontSize: '0.75rem', color: '#4b5563', fontWeight: 600 }}>{h}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {todayAppts.map((a: any) => (
                      <tr key={a.appointment_id} className="table-row">
                        <td style={{ padding: '0.625rem 0.75rem', color: '#06b6d4', fontWeight: 600, fontSize: '0.8rem' }}>
                          {a.appointment_time}
                        </td>
                        <td style={{ padding: '0.625rem 0.75rem', fontWeight: 600, color: '#e2e8f0', fontSize: '0.85rem' }}>{a.patient_name}</td>
                        <td style={{ padding: '0.625rem 0.75rem', color: '#94a3b8', fontSize: '0.8rem' }}>{a.doctor_name}</td>
                        <td style={{ padding: '0.625rem 0.75rem' }}>
                          <span className={`badge-${a.status === 'completed' ? 'success' : a.status === 'cancelled' ? 'danger' : 'info'}`}
                            style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', borderRadius: 4, display: 'inline-block' }}>
                            {a.status}
                          </span>
                        </td>
                        <td style={{ padding: '0.625rem 0.75rem', display: 'flex', gap: '0.4rem' }}>
                          <button onClick={() => handleStatusUpdate(a.appointment_id, 'confirmed')}
                            style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', borderRadius: 4, border: 'none', cursor: 'pointer',
                              background: 'rgba(6,182,212,0.1)', color: '#06b6d4' }}>Check-In</button>
                          <button onClick={() => handleStatusUpdate(a.appointment_id, 'completed')}
                            style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', borderRadius: 4, border: 'none', cursor: 'pointer',
                              background: 'rgba(16,185,129,0.1)', color: '#10b981' }}>Complete</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </>
        )}

        {tab === 'schedule' && (
          <div className="card" style={{ maxWidth: 600 }}>
            <div style={{ fontSize: '1rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '1.25rem' }}>Schedule New Appointment</div>
            {bookMsg && <div style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: 8, padding: '0.75rem', marginBottom: '1rem', color: '#10b981', fontSize: '0.85rem' }}>{bookMsg}</div>}
            {bookErr && <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 8, padding: '0.75rem', marginBottom: '1rem', color: '#f87171', fontSize: '0.85rem' }}>{bookErr}</div>}
            <form onSubmit={handleBook} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Select Patient *</label>
                <select className="input-field" required value={booking.patient_id} onChange={e => setBooking({ ...booking, patient_id: e.target.value })}>
                  <option value="">-- Select Patient --</option>
                  {patients.map(p => <option key={p.patient_id} value={p.patient_id}>{p.name} (#{p.patient_id})</option>)}
                </select>
              </div>
              <div>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Select Doctor *</label>
                <select className="input-field" required value={booking.doctor_id} onChange={e => setBooking({ ...booking, doctor_id: e.target.value })}>
                  <option value="">-- Select Doctor --</option>
                  {doctors.filter(d => d.available).map(d => <option key={d.doctor_id} value={d.doctor_id}>{d.name} · {d.specialization}</option>)}
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
              <button type="submit" className="btn-primary" disabled={saving} style={{ alignSelf: 'flex-start', padding: '0.625rem 1.5rem' }}>
                {saving ? 'Scheduling...' : 'Schedule Appointment'}
              </button>
            </form>
          </div>
        )}

        {tab === 'rooms' && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
              <div className="stat-card" style={{ borderTopWidth: 3, borderTopColor: '#10b981' }}>
                <div style={{ fontSize: '0.72rem', color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>Available Rooms</div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: '#10b981' }}>{availableRooms.length}</div>
              </div>
              <div className="stat-card" style={{ borderTopWidth: 3, borderTopColor: '#ef4444' }}>
                <div style={{ fontSize: '0.72rem', color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>Occupied Rooms</div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: '#ef4444' }}>{occupiedRooms.length}</div>
              </div>
              <div className="stat-card" style={{ borderTopWidth: 3, borderTopColor: '#6366f1' }}>
                <div style={{ fontSize: '0.72rem', color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>Total Rooms</div>
                <div style={{ fontSize: '2rem', fontWeight: 800, color: '#f1f5f9' }}>{rooms.length}</div>
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: '1rem' }}>
              {rooms.map(r => (
                <div key={r.room_id} className="card glass-hover">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                    <div>
                      <div style={{ fontWeight: 800, color: '#e2e8f0', fontSize: '1rem' }}>Room #{r.room_id}</div>
                      <div style={{ color: '#6b7280', fontSize: '0.75rem', textTransform: 'capitalize' }}>{r.room_type}</div>
                    </div>
                    <span className={r.availability_status?.toLowerCase() === 'available' ? 'badge-success' : 'badge-danger'}
                      style={{ fontSize: '0.65rem', padding: '0.2rem 0.5rem', borderRadius: 4, fontWeight: 600 }}>
                      {r.availability_status}
                    </span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: '#4b5563', background: '#0a0f1e', borderRadius: 6, padding: '0.5rem 0.625rem' }}>
                    <span>Capacity: <b style={{ color: '#e2e8f0' }}>{r.capacity}</b></span>
                    <span style={{ color: '#10b981', fontWeight: 600 }}>₹{r.cost_per_day}/day</span>
                  </div>
                  <div style={{ marginTop: '0.625rem', height: 4, background: '#1e2d45', borderRadius: 2 }}>
                    <div style={{ height: '100%', borderRadius: 2, width: `${(r.current_occupancy / r.capacity) * 100}%`,
                      background: r.current_occupancy >= r.capacity ? '#ef4444' : '#10b981', transition: 'width 0.3s' }} />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
