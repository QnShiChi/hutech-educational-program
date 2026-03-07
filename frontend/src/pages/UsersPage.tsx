import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Input, Select, Space, Table, Tag } from 'antd';
import { PlusOutlined, EditOutlined, StopOutlined, SearchOutlined } from '@ant-design/icons';

import PageHeader from '@/components/PageHeader';
import PermissionGuard from '@/components/PermissionGuard';
import { confirmModal } from '@/components/ConfirmModal';
import { useUsers, useDeactivateUser } from '@/hooks/useUsers';
import { useDepartments } from '@/hooks/useDepartments';
import type { User } from '@/types/api';

export default function UsersPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [deptFilter, setDeptFilter] = useState<string | undefined>();
  const [statusFilter, setStatusFilter] = useState<boolean | undefined>();

  const filters = useMemo(
    () => ({
      search: search || undefined,
      department: deptFilter,
      is_active: statusFilter,
      page,
      page_size: pageSize,
    }),
    [search, deptFilter, statusFilter, page, pageSize],
  );

  const { data, isLoading } = useUsers(filters);
  const { data: deptData } = useDepartments({ page_size: 200 });
  const deactivate = useDeactivateUser();

  const handleDeactivate = (user: User) => {
    confirmModal({
      content: `Vô hiệu hóa người dùng "${user.name || user.username}"?`,
      danger: true,
      onOk: async () => { await deactivate.mutateAsync(user.id); },
    });
  };

  const columns = [
    {
      title: 'Họ tên',
      dataIndex: 'name',
      key: 'name',
      render: (name: string, record: User) => name || `${record.first_name} ${record.last_name}`.trim() || record.username,
    },
    { title: 'Email', dataIndex: 'email', key: 'email' },
    { title: 'Mã NV', dataIndex: 'employee_id', key: 'employee_id' },
    {
      title: 'Đơn vị',
      key: 'department',
      render: (_: unknown, record: User) => record.department?.name ?? '—',
    },
    {
      title: 'Vai trò',
      key: 'roles',
      render: (_: unknown, record: User) =>
        record.roles?.map((r) => (
          <Tag key={r.id} color="blue">
            {r.name}
          </Tag>
        )) ?? '—',
    },
    {
      title: 'Trạng thái',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) =>
        active ? <Tag color="green">Hoạt động</Tag> : <Tag color="red">Vô hiệu</Tag>,
    },
    {
      title: 'Hành động',
      key: 'actions',
      render: (_: unknown, record: User) => (
        <Space>
          <PermissionGuard requires="rbac.manage_users">
            <Button
              type="link"
              icon={<EditOutlined />}
              onClick={() => navigate(`/rbac/users/${record.id}`)}
            >
              Sửa
            </Button>
          </PermissionGuard>
          <PermissionGuard requires="rbac.manage_users">
            {record.is_active && (
              <Button
                type="link"
                danger
                icon={<StopOutlined />}
                onClick={() => handleDeactivate(record)}
              >
                Vô hiệu hóa
              </Button>
            )}
          </PermissionGuard>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Quản lý Người dùng"
        subtitle="Danh sách người dùng hệ thống"
        actions={
          <PermissionGuard requires="rbac.manage_users">
            <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/rbac/users/new')}>
              Tạo người dùng
            </Button>
          </PermissionGuard>
        }
      />

      <Space className="mb-4" wrap>
        <Input
          prefix={<SearchOutlined />}
          placeholder="Tìm theo tên, email, mã NV..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          allowClear
          style={{ width: 280 }}
        />
        <Select
          placeholder="Đơn vị"
          allowClear
          style={{ width: 200 }}
          value={deptFilter}
          onChange={(v) => { setDeptFilter(v); setPage(1); }}
          options={deptData?.results?.map((d) => ({ label: d.name, value: d.id })) ?? []}
        />
        <Select
          placeholder="Trạng thái"
          allowClear
          style={{ width: 140 }}
          value={statusFilter}
          onChange={(v) => { setStatusFilter(v); setPage(1); }}
          options={[
            { label: 'Hoạt động', value: true },
            { label: 'Vô hiệu', value: false },
          ]}
        />
      </Space>

      <Table<User>
        rowKey="id"
        columns={columns}
        dataSource={data?.results}
        loading={isLoading}
        pagination={{
          current: page,
          pageSize,
          total: data?.count ?? 0,
          showSizeChanger: true,
          showTotal: (total) => `Tổng: ${total}`,
          onChange: (p, ps) => { setPage(p); setPageSize(ps); },
        }}
        scroll={{ x: 'max-content' }}
        size="middle"
      />
    </div>
  );
}
