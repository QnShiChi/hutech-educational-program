import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Input, Select, Space, Table, Tag } from 'antd';
import { PlusOutlined, UploadOutlined, SearchOutlined, EyeOutlined } from '@ant-design/icons';

import PageHeader from '@/components/PageHeader';
import PermissionGuard from '@/components/PermissionGuard';
import StatusTag from '@/components/StatusTag';
import { usePrograms } from '@/hooks/usePrograms';
import { useDepartments } from '@/hooks/useDepartments';
import type { TrainingProgram, ProgramStatus, DegreeLevel } from '@/types/api';
import { DEGREE_LEVEL_LABELS, TRAINING_MODE_LABELS, PROGRAM_STATUS_LABELS } from '@/types/api';

export default function ProgramsPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | undefined>();
  const [deptFilter, setDeptFilter] = useState<string | undefined>();
  const [degreeFilter, setDegreeFilter] = useState<string | undefined>();

  const filters = useMemo(
    () => ({
      search: search || undefined,
      status: statusFilter,
      department: deptFilter,
      degree_level: degreeFilter,
      page,
      page_size: pageSize,
    }),
    [search, statusFilter, deptFilter, degreeFilter, page, pageSize],
  );

  const { data, isLoading } = usePrograms(filters);
  const { data: deptData } = useDepartments({ page_size: 200 });

  const columns = [
    { title: 'Mã ngành', dataIndex: 'code', key: 'code', width: 120 },
    {
      title: 'Tên ngành',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: 'Trình độ',
      dataIndex: 'degree_level',
      key: 'degree_level',
      width: 110,
      render: (v: DegreeLevel) => <Tag>{DEGREE_LEVEL_LABELS[v] ?? v}</Tag>,
    },
    {
      title: 'Hình thức',
      dataIndex: 'training_mode',
      key: 'training_mode',
      width: 120,
      render: (v: string) => TRAINING_MODE_LABELS[v as keyof typeof TRAINING_MODE_LABELS] ?? v,
    },
    { title: 'Tín chỉ', dataIndex: 'total_credits', key: 'total_credits', width: 80 },
    {
      title: 'Trạng thái',
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (v: ProgramStatus) => <StatusTag status={v} />,
    },
    { title: 'Phiên bản', dataIndex: 'version', key: 'version', width: 100 },
    {
      title: '',
      key: 'actions',
      width: 80,
      render: (_: unknown, record: TrainingProgram) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => navigate(`/programs/${record.id}`)}
        >
          Xem
        </Button>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Chương trình Đào tạo"
        subtitle="Danh sách tất cả chương trình đào tạo"
        actions={
          <Space>
            <PermissionGuard requires="programs.manage_programs">
              <Button icon={<UploadOutlined />} onClick={() => navigate('/programs/import')}>
                Import Word
              </Button>
            </PermissionGuard>
            <PermissionGuard requires="programs.manage_programs">
              <Button type="primary" icon={<PlusOutlined />} onClick={() => navigate('/programs/new')}>
                Tạo mới
              </Button>
            </PermissionGuard>
          </Space>
        }
      />

      <Space className="mb-4" wrap>
        <Input
          prefix={<SearchOutlined />}
          placeholder="Tìm theo tên, mã ngành..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          allowClear
          style={{ width: 280 }}
        />
        <Select
          placeholder="Trạng thái"
          allowClear
          style={{ width: 150 }}
          value={statusFilter}
          onChange={(v) => { setStatusFilter(v); setPage(1); }}
          options={Object.entries(PROGRAM_STATUS_LABELS).map(([k, v]) => ({ value: k, label: v }))}
        />
        <Select
          placeholder="Khoa / Bộ môn"
          allowClear
          style={{ width: 200 }}
          value={deptFilter}
          onChange={(v) => { setDeptFilter(v); setPage(1); }}
          options={deptData?.results?.map((d) => ({ label: d.name, value: d.id })) ?? []}
        />
        <Select
          placeholder="Trình độ"
          allowClear
          style={{ width: 140 }}
          value={degreeFilter}
          onChange={(v) => { setDegreeFilter(v); setPage(1); }}
          options={Object.entries(DEGREE_LEVEL_LABELS).map(([k, v]) => ({ value: k, label: v }))}
        />
      </Space>

      <Table<TrainingProgram>
        rowKey="id"
        columns={columns}
        dataSource={data?.results}
        loading={isLoading}
        onRow={(record) => ({
          onClick: () => navigate(`/programs/${record.id}`),
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
