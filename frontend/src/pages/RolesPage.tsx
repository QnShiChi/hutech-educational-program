import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Input, Table, Tag } from 'antd';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';

import PageHeader from '@/components/PageHeader';
import PermissionGuard from '@/components/PermissionGuard';
import { useRoles } from '@/hooks/useRoles';
import type { Role } from '@/types/api';

export default function RolesPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState('');

  const filters = useMemo(
    () => ({ search: search || undefined, page, page_size: pageSize }),
    [search, page, pageSize],
  );

  const { data, isLoading } = useRoles(filters);

  const columns = [
    {
      title: 'Tên vai trò',
      dataIndex: 'name',
      key: 'name',
    },
    { title: 'Mã', dataIndex: 'code', key: 'code' },
    { title: 'Level', dataIndex: 'level', key: 'level' },
    {
      title: 'Hệ thống',
      dataIndex: 'is_system_role',
      key: 'is_system_role',
      render: (v: boolean) => v ? <Tag color="purple">Hệ thống</Tag> : null,
    },
    {
      title: 'Số permissions',
      key: 'permissions_count',
      render: (_: unknown, record: Role) => record.permissions?.length ?? 0,
    },
    {
      title: 'Số users',
      dataIndex: 'user_count',
      key: 'user_count',
      render: (v?: number) => v ?? '—',
    },
  ];

  return (
    <div>
      <PageHeader
        title="Quản lý Vai trò"
        subtitle="Danh sách vai trò và phân quyền"
        actions={
          <PermissionGuard requires="rbac.manage_roles">
            <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/rbac/roles/new')}>
              Tạo vai trò
            </Button>
          </PermissionGuard>
        }
      />

      <Input
        prefix={<SearchOutlined />}
        placeholder="Tìm theo tên hoặc mã..."
        value={search}
        onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        allowClear
        style={{ maxWidth: 320, marginBottom: 16 }}
      />

      <Table<Role>
        rowKey="id"
        columns={columns}
        dataSource={data?.results}
        loading={isLoading}
        onRow={(record) => ({
          onClick: () => navigate(`/rbac/roles/${record.id}`),
          style: { cursor: 'pointer' },
        })}
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
