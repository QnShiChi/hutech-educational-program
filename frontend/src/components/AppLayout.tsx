import { useState, useMemo } from 'react';
import { Outlet, useNavigate, useLocation, Link } from 'react-router-dom';
import { Layout, Menu, Breadcrumb, Avatar, Dropdown, Button, Drawer, Grid } from 'antd';
import {
  AuditOutlined,
  BookOutlined,
  DashboardOutlined,
  FileSearchOutlined,
  ImportOutlined,
  LogoutOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  PartitionOutlined,
  ReadOutlined,
  SafetyOutlined,
  SettingOutlined,
  TeamOutlined,
  UserOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useAuthStore } from '@/store/authStore';
import NotificationBell from '@/components/NotificationBell';

const { Header, Sider, Content } = Layout;
const { useBreakpoint } = Grid;

/* ─── Route → breadcrumb label map ─── */
const BREADCRUMB_MAP: Record<string, string> = {
  '/': 'Dashboard',
  '/rbac': 'Phân quyền',
  '/rbac/users': 'Người dùng',
  '/rbac/roles': 'Vai trò',
  '/rbac/departments': 'Khoa / Phòng ban',
  '/rbac/audit-logs': 'Nhật ký',
  '/programs': 'Chương trình ĐT',
  '/programs/new': 'Tạo mới',
  '/programs/import': 'Import',
  '/courses': 'Học phần',
  '/approvals': 'Phê duyệt',
  '/settings': 'Cài đặt',
};

/* ─── Sidebar menu definition ─── */
const sidebarItems: MenuProps['items'] = [
  {
    key: '/',
    icon: <DashboardOutlined />,
    label: 'Dashboard',
  },
  {
    key: 'rbac',
    icon: <SafetyOutlined />,
    label: 'Phân quyền',
    children: [
      { key: '/rbac/users', icon: <TeamOutlined />, label: 'Người dùng' },
      { key: '/rbac/roles', icon: <UserOutlined />, label: 'Vai trò' },
      { key: '/rbac/departments', icon: <PartitionOutlined />, label: 'Khoa / Phòng ban' },
      { key: '/rbac/audit-logs', icon: <FileSearchOutlined />, label: 'Nhật ký' },
    ],
  },
  {
    key: 'programs_group',
    icon: <BookOutlined />,
    label: 'Chương trình ĐT',
    children: [
      { key: '/programs', icon: <BookOutlined />, label: 'Danh sách CTĐT' },
      { key: '/programs/import', icon: <ImportOutlined />, label: 'Import' },
    ],
  },
  {
    key: '/courses',
    icon: <ReadOutlined />,
    label: 'Học phần',
  },
  {
    key: '/approvals',
    icon: <AuditOutlined />,
    label: 'Phê duyệt',
  },
  {
    key: '/settings',
    icon: <SettingOutlined />,
    label: 'Cài đặt',
  },
];

function useBreadcrumbs() {
  const location = useLocation();

  return useMemo(() => {
    const segments = location.pathname.split('/').filter(Boolean);
    const items: { title: React.ReactNode }[] = [
      { title: <Link to="/">Dashboard</Link> },
    ];

    let path = '';
    for (const segment of segments) {
      path += `/${segment}`;
      const label = BREADCRUMB_MAP[path];
      if (label) {
        items.push({
          title: path === location.pathname ? label : <Link to={path}>{label}</Link>,
        });
      }
    }

    return items;
  }, [location.pathname]);
}

/* ─── Selected / open keys for sidebar ─── */
function useMenuKeys() {
  const { pathname } = useLocation();

  const selectedKeys = [pathname];
  const openKeys: string[] = [];

  if (pathname.startsWith('/rbac')) openKeys.push('rbac');
  if (pathname.startsWith('/programs')) openKeys.push('programs_group');

  return { selectedKeys, openKeys };
}

export default function AppLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();
  const screens = useBreakpoint();
  const breadcrumbItems = useBreadcrumbs();
  const { selectedKeys, openKeys } = useMenuKeys();

  const isMobile = !screens.md;

  const handleMenuClick: MenuProps['onClick'] = ({ key }) => {
    navigate(key);
    if (isMobile) setDrawerOpen(false);
  };

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: user?.name || user?.username || 'Profile',
    },
    { type: 'divider' },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Đăng xuất',
      onClick: () => {
        logout();
        navigate('/login');
      },
    },
  ];

  const menuContent = (
    <>
      <div
        className="flex items-center justify-center text-white font-bold"
        style={{ height: 64, fontSize: collapsed && !isMobile ? 16 : 18 }}
      >
        {collapsed && !isMobile ? 'HP' : 'HUTECH Program'}
      </div>
      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={selectedKeys}
        defaultOpenKeys={openKeys}
        items={sidebarItems}
        onClick={handleMenuClick}
      />
    </>
  );

  return (
    <Layout className="min-h-screen">
      {/* Desktop sidebar */}
      {!isMobile && (
        <Sider
          trigger={null}
          collapsible
          collapsed={collapsed}
          theme="dark"
          width={240}
        >
          {menuContent}
        </Sider>
      )}

      {/* Mobile drawer */}
      {isMobile && (
        <Drawer
          placement="left"
          closable={false}
          onClose={() => setDrawerOpen(false)}
          open={drawerOpen}
          width={240}
          styles={{ body: { padding: 0, background: '#001529' } }}
        >
          {menuContent}
        </Drawer>
      )}

      <Layout>
        <Header className="flex items-center justify-between bg-white px-4 shadow-sm" style={{ height: 64 }}>
          <div className="flex items-center gap-2">
            <Button
              type="text"
              icon={
                isMobile
                  ? <MenuUnfoldOutlined />
                  : collapsed
                    ? <MenuUnfoldOutlined />
                    : <MenuFoldOutlined />
              }
              onClick={() => (isMobile ? setDrawerOpen(true) : setCollapsed(!collapsed))}
            />
            <Breadcrumb items={breadcrumbItems} />
          </div>

          <div className="flex items-center gap-2">
            <NotificationBell />
            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <Avatar
                icon={<UserOutlined />}
                style={{ cursor: 'pointer', backgroundColor: '#003399' }}
              />
            </Dropdown>
          </div>
        </Header>

        <Content className="m-4 p-6 bg-white rounded-lg" style={{ minHeight: 280 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}
