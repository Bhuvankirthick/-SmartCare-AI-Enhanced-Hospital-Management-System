import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface AuthUser {
  user_id: number;
  username: string;
  role: string;
  linked_id: number | null;
  access_token: string;
}

interface AuthStore {
  user: AuthUser | null;
  isAuthenticated: boolean;
  setUser: (user: AuthUser) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      setUser: (user) => set({ user, isAuthenticated: true }),
      logout: () => set({ user: null, isAuthenticated: false }),
    }),
    { name: 'hms-auth' }
  )
);
