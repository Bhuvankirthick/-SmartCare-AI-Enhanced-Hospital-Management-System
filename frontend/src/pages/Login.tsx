import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Shield, Lock, User } from 'lucide-react';
import api from '../api/client';
import { useAuthStore } from '../store/authStore';

const ROLE_LABELS: Record<string, { label: string; color: string }> = {
  admin: { label: 'Administrator', color: '#6366f1' },
  doctor: { label: 'Doctor', color: '#06b6d4' },
  patient: { label: 'Patient', color: '#10b981' },
  receptionist: { label: 'Receptionist', color: '#f59e0b' },
  pharmacist: { label: 'Pharmacist', color: '#ec4899' },
};

const QUICK_LOGINS = [
  { username: 'admin', password: 'admin123', role: 'admin' },
  { username: 'dr.rajesh', password: 'doctor123', role: 'doctor' },
  { username: 'ananya.patient', password: 'patient123', role: 'patient' },
  { username: 'receptionist', password: 'recept123', role: 'receptionist' },
  { username: 'pharmacist', password: 'pharma123', role: 'pharmacist' },
];

export default function Login() {
  const [username, setUsername] = useState('admin');
  const [password, setPassword] = useState('admin123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { setUser } = useAuthStore();
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const res = await api.post('/auth/login', { username, password });
      setUser({ ...res.data, access_token: res.data.access_token });
      navigate(`/${res.data.role}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed. Check credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
      background: 'linear-gradient(135deg, #0a0f1e 0%, #0d1426 50%, #0a1628 100%)', padding: '1rem' }}>

      {/* Background orbs */}
      <div style={{ position: 'fixed', top: '20%', left: '10%', width: 400, height: 400, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(6,182,212,0.08) 0%, transparent 70%)', pointerEvents: 'none' }} />
      <div style={{ position: 'fixed', bottom: '20%', right: '10%', width: 500, height: 500, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(99,102,241,0.07) 0%, transparent 70%)', pointerEvents: 'none' }} />

      <div style={{ width: '100%', maxWidth: 900, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}
           className="animate-fade-in">

        {/* Left panel */}
        <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', padding: '2rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '2rem' }}>
            <div style={{ width: 48, height: 48, borderRadius: 12, background: 'linear-gradient(135deg,#06b6d4,#6366f1)',
              display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Activity size={28} color="white" />
            </div>
            <div>
              <div style={{ fontSize: '1.5rem', fontWeight: 800, color: '#e2e8f0' }}>MediCore HMS</div>
              <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>Hospital Management System</div>
            </div>
          </div>

          <h1 style={{ fontSize: '2rem', fontWeight: 700, color: '#f1f5f9', lineHeight: 1.2, marginBottom: '1rem' }}>
            Intelligent Healthcare<br />
            <span className="gradient-text">Management Platform</span>
          </h1>
          <p style={{ color: '#94a3b8', lineHeight: 1.7, marginBottom: '2rem', fontSize: '0.9rem' }}>
            A complete end-to-end solution for hospitals — from patient management 
            and scheduling to AI-powered resource predictions and automated billing.
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {[
              { icon: Shield, text: 'Role-Based Access Control for all staff' },
              { icon: Activity, text: 'Real-time scheduling & conflict detection' },
              { icon: Lock, text: 'AI-powered 7-day bed occupancy predictions' },
            ].map(({ icon: Icon, text }) => (
              <div key={text} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: '#64748b' }}>
                <Icon size={16} style={{ color: '#06b6d4', flexShrink: 0 }} />
                <span style={{ fontSize: '0.85rem' }}>{text}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right panel - login form */}
        <div className="glass" style={{ borderRadius: 16, padding: '2rem' }}>
          <div style={{ marginBottom: '1.5rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f1f5f9', marginBottom: '0.25rem' }}>Sign In</h2>
            <p style={{ color: '#6b7280', fontSize: '0.8rem' }}>Access your HMS dashboard</p>
          </div>

          {/* Quick-login chips */}
          <div style={{ marginBottom: '1.25rem' }}>
            <div style={{ fontSize: '0.75rem', color: '#4b5563', marginBottom: '0.5rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Quick Demo Login</div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
              {QUICK_LOGINS.map((q) => (
                                <button key={q.role} onClick={() => { setUsername(q.username); setPassword(q.password); }}

                  style={{ fontSize: '0.7rem', padding: '0.3rem 0.6rem', borderRadius: 6, cursor: 'pointer', border: 'none',
                    background: username === q.username ? ROLE_LABELS[q.role].color + '33' : 'rgba(255,255,255,0.05)',
                    color: username === q.username ? ROLE_LABELS[q.role].color : '#6b7280',
                    borderWidth: 1, borderStyle: 'solid',
                    borderColor: username === q.username ? ROLE_LABELS[q.role].color + '66' : 'transparent',
                    transition: 'all 0.15s', fontWeight: 600 }}>
                  {ROLE_LABELS[q.role].label}
                </button>
              ))}
            </div>
          </div>

          <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: 600, display: 'block', marginBottom: '0.4rem' }}>
                Username
              </label>
              <div style={{ position: 'relative' }}>
                <User size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#4b5563' }} />
                <input className="input-field" style={{ paddingLeft: '2.25rem' }} type="text"
                  value={username} onChange={(e) => setUsername(e.target.value)} placeholder="Enter username" required />
              </div>
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: 600, display: 'block', marginBottom: '0.4rem' }}>
                Password
              </label>
              <div style={{ position: 'relative' }}>
                <Lock size={15} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: '#4b5563' }} />
                <input className="input-field" style={{ paddingLeft: '2.25rem' }} type="password"
                  value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Enter password" required />
              </div>
            </div>

            {error && (
              <div style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 8,
                padding: '0.625rem 0.875rem', fontSize: '0.8rem', color: '#f87171' }}>
                {error}
              </div>
            )}

            <button className="btn-primary" type="submit" disabled={loading}
              style={{ width: '100%', padding: '0.75rem', fontSize: '0.9rem', opacity: loading ? 0.7 : 1 }}>
              {loading ? 'Signing in...' : 'Sign In to HMS'}
            </button>
          </form>

          <div style={{ marginTop: '1.25rem', padding: '0.875rem', background: 'rgba(6,182,212,0.05)',
            border: '1px solid rgba(6,182,212,0.15)', borderRadius: 8 }}>
            <div style={{ fontSize: '0.72rem', color: '#4b5563', marginBottom: '0.4rem', fontWeight: 600 }}>DEMO CREDENTIALS</div>
            {QUICK_LOGINS.map((q) => (
              <div key={q.role} style={{ fontSize: '0.72rem', color: '#4b5563', fontFamily: 'monospace' }}>
                {q.username} / {q.password}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
