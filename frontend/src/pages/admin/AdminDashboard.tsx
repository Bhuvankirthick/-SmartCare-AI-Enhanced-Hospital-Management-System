import { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Users, Stethoscope, Calendar, Settings, BedDouble } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import DashboardLayout from '../../components/DashboardLayout';
import api from '../../api/client';

const NAV = [
  { icon: <LayoutDashboard size={17} />, label: 'Dashboard', path: '/admin' },
  { icon: <Users size={17} />, label: 'Patients', path: '/admin/patients' },
  { icon: <Stethoscope size={17} />, label: 'Doctors', path: '/admin/doctors' },
  { icon: <Calendar size={17} />, label: 'Appointments', path: '/admin/appointments' },
  { icon: <BedDouble size={17} />, label: 'Rooms', path: '/admin/rooms' },
  { icon: <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10.5 20.5 7 17l-3.5 3.5a2.12 2.12 0 0 1-3-3l14-14a2.12 2.12 0 0 1 3 3l-3.5 3.5"/><path d="m14.5 10.5 3-3"/><path d="m10.5 14.5 3-3"/></svg>, label: 'Medicines', path: '/admin/medicines' },
  { icon: <svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/><path d="M16 13H8"/><path d="M16 17H8"/><path d="M10 9H8"/></svg>, label: 'Diagnoses', path: '/admin/diagnoses' },
  { icon: <Settings size={17} />, label: 'User Management', path: '/admin/users' },
];

const COLORS = ['#06b6d4', '#6366f1', '#10b981', '#f59e0b', '#ef4444'];

function StatCard({ label, value, sub, color }: { label: string; value: any; sub?: string; color: string }) {
  return (
    <div className="stat-card" style={{ borderTopColor: color, borderTopWidth: 3 }}>
      <div style={{ fontSize: '0.75rem', color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>{label}</div>
      <div style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f1f5f9', marginBottom: '0.25rem' }}>{value}</div>
      {sub && <div style={{ fontSize: '0.75rem', color: '#4b5563' }}>{sub}</div>}
    </div>
  );
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [patients, setPatients] = useState<any[]>([]);
  const [doctors, setDoctors] = useState<any[]>([]);
  const [appointments, setAppointments] = useState<any[]>([]);
  const [rooms, setRooms] = useState<any[]>([]);
  const [medicines, setMedicines] = useState<any[]>([]);
  const [diagnoses, setDiagnoses] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const location = useLocation();
  const navigate = useNavigate();

  const p = location.pathname.split('/').pop();
  const tab = (!p || p === 'admin') ? 'overview' : p;

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/patients/?limit=50').then(r => setPatients(r.data)),
      api.get('/doctors/').then(r => setDoctors(r.data)),
      api.get('/appointments/?limit=100').then(r => setAppointments(r.data)),
      api.get('/rooms/').then(r => setRooms(r.data)),
      api.get('/medicines/').then(r => setMedicines(r.data)),
      api.get('/treatments/').then(r => setDiagnoses(r.data)),
      api.get('/auth/users').then(r => setUsers(r.data)),
      api.get('/analytics/stats').then(r => setStats(r.data)),
    ]).finally(() => setLoading(false));
  }, []);

  const renderContent = () => {
    if (loading) return <div style={{ color: '#4b5563', padding: '2rem', textAlign: 'center' }}>Loading...</div>;

    if (tab === 'overview') return (
      <div className="animate-slide-up">
        <div style={{ marginBottom: '1.5rem' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#f1f5f9' }}>Administrator Dashboard</h1>
          <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>Real-time hospital operations overview</p>
        </div>

        {/* Stat cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '1rem', marginBottom: '1.5rem' }}>
          <StatCard label="Total Patients" value={stats?.total_patients ?? 0} sub="Registered" color="#06b6d4" />
          <StatCard label="Doctors" value={stats?.total_doctors ?? 0} sub="Active staff" color="#6366f1" />
          <StatCard label="Appointments" value={stats?.total_appointments ?? 0} sub="All time" color="#10b981" />
          <StatCard label="Revenue" value={`₹${(stats?.total_revenue ?? 0).toLocaleString('en-IN')}`} sub="Collected" color="#f59e0b" />
          <StatCard label="Pending Bills" value={stats?.pending_bills ?? 0} sub="Unpaid" color="#ef4444" />
          <StatCard label="Available Beds" value={stats?.available_beds ?? 0} sub="Right now" color="#06b6d4" />
          <StatCard label="Low Stock" value={stats?.low_stock_count ?? 0} sub="Medicines" color="#ec4899" />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
          {/* Daily appointments chart */}
          <div className="card">
            <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '1rem' }}>Appointments (Last 7 Days)</div>
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={stats?.daily_appointments ?? []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e2d45" />
                <XAxis dataKey="date" tick={{ fill: '#6b7280', fontSize: 11 }} />
                <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1e2d45', borderRadius: 8, color: '#e2e8f0' }} />
                <Bar dataKey="count" fill="#06b6d4" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Status pie */}
          <div className="card">
            <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '1rem' }}>Appointment Status</div>
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={stats?.status_breakdown ?? []} dataKey="count" nameKey="status" cx="50%" cy="50%" outerRadius={70} label={({ name, value }: any) => `${name}: ${value}`}
                  labelLine={false} fontSize={10}>
                  {(stats?.status_breakdown ?? []).map((_: any, i: number) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Pie>
                <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1e2d45', borderRadius: 8, color: '#e2e8f0' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Revenue chart */}
        <div className="card" style={{ marginBottom: '1rem' }}>
          <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '1rem' }}>Monthly Revenue (₹)</div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={stats?.monthly_revenue ?? []}>
              <defs>
                <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2d45" />
              <XAxis dataKey="month" tick={{ fill: '#6b7280', fontSize: 11 }} />
              <YAxis tick={{ fill: '#6b7280', fontSize: 11 }} />
              <Tooltip contentStyle={{ background: '#111827', border: '1px solid #1e2d45', borderRadius: 8, color: '#e2e8f0' }}
                formatter={(v: any) => [`₹${v.toLocaleString('en-IN')}`, 'Revenue']} />
              <Area type="monotone" dataKey="revenue" stroke="#6366f1" fill="url(#revGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Recent appointments */}
        <div className="card">
          <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '1rem' }}>Recent Appointments</div>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid #1e2d45' }}>
                {['Patient', 'Doctor', 'Date', 'Reason', 'Status'].map(h => (
                  <th key={h} style={{ textAlign: 'left', padding: '0.5rem 0.75rem', fontSize: '0.75rem', color: '#4b5563', fontWeight: 600 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {appointments.slice(0, 8).map((a: any) => (
                <tr key={a.appointment_id} className="table-row">
                  <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.825rem', color: '#e2e8f0' }}>{a.patient_name}</td>
                  <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.825rem', color: '#94a3b8' }}>{a.doctor_name}</td>
                  <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.75rem', color: '#6b7280' }}>
                    {new Date(a.appointment_date).toLocaleDateString('en-IN')}
                  </td>
                  <td style={{ padding: '0.625rem 0.75rem' }}>
                    <span className={`badge-${a.status === 'completed' ? 'success' : a.status === 'cancelled' ? 'danger' : a.status === 'confirmed' ? 'info' : 'warning'}`}
                      style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', borderRadius: 4, display: 'inline-block', fontWeight: 600 }}>
                      {a.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );

    if (tab === 'patients') return (
      <PatientManagement patients={patients} setPatients={setPatients} />
    );

    if (tab === 'doctors') return <DoctorManagement doctors={doctors} setDoctors={setDoctors} />;
    if (tab === 'appointments') return <AppointmentManagement appointments={appointments} />;
    if (tab === 'rooms') return <RoomManagement rooms={rooms} />;
    if (tab === 'medicines') return <MedicineManagement medicines={medicines} />;
    if (tab === 'diagnoses') return <DiagnosisManagement diagnoses={diagnoses} />;
    if (tab === 'users') return <UserManagement users={users} setUsers={setUsers} />;

    return <div style={{ color: '#6b7280', padding: '2rem', textAlign: 'center' }}>Section coming soon</div>;
  };

  const navWithClick = NAV.map(n => ({
    ...n,
    path: n.path,
  }));

  return (
    <DashboardLayout navItems={navWithClick} roleLabel="Administrator" roleColor="#6366f1">
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        {(['overview', 'patients', 'doctors', 'appointments', 'rooms', 'medicines', 'diagnoses', 'users'] as const).map(t => (
          <button key={t} onClick={() => navigate(t === 'overview' ? '/admin' : `/admin/${t}`)}
            style={{ padding: '0.4rem 0.875rem', borderRadius: 6, border: 'none', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600, textTransform: 'capitalize',
              background: tab === t ? 'linear-gradient(135deg, #06b6d4, #6366f1)' : '#111827',
              color: tab === t ? 'white' : '#6b7280', transition: 'all 0.15s' }}>
            {t}
          </button>
        ))}
      </div>
      {renderContent()}
    </DashboardLayout>
  );
}

function PatientManagement({ patients, setPatients }: { patients: any[]; setPatients: any }) {
  const [showForm, setShowForm] = useState(false);
  const [q, setQ] = useState('');
  const [form, setForm] = useState({ name: '', gender: 'Male', blood_group: 'O+', contact: '', email: '', address: '', username: '', password: '' });
  const [saving, setSaving] = useState(false);

  const filtered = patients.filter(p => p.name.toLowerCase().includes(q.toLowerCase()) || p.email?.toLowerCase().includes(q.toLowerCase()));

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await api.post('/patients/', form);
      setPatients([...patients, res.data]);
      setShowForm(false);
      setForm({ name: '', gender: 'Male', blood_group: 'O+', contact: '', email: '', address: '', username: '', password: '' });
    } finally { setSaving(false); }
  };

  return (
    <div className="animate-slide-up">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f1f5f9' }}>Patient Management</h1>
          <p style={{ color: '#6b7280', fontSize: '0.8rem' }}>{patients.length} registered patients</p>
        </div>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>+ Add Patient</button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: '1rem' }}>
          <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '1rem' }}>New Patient</div>
          <form onSubmit={handleAdd} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            {[
              { key: 'name', label: 'Full Name', required: true },
              { key: 'email', label: 'Email' },
              { key: 'contact', label: 'Phone' },
              { key: 'address', label: 'Address' },
            ].map(f => (
              <div key={f.key}>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>{f.label}</label>
                <input className="input-field" value={(form as any)[f.key]} required={f.required}
                  onChange={e => setForm({ ...form, [f.key]: e.target.value })} />
              </div>
            ))}
            <div>
              <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Username *</label>
              <input className="input-field" required value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} />
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Password *</label>
              <input className="input-field" type="password" required value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Gender</label>
              <select className="input-field" value={form.gender} onChange={e => setForm({ ...form, gender: e.target.value })}>
                {['Male', 'Female', 'Other'].map(g => <option key={g}>{g}</option>)}
              </select>
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Blood Type</label>
              <select className="input-field" value={form.blood_group} onChange={e => setForm({ ...form, blood_group: e.target.value })}>
                {['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-'].map(bt => <option key={bt}>{bt}</option>)}
              </select>
            </div>
            <div style={{ gridColumn: '1/-1', display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
              <button type="button" className="btn-ghost" onClick={() => setShowForm(false)}>Cancel</button>
              <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Saving...' : 'Add Patient'}</button>
            </div>
          </form>
        </div>
      )}

      <div className="card">
        <input className="input-field" placeholder="Search patients..." value={q} onChange={e => setQ(e.target.value)}
          style={{ marginBottom: '1rem' }} />
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #1e2d45' }}>
              {['ID', 'Name', 'Gender', 'Blood Type', 'Contact', 'Email'].map(h =>
                <th key={h} style={{ textAlign: 'left', padding: '0.5rem 0.75rem', fontSize: '0.75rem', color: '#4b5563', fontWeight: 600 }}>{h}</th>)}
            </tr>
          </thead>
          <tbody>
            {filtered.slice(0, 30).map((p: any) => (
              <tr key={p.patient_id} className="table-row">
                <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.75rem', color: '#4b5563' }}>#{p.patient_id}</td>
                <td style={{ padding: '0.625rem 0.75rem', fontWeight: 600, color: '#e2e8f0', fontSize: '0.85rem' }}>{p.name}</td>
                <td style={{ padding: '0.625rem 0.75rem', color: '#94a3b8', fontSize: '0.8rem' }}>{p.gender}</td>
                <td style={{ padding: '0.625rem 0.75rem' }}>
                  <span className="badge-info" style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', borderRadius: 4 }}>{p.blood_group}</span>
                </td>
                <td style={{ padding: '0.625rem 0.75rem', color: '#6b7280', fontSize: '0.8rem' }}>{p.contact}</td>
                <td style={{ padding: '0.625rem 0.75rem', color: '#6b7280', fontSize: '0.8rem' }}>{p.email}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function DoctorManagement({ doctors, setDoctors }: { doctors: any[]; setDoctors: any }) {
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', specialization: 'General Medicine', contact: '', email: '', consultation_fee: 500, username: '', password: '' });
  const [saving, setSaving] = useState(false);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const res = await api.post('/doctors/', form);
      setDoctors([...doctors, res.data]);
      setShowForm(false);
      setForm({ name: '', specialization: 'General Medicine', contact: '', email: '', consultation_fee: 500, username: '', password: '' });
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error creating doctor');
    } finally { setSaving(false); }
  };

  return (
    <div className="animate-slide-up">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div>
          <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f1f5f9' }}>Doctor Management</h1>
          <p style={{ color: '#6b7280', fontSize: '0.8rem' }}>{doctors.length} active doctors</p>
        </div>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>+ Add Doctor</button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: '1rem' }}>
          <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '1rem' }}>New Doctor Registration</div>
          <form onSubmit={handleAdd} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            {[
              { key: 'name', label: 'Doctor Name', required: true },
              { key: 'specialization', label: 'Specialization', required: true },
              { key: 'email', label: 'Email' },
              { key: 'contact', label: 'Phone' },
              { key: 'consultation_fee', label: 'Consultation Fee (₹)', type: 'number' },
            ].map(f => (
              <div key={f.key}>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>{f.label}</label>
                <input className="input-field" type={f.type || 'text'} value={(form as any)[f.key]} required={f.required}
                  onChange={e => setForm({ ...form, [f.key]: f.type === 'number' ? parseFloat(e.target.value) : e.target.value })} />
              </div>
            ))}
            <div>
              <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Username *</label>
              <input className="input-field" required value={form.username} onChange={e => setForm({ ...form, username: e.target.value })} />
            </div>
            <div>
              <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Password *</label>
              <input className="input-field" type="password" required value={form.password} onChange={e => setForm({ ...form, password: e.target.value })} />
            </div>
            <div style={{ gridColumn: '1/-1', display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
              <button type="button" className="btn-ghost" onClick={() => setShowForm(false)}>Cancel</button>
              <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Saving...' : 'Add Doctor'}</button>
            </div>
          </form>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1rem' }}>
        {doctors.map((d: any) => (
          <div key={d.doctor_id} className="card glass-hover">
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem' }}>
              <div style={{ width: 44, height: 44, borderRadius: 10, background: 'linear-gradient(135deg,#6366f1,#06b6d4)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontSize: '1.1rem', fontWeight: 700, color: 'white' }}>
                {d.name.charAt(0)}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontWeight: 700, color: '#e2e8f0', fontSize: '0.9rem' }}>{d.name}</div>
                <div style={{ color: '#06b6d4', fontSize: '0.75rem', fontWeight: 600 }}>{d.specialization}</div>
              </div>
              <span className={d.available ? 'badge-success' : 'badge-danger'}
                style={{ fontSize: '0.65rem', padding: '0.2rem 0.5rem', borderRadius: 4, whiteSpace: 'nowrap' }}>
                {d.available ? 'Available' : 'Unavailable'}
              </span>
            </div>
            <div style={{ marginTop: '0.875rem', padding: '0.625rem', background: '#0a0f1e', borderRadius: 8,
              fontSize: '0.75rem', color: '#6b7280', display: 'flex', justifyContent: 'space-between' }}>
              <span>Fee: <span style={{ color: '#10b981', fontWeight: 600 }}>₹{d.consultation_fee}</span></span>
              <span>ID: #{d.doctor_id}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function UserManagement({ users, setUsers }: { users: any[]; setUsers: any }) {
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ username: '', email: '', password: '', role: 'receptionist' });
  const [saving, setSaving] = useState(false);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault(); setSaving(true);
    try {
      const res = await api.post('/auth/users', form);
      setUsers([...users, res.data]);
      setShowForm(false);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error creating user');
    } finally { setSaving(false); }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this user?')) return;
    await api.delete(`/auth/users/${id}`);
    setUsers(users.filter(u => u.user_id !== id));
  };

  const ROLE_COLORS: Record<string, string> = { admin: '#6366f1', doctor: '#06b6d4', patient: '#10b981', receptionist: '#f59e0b', pharmacist: '#ec4899' };

  return (
    <div className="animate-slide-up">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f1f5f9' }}>User Management</h1>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>+ Add User</button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: '1rem' }}>
          <form onSubmit={handleAdd} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
            {[{ key: 'username', label: 'Username' }, { key: 'email', label: 'Email' }, { key: 'password', label: 'Password', type: 'password' }].map(f => (
              <div key={f.key}>
                <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>{f.label}</label>
                <input className="input-field" type={f.type || 'text'} required
                  value={(form as any)[f.key]} onChange={e => setForm({ ...form, [f.key]: e.target.value })} />
              </div>
            ))}
            <div>
              <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Role</label>
              <select className="input-field" value={form.role} onChange={e => setForm({ ...form, role: e.target.value })}>
                {['admin', 'doctor', 'patient', 'receptionist', 'pharmacist'].map(r => <option key={r}>{r}</option>)}
              </select>
            </div>
            <div style={{ gridColumn: '1/-1', display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
              <button type="button" className="btn-ghost" onClick={() => setShowForm(false)}>Cancel</button>
              <button type="submit" className="btn-primary" disabled={saving}>{saving ? 'Creating...' : 'Create User'}</button>
            </div>
          </form>
        </div>
      )}

      <div className="card">
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #1e2d45' }}>
              {['ID', 'Username', 'Email', 'Role', 'Status', 'Actions'].map(h =>
                <th key={h} style={{ textAlign: 'left', padding: '0.5rem 0.75rem', fontSize: '0.75rem', color: '#4b5563', fontWeight: 600 }}>{h}</th>)}
            </tr>
          </thead>
          <tbody>
            {users.map((u: any) => (
              <tr key={u.user_id} className="table-row">
                <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.75rem', color: '#4b5563' }}>#{u.user_id}</td>
                <td style={{ padding: '0.625rem 0.75rem', fontWeight: 600, color: '#e2e8f0', fontSize: '0.85rem' }}>{u.username}</td>
                <td style={{ padding: '0.625rem 0.75rem', color: '#6b7280', fontSize: '0.8rem' }}>{u.email}</td>
                <td style={{ padding: '0.625rem 0.75rem' }}>
                  <span style={{ fontSize: '0.7rem', padding: '0.2rem 0.6rem', borderRadius: 4, fontWeight: 600,
                    background: ROLE_COLORS[u.role] + '22', color: ROLE_COLORS[u.role],
                    border: `1px solid ${ROLE_COLORS[u.role]}44` }}>
                    {u.role}
                  </span>
                </td>
                <td style={{ padding: '0.625rem 0.75rem' }}>
                  <span className={u.is_active ? 'badge-success' : 'badge-danger'}
                    style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', borderRadius: 4 }}>
                    {u.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td style={{ padding: '0.625rem 0.75rem' }}>
                  <button onClick={() => handleDelete(u.user_id)}
                    style={{ fontSize: '0.75rem', color: '#ef4444', background: 'none', border: 'none', cursor: 'pointer', padding: '0.2rem 0.5rem' }}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function AppointmentManagement({ appointments }: { appointments: any[] }) {
  return (
    <div className="animate-slide-up">
      <div style={{ marginBottom: '1rem' }}>
        <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f1f5f9' }}>Appointment Management</h1>
        <p style={{ color: '#6b7280', fontSize: '0.8rem' }}>{appointments.length} total specific appointments</p>
      </div>
      <div className="card">
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #1e2d45' }}>
              {['ID', 'Patient', 'Doctor', 'Date', 'Time', 'Status'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '0.5rem 0.75rem', fontSize: '0.75rem', color: '#4b5563', fontWeight: 600 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {appointments.map((a: any) => (
              <tr key={a.appointment_id} className="table-row">
                <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.75rem', color: '#4b5563' }}>#{a.appointment_id}</td>
                <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.825rem', color: '#e2e8f0', fontWeight: 600 }}>{a.patient_name}</td>
                <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.825rem', color: '#94a3b8' }}>{a.doctor_name}</td>
                <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.75rem', color: '#6b7280' }}>
                  {new Date(a.appointment_date).toLocaleDateString('en-IN')}
                </td>
                <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.75rem', color: '#6b7280' }}>{a.appointment_time}</td>
                <td style={{ padding: '0.625rem 0.75rem' }}>
                  <span className={`badge-${a.status === 'completed' || a.status === 'Completed' ? 'success' : a.status === 'cancelled' ? 'danger' : a.status === 'confirmed' ? 'info' : 'warning'}`}
                    style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', borderRadius: 4, display: 'inline-block', fontWeight: 600 }}>
                    {a.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function RoomManagement({ rooms }: { rooms: any[] }) {
  return (
    <div className="animate-slide-up">
      <div style={{ marginBottom: '1rem' }}>
        <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f1f5f9' }}>Room Management</h1>
        <p style={{ color: '#6b7280', fontSize: '0.8rem' }}>{rooms.length} hospital rooms monitored</p>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '1rem' }}>
        {rooms.map((r: any) => (
          <div key={r.room_id} className="card glass-hover" style={{ borderLeft: `3px solid ${r.availability_status === 'Available' ? '#10b981' : '#ef4444'}` }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <div style={{ fontWeight: 800, color: '#e2e8f0', fontSize: '1rem' }}>Room {r.room_id} &mdash; {r.room_type}</div>
              <span className={r.availability_status === 'Available' ? 'badge-success' : 'badge-danger'}
                    style={{ fontSize: '0.65rem', padding: '0.2rem 0.5rem', borderRadius: 4, whiteSpace: 'nowrap' }}>
                {r.availability_status}
              </span>
            </div>
            <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginBottom: '0.5rem' }}>Capacity: {r.capacity} Bed{r.capacity > 1 ? 's' : ''}</div>
            <div style={{ fontSize: '1.2rem', fontWeight: 800, color: '#06b6d4' }}>₹{r.cost_per_day}<span style={{ fontSize: '0.75rem', color: '#6b7280', fontWeight: 400 }}> / day</span></div>
          </div>
        ))}
      </div>
    </div>
  );
}

function MedicineManagement({ medicines }: { medicines: any[] }) {
  return (
    <div className="animate-slide-up">
      <div style={{ marginBottom: '1rem' }}>
        <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f1f5f9' }}>Drug & Medicine Inventory</h1>
        <p style={{ color: '#6b7280', fontSize: '0.8rem' }}>{medicines.length} unique items tracked</p>
      </div>
      <div className="card">
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #1e2d45' }}>
              {['ID', 'Medicine Name', 'Stock', 'Unit Price', 'Expiry', 'Status'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '0.5rem 0.75rem', fontSize: '0.75rem', color: '#4b5563', fontWeight: 600 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {medicines.map((m: any) => (
              <tr key={m.medicine_id} className="table-row">
                <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.75rem', color: '#4b5563' }}>#{m.medicine_id}</td>
                <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.825rem', color: '#e2e8f0', fontWeight: 600 }}>{m.name}</td>
                <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.825rem', color: '#fff' }}>{m.stock_quantity} units</td>
                <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.825rem', color: '#10b981', fontWeight: 600 }}>₹{m.price}</td>
                <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.75rem', color: '#6b7280' }}>
                  {new Date(m.expiry_date).toLocaleDateString('en-IN')}
                </td>
                <td style={{ padding: '0.625rem 0.75rem' }}>
                  <span className={m.stock_quantity > 50 ? 'badge-success' : m.stock_quantity > 0 ? 'badge-warning' : 'badge-danger'}
                    style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', borderRadius: 4, display: 'inline-block', fontWeight: 600 }}>
                    {m.stock_quantity > 50 ? 'In Stock' : m.stock_quantity > 0 ? 'Low Stock' : 'Out of Stock'}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function DiagnosisManagement({ diagnoses }: { diagnoses: any[] }) {
  return (
    <div className="animate-slide-up">
      <div style={{ marginBottom: '1rem' }}>
        <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f1f5f9' }}>Diagnoses & Treatments Overview</h1>
        <p style={{ color: '#6b7280', fontSize: '0.8rem' }}>{diagnoses.length} treatment records mapped</p>
      </div>
      <div className="card">
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid #1e2d45' }}>
              {['Record ID', 'Doctor', 'Patient ID', 'Diagnosis Notes', 'Date'].map(h => (
                <th key={h} style={{ textAlign: 'left', padding: '0.5rem 0.75rem', fontSize: '0.75rem', color: '#4b5563', fontWeight: 600 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {diagnoses.map((d: any) => (
               <tr key={d.diagnosis_id} className="table-row">
                 <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.75rem', color: '#4b5563' }}>#{d.diagnosis_id}</td>
                 <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.825rem', color: '#e2e8f0', fontWeight: 600 }}>{d.doctor_name || 'N/A'}</td>
                 <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.825rem', color: '#94a3b8' }}>Patient #{d.patient_id}</td>
                 <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.75rem', color: '#6b7280' }}>{d.diagnosis_details}</td>
                 <td style={{ padding: '0.625rem 0.75rem', fontSize: '0.75rem', color: '#6b7280' }}>
                   {new Date(d.diagnosis_date).toLocaleDateString('en-IN')}
                 </td>
               </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
