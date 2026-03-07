import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button, Input, Table, Tag, Modal, Form, InputNumber, Select } from 'antd';
import { PlusOutlined, SearchOutlined, EyeOutlined } from '@ant-design/icons';

import PageHeader from '@/components/PageHeader';
import PermissionGuard from '@/components/PermissionGuard';
import { useCourses, useCreateCourse } from '@/hooks/useCourses';
import { COURSE_TYPE_LABELS } from '@/types/api';
import type { Course, CourseType } from '@/types/api';

export default function CoursesPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [search, setSearch] = useState('');
  const [createOpen, setCreateOpen] = useState(false);
  const [form] = Form.useForm();
  const createCourse = useCreateCourse();

  const filters = useMemo(() => ({
    search: search || undefined,
    page,
    page_size: pageSize,
  }), [search, page, pageSize]);

  const { data, isLoading } = useCourses(filters);

  const handleCreate = async () => {
    try {
      const values = await form.validateFields();
      await createCourse.mutateAsync(values);
      setCreateOpen(false);
      form.resetFields();
    } catch {}
  };

  const columns = [
    { title: 'Mã HP', dataIndex: 'code', key: 'code', width: 120 },
    { title: 'Tên học phần', dataIndex: 'name', key: 'name', ellipsis: true },
    { title: 'TC', dataIndex: 'credits', key: 'credits', width: 60 },
    { title: 'LT', dataIndex: 'theory_hours', key: 'theory_hours', width: 50 },
    { title: 'TH', dataIndex: 'practice_hours', key: 'practice_hours', width: 50 },
    { title: 'Tự học', dataIndex: 'self_study_hours', key: 'self_study', width: 60 },
    {
      title: 'Loại',
      dataIndex: 'course_type',
      key: 'course_type',
      width: 110,
      render: (v: CourseType) => <Tag>{COURSE_TYPE_LABELS[v] ?? v}</Tag>,
    },
    {
      title: '',
      key: 'actions',
      width: 80,
      render: (_: unknown, record: Course) => (
        <Button type="link" icon={<EyeOutlined />} onClick={() => navigate(`/courses/${record.id}`)}>
          Xem
        </Button>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Học phần"
        subtitle="Danh sách học phần trong hệ thống"
        actions={
          <PermissionGuard requires="programs.manage_courses">
            <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateOpen(true)}>
              Tạo học phần
            </Button>
          </PermissionGuard>
        }
      />

      <Input
        prefix={<SearchOutlined />}
        placeholder="Tìm theo mã hoặc tên..."
        value={search}
        onChange={(e) => { setSearch(e.target.value); setPage(1); }}
        allowClear
        style={{ width: 300, marginBottom: 16 }}
      />

      <Table<Course>
        rowKey="id"
        columns={columns}
        dataSource={data?.results}
        loading={isLoading}
        onRow={(record) => ({
          onClick: () => navigate(`/courses/${record.id}`),
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
        size="middle"
      />

      <Modal
        title="Tạo Học phần mới"
        open={createOpen}
        onCancel={() => setCreateOpen(false)}
        onOk={handleCreate}
        confirmLoading={createCourse.isPending}
        destroyOnClose
      >
        <Form form={form} layout="vertical">
          <Form.Item name="code" label="Mã HP" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="name" label="Tên học phần" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="name_en" label="Tên tiếng Anh">
            <Input />
          </Form.Item>
          <Form.Item name="credits" label="Số tín chỉ" rules={[{ required: true }]}>
            <InputNumber min={1} max={20} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="course_type" label="Loại" rules={[{ required: true }]}>
            <Select options={Object.entries(COURSE_TYPE_LABELS).map(([k, v]) => ({ value: k, label: v }))} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
