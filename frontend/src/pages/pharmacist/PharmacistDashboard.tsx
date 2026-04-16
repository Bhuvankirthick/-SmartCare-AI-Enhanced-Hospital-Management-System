import { useEffect, useState } from 'react';
import { Package, AlertTriangle, PlusCircle, RefreshCw } from 'lucide-react';
import DashboardLayout from '../../components/DashboardLayout';
import api from '../../api/client';

const NAV = [
  { icon: <Package size={17} />, label: 'Inventory', path: '/pharmacist' },
  { icon: <AlertTriangle size={17} />, label: 'Low Stock Alerts', path: '/pharmacist/alerts' },
  { icon: <PlusCircle size={17} />, label: 'Add Medicine', path: '/pharmacist/add' },
  { icon: <RefreshCw size={17} />, label: 'Restock', path: '/pharmacist/restock' },
];

export default function PharmacistDashboard() {
  const [tab, setTab] = useState<'inventory' | 'alerts' | 'add'>('inventory');
  const [medicines, setMedicines] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [q, setQ] = useState('');
  const [form, setForm] = useState({ name: '', category: '', stock_level: '', reorder_threshold: '20', unit_price: '', supplier: '', unit: 'tablets' });
  const [saving, setSaving] = useState(false);
  const [addMsg, setAddMsg] = useState('');
  const [restockId, setRestockId] = useState<number | null>(null);
  const [restockQty, setRestockQty] = useState('');

  useEffect(() => {
    api.get('/medicines/?limit=200').then(r => { setMedicines(r.data); setLoading(false); });
  }, []);

  const lowStock = medicines.filter(m => m.is_low_stock);
  const filtered = medicines.filter(m => m.name.toLowerCase().includes(q.toLowerCase()) || m.category?.toLowerCase().includes(q.toLowerCase()));

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault(); setSaving(true); setAddMsg('');
    try {
      const res = await api.post('/medicines/', {
        name: form.name, category: form.category,
        stock_level: parseInt(form.stock_level) || 0,
        reorder_threshold: parseInt(form.reorder_threshold) || 20,
        unit_price: parseFloat(form.unit_price) || 0,
        supplier: form.supplier, unit: form.unit,
      });
      setMedicines([...medicines, res.data]);
      setAddMsg(`Added "${form.name}" to inventory.`);
      setForm({ name: '', category: '', stock_level: '', reorder_threshold: '20', unit_price: '', supplier: '', unit: 'tablets' });
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Error adding medicine');
    } finally { setSaving(false); }
  };

  const handleRestock = async (id: number) => {
    const qty = parseInt(restockQty);
    if (!qty || qty <= 0) return;
    const med = medicines.find(m => m.medicine_id === id);
    await api.put(`/medicines/${id}`, { stock_level: med.stock_level + qty });
    setMedicines(medicines.map(m => m.medicine_id === id ? { ...m, stock_level: m.stock_level + qty, is_low_stock: (m.stock_level + qty) <= m.reorder_threshold } : m));
    setRestockId(null); setRestockQty('');
  };

  const CATEGORY_COLORS: Record<string, string> = {
    'Analgesic': '#06b6d4', 'Antibiotic': '#6366f1', 'Antidiabetic': '#10b981',
    'Antacid': '#f59e0b', 'NSAID': '#ec4899', 'IV Fluid': '#8b5cf6',
    'Hormone': '#ef4444', 'Lipid-lowering': '#f97316',
  };

  return (
    <DashboardLayout navItems={NAV} roleLabel="Pharmacist" roleColor="#ec4899">
      <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
        {(['inventory', 'alerts', 'add'] as const).map(t => (
          <button key={t} onClick={() => setTab(t)}
            style={{ padding: '0.4rem 0.875rem', borderRadius: 6, border: 'none', cursor: 'pointer', fontSize: '0.8rem', fontWeight: 600,
              background: tab === t ? 'linear-gradient(135deg, #ec4899, #6366f1)' : '#111827',
              color: tab === t ? 'white' : '#6b7280', transition: 'all 0.15s',
              position: 'relative' }}>
            {t === 'inventory' ? 'Drug Inventory' : t === 'alerts' ? `Low Stock Alerts ${lowStock.length > 0 ? `(${lowStock.length})` : ''}` : 'Add Medicine'}
          </button>
        ))}
      </div>

      {loading ? <div style={{ color: '#4b5563', textAlign: 'center', padding: '2rem' }}>Loading...</div> : (
        <div className="animate-slide-up">
          {/* Stats */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.5rem' }}>
            {[
              { label: 'Total Medicines', value: medicines.length, color: '#06b6d4' },
              { label: 'Low Stock Alerts', value: lowStock.length, color: '#ef4444' },
              { label: 'Well Stocked', value: medicines.length - lowStock.length, color: '#10b981' },
              { label: 'Categories', value: new Set(medicines.map(m => m.category)).size, color: '#6366f1' },
            ].map(s => (
              <div key={s.label} className="stat-card" style={{ borderTopWidth: 3, borderTopColor: s.color }}>
                <div style={{ fontSize: '0.72rem', color: '#6b7280', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>{s.label}</div>
                <div style={{ fontSize: '1.75rem', fontWeight: 800, color: s.label === 'Low Stock Alerts' && lowStock.length > 0 ? '#ef4444' : '#f1f5f9' }}>{s.value}</div>
              </div>
            ))}
          </div>

          {tab === 'inventory' && (
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <div style={{ fontSize: '0.875rem', fontWeight: 700, color: '#e2e8f0' }}>Medicine Inventory</div>
                <input className="input-field" placeholder="Search medicines..." value={q} onChange={e => setQ(e.target.value)} style={{ width: 250 }} />
              </div>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid #1e2d45' }}>
                    {['Medicine', 'Category', 'Stock', 'Threshold', 'Unit Price', 'Supplier', 'Status', 'Action'].map(h =>
                      <th key={h} style={{ textAlign: 'left', padding: '0.5rem 0.75rem', fontSize: '0.75rem', color: '#4b5563', fontWeight: 600 }}>{h}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((m: any) => (
                    <tr key={m.medicine_id} className="table-row">
                      <td style={{ padding: '0.625rem 0.75rem', fontWeight: 600, color: '#e2e8f0', fontSize: '0.85rem' }}>{m.name}</td>
                      <td style={{ padding: '0.625rem 0.75rem' }}>
                        <span style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', borderRadius: 4, fontWeight: 600,
                          background: (CATEGORY_COLORS[m.category] || '#6b7280') + '22', color: CATEGORY_COLORS[m.category] || '#6b7280',
                          border: `1px solid ${(CATEGORY_COLORS[m.category] || '#6b7280')}44` }}>
                          {m.category}
                        </span>
                      </td>
                      <td style={{ padding: '0.625rem 0.75rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <div style={{ width: 60, height: 5, background: '#1e2d45', borderRadius: 2 }}>
                            <div style={{
                              height: '100%', borderRadius: 2,
                              width: `${Math.min(100, (m.stock_level / Math.max(m.reorder_threshold * 3, 1)) * 100)}%`,
                              background: m.is_low_stock ? '#ef4444' : '#10b981',
                            }} />
                          </div>
                          <span style={{ color: m.is_low_stock ? '#ef4444' : '#e2e8f0', fontWeight: 600, fontSize: '0.85rem' }}>{m.stock_level}</span>
                        </div>
                      </td>
                      <td style={{ padding: '0.625rem 0.75rem', color: '#6b7280', fontSize: '0.8rem' }}>{m.reorder_threshold}</td>
                      <td style={{ padding: '0.625rem 0.75rem', color: '#10b981', fontWeight: 600, fontSize: '0.82rem' }}>₹{m.unit_price}/{m.unit}</td>
                      <td style={{ padding: '0.625rem 0.75rem', color: '#6b7280', fontSize: '0.78rem' }}>{m.supplier}</td>
                      <td style={{ padding: '0.625rem 0.75rem' }}>
                        {m.is_low_stock
                          ? <span className="badge-danger" style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', borderRadius: 4, fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem', width: 'fit-content' }}>
                            <AlertTriangle size={10} /> Low Stock
                          </span>
                          : <span className="badge-success" style={{ fontSize: '0.7rem', padding: '0.2rem 0.5rem', borderRadius: 4, fontWeight: 600 }}>OK</span>
                        }
                      </td>
                      <td style={{ padding: '0.625rem 0.75rem' }}>
                        {restockId === m.medicine_id ? (
                          <div style={{ display: 'flex', gap: '0.3rem' }}>
                            <input className="input-field" type="number" placeholder="Qty" value={restockQty} onChange={e => setRestockQty(e.target.value)}
                              style={{ width: 60, padding: '0.2rem 0.4rem', fontSize: '0.75rem' }} />
                            <button onClick={() => handleRestock(m.medicine_id)}
                              style={{ fontSize: '0.72rem', padding: '0.2rem 0.5rem', borderRadius: 4, border: 'none', cursor: 'pointer', background: 'rgba(16,185,129,0.15)', color: '#10b981' }}>+</button>
                            <button onClick={() => setRestockId(null)}
                              style={{ fontSize: '0.72rem', padding: '0.2rem 0.4rem', borderRadius: 4, border: 'none', cursor: 'pointer', background: 'transparent', color: '#4b5563' }}>✕</button>
                          </div>
                        ) : (
                          <button onClick={() => { setRestockId(m.medicine_id); setRestockQty(''); }}
                            style={{ fontSize: '0.72rem', color: '#06b6d4', background: 'none', border: 'none', cursor: 'pointer' }}>
                            Restock
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {tab === 'alerts' && (
            <div>
              <div style={{ marginBottom: '1rem' }}>
                <h1 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f1f5f9' }}>Low Stock Alerts</h1>
                <p style={{ color: '#6b7280', fontSize: '0.8rem' }}>{lowStock.length} medicines below reorder threshold</p>
              </div>
              {lowStock.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '3rem', background: '#111827', borderRadius: 12, border: '1px solid #1e2d45' }}>
                  <div style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>✅</div>
                  <div style={{ color: '#10b981', fontWeight: 600 }}>All medicines are well-stocked!</div>
                </div>
              ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1rem' }}>
                  {lowStock.map((m: any) => (
                    <div key={m.medicine_id} style={{ background: '#111827', border: '1px solid rgba(239,68,68,0.3)', borderRadius: 12, padding: '1.25rem',
                      borderLeft: '3px solid #ef4444' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                        <div>
                          <div style={{ fontWeight: 700, color: '#e2e8f0', fontSize: '0.9rem' }}>{m.name}</div>
                          <div style={{ color: '#6b7280', fontSize: '0.75rem' }}>{m.category} · {m.supplier}</div>
                        </div>
                        <AlertTriangle size={18} style={{ color: '#ef4444', flexShrink: 0 }} />
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.75rem' }}>
                        <span>Current Stock: <b style={{ color: '#ef4444' }}>{m.stock_level} {m.unit}</b></span>
                        <span>Min Required: <b style={{ color: '#f59e0b' }}>{m.reorder_threshold}</b></span>
                      </div>
                      <div style={{ height: 5, background: '#1e2d45', borderRadius: 2, marginBottom: '0.75rem' }}>
                        <div style={{ height: '100%', borderRadius: 2, width: `${Math.min(100, (m.stock_level / m.reorder_threshold) * 100)}%`, background: '#ef4444' }} />
                      </div>
                      <div style={{ padding: '0.5rem 0.75rem', background: 'rgba(239,68,68,0.08)', borderRadius: 6, fontSize: '0.75rem', color: '#f87171' }}>
                        Need {Math.max(0, m.reorder_threshold - m.stock_level)} units to reach minimum threshold. Contact: {m.supplier}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {tab === 'add' && (
            <div className="card" style={{ maxWidth: 600 }}>
              <div style={{ fontSize: '1rem', fontWeight: 700, color: '#e2e8f0', marginBottom: '1.25rem' }}>Add New Medicine</div>
              {addMsg && <div style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: 8, padding: '0.75rem', marginBottom: '1rem', color: '#10b981', fontSize: '0.85rem' }}>{addMsg}</div>}
              <form onSubmit={handleAdd} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.875rem' }}>
                {[
                  { key: 'name', label: 'Medicine Name', required: true, span: 2 },
                  { key: 'category', label: 'Category' },
                  { key: 'supplier', label: 'Supplier' },
                  { key: 'stock_level', label: 'Initial Stock', type: 'number' },
                  { key: 'reorder_threshold', label: 'Reorder Threshold', type: 'number' },
                  { key: 'unit_price', label: 'Unit Price (₹)', type: 'number' },
                ].map(f => (
                  <div key={f.key} style={{ gridColumn: f.span === 2 ? '1/-1' : 'auto' }}>
                    <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>{f.label}</label>
                    <input className="input-field" type={f.type || 'text'} required={f.required}
                      value={(form as any)[f.key]} onChange={e => setForm({ ...form, [f.key]: e.target.value })} />
                  </div>
                ))}
                <div>
                  <label style={{ fontSize: '0.75rem', color: '#94a3b8', display: 'block', marginBottom: '0.3rem', fontWeight: 600 }}>Unit</label>
                  <select className="input-field" value={form.unit} onChange={e => setForm({ ...form, unit: e.target.value })}>
                    {['tablets', 'capsules', 'ml', 'mg', 'units', 'bags', 'vials', 'strips', 'bottles'].map(u => <option key={u}>{u}</option>)}
                  </select>
                </div>
                <div style={{ gridColumn: '1/-1' }}>
                  <button type="submit" className="btn-primary" disabled={saving} style={{ padding: '0.625rem 1.5rem' }}>
                    {saving ? 'Adding...' : 'Add to Inventory'}
                  </button>
                </div>
              </form>
            </div>
          )}
        </div>
      )}
    </DashboardLayout>
  );
}
