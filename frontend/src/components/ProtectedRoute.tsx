import { useEffect, useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import { useAuthStore } from '@/store/authStore';
import apiClient from '@/services/apiClient';
import type { User } from '@/types/api';

/**
 * Wrapper that redirects unauthenticated users to /login.
 * On first mount with a stored token it also fetches the user profile.
 */
export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user, setUser, logout } = useAuthStore();
  const location = useLocation();
  const [loading, setLoading] = useState(!user && isAuthenticated);

  useEffect(() => {
    if (isAuthenticated && !user) {
      apiClient
        .get<User>('/rbac/users/me/')
        .then((res) => setUser(res.data))
        .catch(() => logout())
        .finally(() => setLoading(false));
    }
  }, [isAuthenticated, user, setUser, logout]);

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <Spin size="large" tip="Đang tải..." />
      </div>
    );
  }

  return <>{children}</>;
}
