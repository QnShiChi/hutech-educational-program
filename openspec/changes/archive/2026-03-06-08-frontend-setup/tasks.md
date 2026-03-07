# Tasks: 08 - Frontend Setup

## 1. Project Init

- [x] 1.1 Create Vite React-TS project
- [x] 1.2 Install deps: antd, tailwind, axios, tanstack-query, zustand, react-router-dom
- [x] 1.3 Configure Tailwind + Ant Design theme (HUTECH brand colors)
- [x] 1.4 Configure path aliases (@/ → src/)
- [x] 1.5 Configure Vite proxy to Django backend

## 2. Auth & State

- [x] 2.1 Create auth store (Zustand): user, tokens, permissions, login/logout
- [x] 2.2 Create API client (Axios) with JWT interceptor
- [x] 2.3 Create Login page (Ant Design Form)
- [x] 2.4 Create ProtectedRoute component
- [x] 2.5 Create PermissionGuard component

## 3. Layout

- [x] 3.1 Create MainLayout with Ant Design Layout (Sider + Header + Content)
- [x] 3.2 Create Sidebar with menu items (icons, groups, collapse)
- [x] 3.3 Create Header (breadcrumb, notification bell, user avatar dropdown)
- [x] 3.4 Create responsive behavior (mobile sidebar as drawer)

## 4. Routing

- [x] 4.1 Setup React Router with all routes
- [x] 4.2 Create placeholder pages for all routes
- [x] 4.3 Implement breadcrumb auto-generation from route
- [x] 4.4 404 page

## 5. Shared Components

- [x] 5.1 PageHeader component (title + actions)
- [x] 5.2 DataTable component (wrapper around Ant Table with search/filter/pagination)
- [x] 5.3 StatusTag component (color-coded status badges)
- [x] 5.4 ConfirmModal component
- [x] 5.5 NotificationBell component (badge + dropdown)

## 6. TypeScript Types

- [x] 6.1 Define all API response types (User, Role, Permission, Department)
- [x] 6.2 Define TrainingProgram, PLO, PO, Course types
- [x] 6.3 Define API pagination response type
- [x] 6.4 Define Enum types matching backend choices

## 7. Verification

- [x] 7.1 Build passes (vite build ✓)
