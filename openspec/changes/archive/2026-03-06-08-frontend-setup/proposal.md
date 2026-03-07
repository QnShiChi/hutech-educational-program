# Proposal: Frontend Setup & Layout

## Summary
Scaffold React + TypeScript + Vite frontend với Ant Design, tạo layout chung (sidebar, header, breadcrumb), routing, auth flow, API client.

## Design

### Layout Structure
```
┌─────────────────────────────────────────────────────┐
│ Header: Logo | Breadcrumb              | Bell | User│
├──────────┬──────────────────────────────────────────┤
│ Sidebar  │ Content Area                             │
│          │                                          │
│ Dashboard│                                          │
│ Phân quyền│                                         │
│  - Users │                                          │
│  - Roles │                                          │
│  - Depts │                                          │
│ CTĐT     │                                          │
│  - DS CTĐT│                                         │
│  - Import│                                          │
│ Học phần │                                          │
│ Phê duyệt│                                         │
│ Cài đặt  │                                          │
└──────────┴──────────────────────────────────────────┘
```

### Route Structure
```typescript
/login
/dashboard
/rbac/users
/rbac/users/:id
/rbac/roles
/rbac/departments
/programs
/programs/new
/programs/import
/programs/:id              (detail with tabs)
/programs/:id/edit
/courses
/courses/:id
/approvals
/approvals/:id
/settings
```

### Auth Flow
1. Login page → POST /api/v1/auth/token/ → get access + refresh tokens
2. Store tokens in memory (Zustand store, NOT localStorage)
3. Axios interceptor: add Bearer token to all requests
4. On 401: try refresh → if fail → redirect to login
5. User profile + permissions loaded on app init from /api/v1/rbac/users/me/

### Permission Guard
```typescript
// Component that hides content based on permissions
<PermissionGuard requires="programs.create">
  <Button>Tạo CTĐT</Button>
</PermissionGuard>

// Hook
const canCreate = usePermission('programs.create');
```

### API Client Setup
```typescript
// services/api.ts
const api = axios.create({ baseURL: '/api/v1/' });
api.interceptors.request.use(addAuthToken);
api.interceptors.response.use(null, handleAuthError);

// hooks/usePrograms.ts
export const usePrograms = (filters) => useQuery({
  queryKey: ['programs', filters],
  queryFn: () => api.get('/programs/', { params: filters })
});
```
