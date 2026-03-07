import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import viVN from 'antd/locale/vi_VN';

import themeConfig from '@/theme/themeConfig';
import AppLayout from '@/components/AppLayout';
import ProtectedRoute from '@/components/ProtectedRoute';

import LoginPage from '@/pages/LoginPage';
import DashboardPage from '@/pages/DashboardPage';
import UsersPage from '@/pages/UsersPage';
import UserDetailPage from '@/pages/UserDetailPage';
import RolesPage from '@/pages/RolesPage';
import RoleDetailPage from '@/pages/RoleDetailPage';
import DepartmentsPage from '@/pages/DepartmentsPage';
import AuditLogsPage from '@/pages/AuditLogsPage';
import ProgramsPage from '@/pages/ProgramsPage';
import ProgramNewPage from '@/pages/ProgramNewPage';
import ProgramImportPage from '@/pages/ProgramImportPage';
import ProgramDetailPage from '@/pages/ProgramDetailPage';
import CoursesPage from '@/pages/CoursesPage';
import CourseDetailPage from '@/pages/CourseDetailPage';
import ApprovalsPage from '@/pages/ApprovalsPage';
import ApprovalDetailPage from '@/pages/ApprovalDetailPage';
import SettingsPage from '@/pages/SettingsPage';
import NotFoundPage from '@/pages/NotFoundPage';

import './index.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ConfigProvider locale={viVN} theme={themeConfig}>
        <BrowserRouter>
          <Routes>
            {/* Public */}
            <Route path="/login" element={<LoginPage />} />

            {/* Protected area */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <AppLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<DashboardPage />} />

              {/* RBAC */}
              <Route path="rbac/users" element={<UsersPage />} />
              <Route path="rbac/users/new" element={<UserDetailPage />} />
              <Route path="rbac/users/:id" element={<UserDetailPage />} />
              <Route path="rbac/roles" element={<RolesPage />} />
              <Route path="rbac/roles/new" element={<RoleDetailPage />} />
              <Route path="rbac/roles/:id" element={<RoleDetailPage />} />
              <Route path="rbac/departments" element={<DepartmentsPage />} />
              <Route path="rbac/audit-logs" element={<AuditLogsPage />} />

              {/* Programs / CTĐT */}
              <Route path="programs" element={<ProgramsPage />} />
              <Route path="programs/new" element={<ProgramNewPage />} />
              <Route path="programs/import" element={<ProgramImportPage />} />
              <Route path="programs/:id" element={<ProgramDetailPage />} />
              <Route path="programs/:id/edit" element={<ProgramDetailPage />} />

              {/* Courses */}
              <Route path="courses" element={<CoursesPage />} />
              <Route path="courses/:id" element={<CourseDetailPage />} />

              {/* Approvals */}
              <Route path="approvals" element={<ApprovalsPage />} />
              <Route path="approvals/:id" element={<ApprovalDetailPage />} />

              {/* Settings */}
              <Route path="settings" element={<SettingsPage />} />
            </Route>

            {/* 404 */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </BrowserRouter>
      </ConfigProvider>
    </QueryClientProvider>
  );
}
