import { useEffect, useState } from 'react';
import { Calendar, ClipboardList, FileText, User } from 'lucide-react';
import DashboardLayout from '../../components/DashboardLayout';
import api from '../../api/client';
import { useAuthStore } from '../../store/authStore';

const NAV = [
  { icon: <Calendar size={17} />, label: 'My Appointments', path: '/doctor' },
  { icon: <ClipboardList size={17} />, label: 'Patient EHR', path: '/doctor/ehr' },
  { icon: <FileText size={17} />, label: 'Write Treatment', path: '/doctor/treatment' },
  { icon: <User size={17} />, label: 'My Patients', path: '/doctor/patients' },
];

export default function DoctorDashboard() {
  const { user } = useAuthStore();
  const [appointments, setAppointments] = useState<any[]>([]);
  const [tab, setTab] = useState<'appointments' | 'ehr' | 'treatment'>('appointments');
  const [loading, setLoading] = useState(true);
  const [patients, setPatients] = useState<any[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<any>(null);
  const [patientTreatments, setPatientTreatments] = useState<any[]>([]);
  const [txForm, setTxForm] = useState({ patient_id: '', diagnosis: '', description: '', medications: '', lab_results: '', cost: '' });
  const [saving, setSaving] = useState(false);
  const [txSuccess, setTxSuccess] = useState('');

  useEffect(() => {
    Promise.all([
      api.get('/appointments/').then(r => setAppointments(r.data)),
      api.get('/patients/?limit=100').then(r => setPatients(r.data)),
    ]).finally(() => setLoading(false));
  }, []);

  const loadPatientEHR = async (pid: number) => {
    const p = patients.find(px => px.patient_id === pid);
    setSelectedPatient(p);
    const res = await api.get(`/treatments/patient/${pid}`);
    setPatientTreatments(res.data);
  };

  const handleTreatment = async (e: React.FormEvent) => {
    e.preventDefault(); setSaving(true); setTxSuccess('');
    try {
      const meds = txForm.medications ? txForm.medications.split(',').map(m => ({ name: m.trim(), dose: 'As prescribed', duration: '7 days' })) : [];
      await api.post('/treatments/', {
        patient_id: parseInt(txForm.patient_id),
        doctor_id: user?.linked_id,
        diagnosis: txForm.diagnosis,
        description: txForm.description,
        medications: meds,
        lab_results: txForm.lab_results,
        cost: parseFloat(txForm.cost) || 0,
      });
      setTxSuccess('Treatment record saved successfully!');
      setTxForm({ patient_id: '', diagnosis: '', description: '', medications: '', lab_results: '', cost: '' });
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error saving treatment');
    } finally { setSaving(false); }
  };

  const today = appointments.filter(a => {
    const d = new Date(a.appointment_date);
    const now = new Date();
    return d.toDateString() === now.toDateString();
  });

  const upcoming = appointments.filter(a => new Date(a.appointment_date) > new Date() && a.status !== 'cancelled');

  return (
    <DashboardLayout navItems={NAV} roleLabel="Doctor Portal" roleColor="#06b6d4">
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        {(['appointments', 'ehr', 'treatment'] as const).map(t => (
          <button key={t} onClick={() => setTab(t)}
            style={{ padding: '0.4rem 0.875rem', borderRadius: 6, border: 'none', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600, textTransform: 'capitalize',
              background: tab === t ? 'linear-gradient(135deg, #06b6d4, #6366f1)' : '#111827',
              color: tab === t ? 'white' : '#6b7280', transition: 'all 0.15s' }}>
            {t === 'ehr' ? 'Patient EHR' : t === 'treatment' ? 'Write Treatment' : 'My Appointments'}
          </button>
        ))}
      </div>

      {loading ? <div style={{ color: '#4b5563', textAlign: 'center', padding: '2rem' }}>Loading...</div> : (
        <div className="animate-slide-up">
          {tab === 'appointments' && (
            <>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
                {[
                  { label: "Today's Appointments", value: today.length, color: '#06b6d4' },
                  { label: 'Upcoming', value: upcoming.length, color: '#6366f1' },
                  { label: 'Total', value: appointments.length, color: '#10b981' },
                ].map(s => (
                  <div key={s.label} className="stat-card" style={{ borderTopWidth: 3, borderTopColor: s.color }}>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>{s.label}</div>
                    <div style={{ fontSize: '2rem', fontWeight: 800, color: '#f1f5f9' }}>{s.value}</div>
                  </div>
                ))}
              </div>

              <div className="card">
                <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '1rem' }}>All Appointments</div>
                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #1e2d45' }}>
                      {['Patient', 'Date & Time', 'Reason', 'Status', 'Action'].map(h =>
                        <th key={h} style={{ textAlign: 'left', padding: '0.5rem 0.75rem', fontSize: '0.75rem', color: '#4b5563', fontWeight: 600 }}>{h}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {appointments.map((a: any) => (
                      <tr key={a.appointment_id} className="table-row">
                        <td style={{ padding: '0.625rem 0.75rem', fontWeight: 600, color: '#e2e8f0', fontSize: '0.85rem' }}>{a.patient_name}</td>
                        <td style={{ padding: '0.625rem 0.75rem', color: '#6b7280', fontSize: '0.8rem' }}>
                          {new Date(a.appointment_date).toLocaleString('en-IN', { dateStyle: 'medium', timeStyle: 'short' })}
                        </td>
                        <td style={{ padding: '0.625rem 0.75rem', color: '#94a3b8', fontSize: '0.8rem' }}>{a.reason}</td>
                        <td style={{ padding: '0.625rem 0.75rem' }}>
                          <span className={`badge-${a.status === 'completed' ? 'success' : a.status === 'cancelled' ? 'danger' : a.status === 'confirmed' ? 'info' : 'warning'}`}
                            style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', borderRadius: 4, display: 'inline-block', fontWeight: 600 }}>
                            {a.status}
                          </span>
                        </td>
                        <td style={{ padding: '0.625rem 0.75rem' }}>
                          <button onClick={() => { setTab('ehr'); loadPatientEHR(a.patient_id); setTxForm({ ...txForm, patient_id: String(a.patient_id) }); }}
                            style={{ fontSize: '0.75rem', color: '#06b6d4', background: 'none', border: 'none', cursor: 'pointer' }}>
                            View EHR
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}

          {tab === 'ehr' && (
            <div>
              <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f1f5f9', marginBottom: '1rem' }}>Patient EHR — Medical History</h1>
              <div style={{ display: 'grid', gridTemplateColumns: '280px 1fr', gap: '1rem' }}>
                <div className="card" style={{ height: 'fit-content' }}>
                  <div style={{ fontSize: '0.8rem', fontWeight: 700, color: '#94a3b8', marginBottom: '0.75rem' }}>SELECT PATIENT</div>
                  {patients.map((p: any) => (
                    <div key={p.patient_id} onClick={() => loadPatientEHR(p.patient_id)}
                      style={{ padding: '0.5rem 0.625rem', borderRadius: 6, cursor: 'pointer', marginBottom: '0.25rem', transition: 'all 0.15s',
                        background: selectedPatient?.patient_id === p.patient_id ? 'rgba(6,182,212,0.12)' : 'transparent',
                        border: `1px solid ${selectedPatient?.patient_id === p.patient_id ? 'rgba(6,182,212,0.3)' : 'transparent'}` }}>
                      <div style={{ fontWeight: 600, color: '#e2e8f0', fontSize: '0.85rem' }}>{p.name}</div>
                      <div style={{ color: '#4b5563', fontSize: '0.72rem' }}>{p.gender} · {p.blood_type}</div>
                    </div>
                  ))}
                </div>

                <div>
                  {selectedPatient ? (
                    <div>
                      <div className="card" style={{ marginBottom: '1rem' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem' }}>
                          {[
                            { label: 'Full Name', value: selectedPatient.name },
                            { label: 'Date of Birth', value: selectedPatient.date_of_birth || 'N/A' },
                            { label: 'Blood Type', value: selectedPatient.blood_type },
                            { label: 'Gender', value: selectedPatient.gender },
                            { label: 'Contact', value: selectedPatient.contact_number },
                            { label: 'Emergency Contact', value: selectedPatient.emergency_contact },
                          ].map(f => (
                            <div key={f.label}>
                              <div style={{ fontSize: '0.7rem', color: '#4b5563', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{f.label}</div>
                              <div style={{ fontSize: '0.85rem', color: '#e2e8f0', marginTop: '0.2rem' }}>{f.value}</div>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '0.75rem' }}>
                        Treatment History ({patientTreatments.length} records)
                      </div>
                      {patientTreatments.length === 0 ? (
                        <div style={{ color: '#4b5563', padding: '1.5rem', textAlign: 'center', background: '#111827', borderRadius: 12, border: '1px solid #1e2d45' }}>
                          No treatment records yet.
                        </div>
                      ) : (
                        patientTreatments.map((t: any) => (
                          <div key={t.treatment_id} className="card" style={{ marginBottom: '0.75rem', borderLeft: '3px solid #06b6d4' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                              <div style={{ fontWeight: 700, color: '#e2e8f0', fontSize: '0.9rem' }}>{t.diagnosis}</div>
                              <div style={{ color: '#4b5563', fontSize: '0.75rem' }}>
                                {new Date(t.treatment_date).toLocaleDateString('en-IN', { dateStyle: 'medium' })} · Dr. {t.doctor_name}
                              </div>
                            </div>
                            {t.description && <p style={{ color: '#94a3b8', fontSize: '0.8rem', marginBottom: '0.75rem', lineHeight: 1.6 }}>{t.description}</p>}
                            {t.medications?.length > 0 && (
                              <div style={{ marginBottom: '0.5rem' }}>
                                <div style={{ fontSize: '0.7rem', fontWeight: 700, color: '#6366f1', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.4rem' }}>MEDICATIONS</div>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem' }}>
                                  {t.medications.map((m: any, i: number) => (
                                    <span key={i} className="badge-purple" style={{ fontSize: '0.72rem', padding: '0.25rem 0.5rem', borderRadius: 4 }}>
                                      {m.name} · {m.dose}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                            {t.lab_results && (
                              <div style={{ background: '#0a0f1e', borderRadius: 6, padding: '0.5rem 0.75rem', fontSize: '0.78rem', color: '#6b7280', marginTop: '0.5rem' }}>
                                <span style={{ color: '#4b5563', fontWeight: 600 }}>Lab Results: </span>{t.lab_results}
                              </div>
                            )}
                          </div>
                        ))
                      )}
                    </div>
                  ) : (
                    <div style={{ color: '#4b5563', padding: '3rem', textAlign: 'center', background: '#111827', borderRadius: 12, border: '1px solid #1e2d45' }}>
                      Select a patient to view their medical history
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {tab === 'treatment' && (
            <div>
              <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f1f5f9', marginBottom: '1rem' }}>Write Treatment / Prescription</h1>
              <div className="card" style={{ maxWidth: 700 }}>
                {txSuccess && (
                  <div style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: 8,
                    padding: '0.75rem', marginBottom: '1rem', color: '#10b981', fontSize: '0.85rem' }}>
                    {txSuccess}
                  </div>
                )}
                <form onSubmit={handleTreatment} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Select Patient *</label>
                    <select className="input-field" required value={txForm.patient_id} onChange={e => setTxForm({ ...txForm, patient_id: e.target.value })}>
                      <option value="">-- Select Patient --</option>
                      {patients.map(p => <option key={p.patient_id} value={p.patient_id}>{p.name} (ID: {p.patient_id})</option>)}
                    </select>
                  </div>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Diagnosis *</label>
                    <input className="input-field" required value={txForm.diagnosis}
                      onChange={e => setTxForm({ ...txForm, diagnosis: e.target.value })} placeholder="e.g. Type 2 Diabetes Mellitus" />
                  </div>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Clinical Notes</label>
                    <textarea className="input-field" value={txForm.description}
                      onChange={e => setTxForm({ ...txForm, description: e.target.value })}
                      placeholder="Detailed clinical description, observations, and plan..." rows={4} style={{ resize: 'vertical' }} />
                  </div>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>
                      Medications (comma-separated names)
                    </label>
                    <input className="input-field" value={txForm.medications}
                      onChange={e => setTxForm({ ...txForm, medications: e.target.value })}
                      placeholder="e.g. Metformin 500mg, Atorvastatin 10mg" />
                  </div>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Lab Results</label>
                    <textarea className="input-field" value={txForm.lab_results}
                      onChange={e => setTxForm({ ...txForm, lab_results: e.target.value })}
                      placeholder="Blood panel, imaging, or other test results..." rows={2} style={{ resize: 'vertical' }} />
                  </div>
                  <div>
                    <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Treatment Cost (₹)</label>
                    <input className="input-field" type="number" value={txForm.cost}
                      onChange={e => setTxForm({ ...txForm, cost: e.target.value })} placeholder="0.00" />
                  </div>
                  <button type="submit" className="btn-primary" disabled={saving} style={{ alignSelf: 'flex-start', padding: '0.625rem 1.5rem' }}>
                    {saving ? 'Saving...' : 'Save Treatment Record'}
                  </button>
                </form>
              </div>
            </div>
          )}
        </div>
      )}
    </DashboardLayout>
  );
}
