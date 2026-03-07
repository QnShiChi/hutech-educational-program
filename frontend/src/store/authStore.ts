import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/types/api';

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: User | null;
  permissions: string[];
  isAuthenticated: boolean;

  setTokens: (access: string, refresh: string) => void;
  setUser: (user: User) => void;
  logout: () => void;
  hasPermission: (perm: string) => boolean;
  hasAnyPermission: (...perms: string[]) => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      accessToken: null,
      refreshToken: null,
      user: null,
      permissions: [],
      isAuthenticated: false,

      setTokens: (access: string, refresh: string) =>
        set({ accessToken: access, refreshToken: refresh, isAuthenticated: true }),

      setUser: (user: User) =>
        set({ user, permissions: user.permissions ?? [] }),

      logout: () =>
        set({
          accessToken: null,
          refreshToken: null,
          user: null,
          permissions: [],
          isAuthenticated: false,
        }),

      hasPermission: (perm: string) => {
        const { permissions } = get();
        return permissions.includes(perm);
      },

      hasAnyPermission: (...perms: string[]) => {
        const { permissions } = get();
        return perms.some((p) => permissions.includes(p));
      },
    }),
    {
      name: 'hutech-auth',
    },
  ),
);
