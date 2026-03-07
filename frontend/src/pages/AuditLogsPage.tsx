import { useState, useMemo } from 'react';
import { Input, Select, Space, Table, Tag } from 'antd';
import { SearchOutlined } from '@ant-design/icons';

import PageHeader from '@/components/PageHeader';
import { useAuditLogs } from '@/hooks/useAuditLogs';
import type { AuditLog } from '@/types/api';

const ACTION_COLORS: Record<string, string> = {
  create: 'green',
  update: 'blue',
  delete: 'red',
  assign: 'purple',
  remove: 'orange',
};

export default function AuditLogsPage() {
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [actionFilter, setActionFilter] = useState<string | undefined>();
  const [entityFilter, setEntityFilter] = useState<string | undefined>();
  const [userFilter, setUserFilter] = useState<string | undefined>();

  const filters = useMemo(
    () => ({
      action: actionFilter,
      entity_type: entityFilter,
      user: userFilter,
      page,
      page_size: pageSize,
    }),
    [actionFilter, entityFilter, userFilter, page, pageSize],
  );

  const { data, isLoading } = useAuditLogs(filters);

  const columns = [
    {
      title: 'Thời gian',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (d: string) => new Date(d).toLocaleString('vi-VN'),
      width: 180,
    },
    {
      title: 'Người dùng',
      key: 'user_name',
      render: (_: unknown, r: AuditLog) => r.user_name ?? r.user_username ?? '—',
    },
    {
      title: 'Hành động',
      dataIndex: 'action',
      key: 'action',
      render: (action: string) => (
        <Tag color={ACTION_COLORS[action] ?? 'default'}>{action}</Tag>
      ),
    },
    {
      title: 'Loại đối tượng',
      dataIndex: 'entity_type',
      key: 'entity_type',
    },
    {
      title: 'ID',
      dataIndex: 'entity_id',
      key: 'entity_id',
      ellipsis: true,
    },
  ];

  return (
    <div>
      <PageHeader title="Nhật ký hệ thống" subtitle="Lịch sử thay đổi và hoạt động" />

      <Space className="mb-4" wrap>
        <Select
          placeholder="Hành động"
          allowClear
          style={{ width: 160 }}
          value={actionFilter}
          onChange={(v) => { setActionFilter(v); setPage(1); }}
          options={['create', 'update', 'delete', 'assign', 'remove'].map((a) => ({
            label: a, value: a,
          }))}
        />
        <Select
          placeholder="Loại đối tượng"
          allowClear
          style={{ width: 180 }}
          value={entityFilter}
          onChange={(v) => { setEntityFilter(v); setPage(1); }}
          options={['User', 'Role', 'Department', 'TrainingProgram'].map((e) => ({
            label: e, value: e,
          }))}
        />
        <Input
          prefix={<SearchOutlined />}
          placeholder="User ID..."
          value={userFilter}
          onChange={(e) => { setUserFilter(e.target.value || undefined); setPage(1); }}
          allowClear
          style={{ width: 200 }}
        />
      </Space>

      <Table<AuditLog>
        rowKey="id"
        columns={columns}
        dataSource={data?.results}
        loading={isLoading}
        expandable={{
          expandedRowRender: (record) => (
            <div className="grid grid-cols-2 gap-4">
              <div>
                <strong>Dữ liệu cũ:</strong>
                <pre className="bg-gray-50 p-2 rounded text-xs mt-1 overflow-auto max-h-40">
                  {record.old_data ? JSON.stringify(record.old_data, null, 2) : '—'}
                </pre>
              </div>
              <div>
                <strong>Dữ liệu mới:</strong>
                <pre className="bg-gray-50 p-2 rounded text-xs mt-1 overflow-auto max-h-40">
                  {record.new_data ? JSON.stringify(record.new_data, null, 2) : '—'}
                </pre>
              </div>
            </div>
          ),
        }}
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
