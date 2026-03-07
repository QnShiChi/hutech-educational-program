import { useState } from 'react';
import { Modal, Input, Table, Button } from 'antd';
import { SearchOutlined, PlusOutlined } from '@ant-design/icons';
import { useCourses } from '@/hooks/useCourses';
import type { Course } from '@/types/api';
import { COURSE_TYPE_LABELS } from '@/types/api';

interface Props {
  open: boolean;
  onClose: () => void;
  onSelect: (course: Course) => void;
  excludeIds?: string[];
}

export default function CourseSearchModal({ open, onClose, onSelect, excludeIds = [] }: Props) {
  const [search, setSearch] = useState('');
  const { data, isLoading } = useCourses({ search: search || undefined, page_size: 50 });

  const filtered = data?.results?.filter((c) => !excludeIds.includes(c.id)) ?? [];

  const columns = [
    { title: 'Mã HP', dataIndex: 'code', key: 'code', width: 120 },
    { title: 'Tên học phần', dataIndex: 'name', key: 'name', ellipsis: true },
    { title: 'Tín chỉ', dataIndex: 'credits', key: 'credits', width: 70 },
    {
      title: 'Loại',
      dataIndex: 'course_type',
      key: 'course_type',
      width: 110,
      render: (v: string) => COURSE_TYPE_LABELS[v as keyof typeof COURSE_TYPE_LABELS] ?? v,
    },
    {
      title: '',
      key: 'action',
      width: 80,
      render: (_: unknown, record: Course) => (
        <Button type="link" size="small" icon={<PlusOutlined />} onClick={() => onSelect(record)}>
          Thêm
        </Button>
      ),
    },
  ];

  return (
    <Modal
      title="Tìm kiếm Học phần"
      open={open}
      onCancel={onClose}
      footer={null}
      width={700}
      destroyOnClose
    >
      <Input
        prefix={<SearchOutlined />}
        placeholder="Tìm theo mã hoặc tên..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        allowClear
        className="mb-3"
      />
      <Table<Course>
        rowKey="id"
        columns={columns}
        dataSource={filtered}
        loading={isLoading}
        pagination={{ pageSize: 10, showSizeChanger: false }}
        size="small"
      />
    </Modal>
  );
}
