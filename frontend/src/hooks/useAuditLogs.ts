import { useQuery } from '@tanstack/react-query';
import * as rbac from '@/services/rbacService';

export function useAuditLogs(filters?: rbac.AuditLogFilters) {
  return useQuery({
    queryKey: ['auditLogs', filters],
    queryFn: () => rbac.getAuditLogs(filters).then((r) => r.data),
  });
}
