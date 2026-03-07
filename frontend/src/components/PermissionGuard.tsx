import type { ReactNode } from 'react';
import { useAuthStore } from '@/store/authStore';

interface PermissionGuardProps {
  /** Required permission codename, e.g. "programs.add_trainingprogram" */
  requires?: string;
  /** Pass multiple — user needs at least ONE */
  requiresAny?: string[];
  /** Fallback UI when permission is denied (default: null / hidden) */
  fallback?: ReactNode;
  children: ReactNode;
}

/**
 * Conditionally renders children based on user permissions.
 *
 * Usage:
 *   <PermissionGuard requires="programs.add_trainingprogram">
 *     <Button>Tạo CTĐT</Button>
 *   </PermissionGuard>
 */
export default function PermissionGuard({
  requires,
  requiresAny,
  fallback = null,
  children,
}: PermissionGuardProps) {
  const hasPermission = useAuthStore((s) => s.hasPermission);
  const hasAnyPermission = useAuthStore((s) => s.hasAnyPermission);

  if (requires && !hasPermission(requires)) {
    return <>{fallback}</>;
  }

  if (requiresAny && requiresAny.length > 0 && !hasAnyPermission(...requiresAny)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
