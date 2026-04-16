import { useState } from 'react';
import type { ReactNode } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Activity, LogOut, Menu, X } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

interface NavItem { icon: ReactNode; label: string; path: string; }

interface Props {
  navItems: NavItem[];
  children: ReactNode;
  roleLabel: string;
  roleColor: string;
}

export default function DashboardLayout({ navItems, children, roleLabel, roleColor }: Props) {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = () => { logout(); navigate('/login'); };

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden', background: '#0a0f1e' }}>
      {/* Sidebar */}
      <aside style={{
        width: sidebarOpen ? 240 : 64, minWidth: sidebarOpen ? 240 : 64, background: '#060d1a',
        borderRight: '1px solid #1e2d45', display: 'flex', flexDirection: 'column',
        transition: 'width 0.25s ease, min-width 0.25s ease', overflow: 'hidden',
      }}>
        {/* Logo */}
        <div style={{ padding: '1rem', display: 'flex', alignItems: 'center', gap: '0.75rem',
          borderBottom: '1px solid #1e2d45', minHeight: 64 }}>
          <div style={{ width: 36, height: 36, borderRadius: 8,
            background: 'linear-gradient(135deg, #06b6d4, #6366f1)', display: 'flex', alignItems: 'center',
            justifyContent: 'center', flexShrink: 0 }}>
            <Activity size={20} color="white" />
          </div>
          {sidebarOpen && (
            <div style={{ overflow: 'hidden' }}>
              <div style={{ fontWeight: 800, fontSize: '0.95rem', color: '#f1f5f9', whiteSpace: 'nowrap' }}>MediCore HMS</div>
              <div style={{ fontSize: '0.65rem', color: roleColor, fontWeight: 600, whiteSpace: 'nowrap', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                {roleLabel}
              </div>
            </div>
          )}
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: '0.75rem', display: 'flex', flexDirection: 'column', gap: '0.25rem', overflowY: 'auto' }}>
          {navItems.map((item) => {
            const isActive = location.pathname === item.path || location.pathname.startsWith(item.path + '/');
            return (
              <div key={item.path} className={`sidebar-item ${isActive ? 'active' : ''}`}
                onClick={() => navigate(item.path)} title={item.label}>
                <span style={{ flexShrink: 0 }}>{item.icon}</span>
                {sidebarOpen && <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{item.label}</span>}
              </div>
            );
          })}
        </nav>

        {/* User + logout */}
        <div style={{ padding: '0.75rem', borderTop: '1px solid #1e2d45' }}>
          {sidebarOpen && (
            <div style={{ marginBottom: '0.5rem', padding: '0.5rem 0.75rem', borderRadius: 8,
              background: 'rgba(6,182,212,0.08)', border: '1px solid rgba(6,182,212,0.15)' }}>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#e2e8f0' }}>{user?.username}</div>
              <div style={{ fontSize: '0.7rem', color: roleColor, textTransform: 'capitalize' }}>{user?.role}</div>
            </div>
          )}
          <div className="sidebar-item" onClick={handleLogout} title="Logout"
            style={{ color: '#ef4444' }}>
            <LogOut size={16} style={{ flexShrink: 0 }} />
            {sidebarOpen && <span>Logout</span>}
          </div>
        </div>
      </aside>

      {/* Main */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
        {/* Topbar */}
        <header style={{ height: 64, background: '#060d1a', borderBottom: '1px solid #1e2d45',
          display: 'flex', alignItems: 'center', padding: '0 1.5rem', gap: '1rem', flexShrink: 0 }}>
          <button onClick={() => setSidebarOpen(!sidebarOpen)}
            style={{ background: 'none', border: 'none', color: '#6b7280', cursor: 'pointer', padding: 4, borderRadius: 6 }}>
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <div style={{ flex: 1 }} />
          <div style={{ fontSize: '0.8rem', color: '#4b5563' }}>
            {new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
          </div>
        </header>

        {/* Content */}
        <main style={{ flex: 1, overflowY: 'auto', padding: '1.5rem' }}>
          {children}
        </main>
      </div>
    </div>
  );
}
