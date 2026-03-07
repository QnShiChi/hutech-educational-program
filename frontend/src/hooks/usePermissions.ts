import { useQuery } from '@tanstack/react-query';
import * as rbac from '@/services/rbacService';

export function usePermissions(filters?: rbac.PermissionFilters) {
  return useQuery({
    queryKey: ['permissions', filters],
    queryFn: () => rbac.getPermissions(filters).then((r) => r.data),
  });
}
