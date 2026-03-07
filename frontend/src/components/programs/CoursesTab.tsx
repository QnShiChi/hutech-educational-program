import { useState } from 'react';
import { Collapse, Table, Button, Space, Spin, Statistic, Row, Col, Popconfirm, Form, Input, InputNumber } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';

import PermissionGuard from '@/components/PermissionGuard';
import CourseSearchModal from './CourseSearchModal';
import {
  useKnowledgeBlocks,
  useCreateKnowledgeBlock,
  useDeleteKnowledgeBlock,
  useProgramCourses,
  useAddProgramCourse,
  useRemoveProgramCourse,
} from '@/hooks/useProgramDetail';
import { COURSE_TYPE_LABELS } from '@/types/api';
import type { ProgramCourse, Course } from '@/types/api';

interface Props {
  programId: string;
}

export default function CoursesTab({ programId }: Props) {
  const [modalOpen, setModalOpen] = useState(false);
  const [addingBlock, setAddingBlock] = useState(false);
  const [selectedBlock, setSelectedBlock] = useState<string | undefined>();
  const [blockForm] = Form.useForm();

  const { data: blocks, isLoading: loadingBlocks } = useKnowledgeBlocks(programId);
  const createBlock = useCreateKnowledgeBlock(programId);
  const deleteBlock = useDeleteKnowledgeBlock(programId);
  const { data: courses, isLoading: loadingCourses } = useProgramCourses(programId);
  const addCourse = useAddProgramCourse(programId);
  const removeCourse = useRemoveProgramCourse(programId);

  if (loadingBlocks || loadingCourses) return <Spin className="flex justify-center mt-10" />;

  const allCourses = courses ?? [];
  const existingCourseIds = allCourses.map((pc) => pc.course.id);

  const handleAddCourse = async (course: Course) => {
    await addCourse.mutateAsync({ course_id: course.id, group_id: selectedBlock });
    setModalOpen(false);
  };

  const handleAddBlock = async () => {
    try {
      const values = await blockForm.validateFields();
      await createBlock.mutateAsync(values);
      blockForm.resetFields();
      setAddingBlock(false);
    } catch {}
  };

  const coursesForBlock = (blockId: string | null) =>
    allCourses.filter((pc) => (pc.group?.id ?? null) === blockId);

  // Credit summary
  const requiredCredits = allCourses.filter((c) => c.is_required).reduce((s, c) => s + c.course.credits, 0);
  const electiveCredits = allCourses.filter((c) => !c.is_required).reduce((s, c) => s + c.course.credits, 0);
  const totalCredits = requiredCredits + electiveCredits;

  const courseColumns = [
    { title: 'Mã HP', key: 'code', render: (_: unknown, r: ProgramCourse) => r.course.code, width: 110 },
    { title: 'Tên học phần', key: 'name', render: (_: unknown, r: ProgramCourse) => r.course.name, ellipsis: true },
    { title: 'TC', key: 'credits', render: (_: unknown, r: ProgramCourse) => r.course.credits, width: 50 },
    { title: 'Loại', key: 'type', render: (_: unknown, r: ProgramCourse) => COURSE_TYPE_LABELS[r.course.course_type] ?? r.course.course_type, width: 110 },
    { title: 'BB/TC', key: 'required', render: (_: unknown, r: ProgramCourse) => r.is_required ? 'BB' : 'TC', width: 60 },
    { title: 'HK', dataIndex: 'semester', key: 'semester', width: 50 },
    {
      title: '',
      key: 'actions',
      width: 60,
      render: (_: unknown, r: ProgramCourse) => (
        <PermissionGuard requires="programs.manage_programs">
          <Popconfirm title="Xóa học phần này?" onConfirm={() => removeCourse.mutate(r.id)}>
            <Button type="link" danger size="small" icon={<DeleteOutlined />} />
          </Popconfirm>
        </PermissionGuard>
      ),
    },
  ];

  const blockItems = (blocks ?? []).sort((a, b) => a.order - b.order).map((block) => ({
    key: block.id,
    label: `${block.name} (${block.min_credits}${block.max_credits ? `–${block.max_credits}` : ''} TC)`,
    extra: (
      <PermissionGuard requires="programs.manage_programs">
        <Space onClick={(e) => e.stopPropagation()}>
          <Button size="small" icon={<PlusOutlined />} onClick={() => { setSelectedBlock(block.id); setModalOpen(true); }}>
            Thêm HP
          </Button>
          <Popconfirm title="Xóa khối kiến thức?" onConfirm={() => deleteBlock.mutate(block.id)}>
            <Button size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      </PermissionGuard>
    ),
    children: (
      <Table<ProgramCourse>
        rowKey="id"
        columns={courseColumns}
        dataSource={coursesForBlock(block.id)}
        pagination={false}
        size="small"
      />
    ),
  }));

  // Courses without block
  const unblocked = coursesForBlock(null);

  return (
    <div>
      <Space className="mb-3">
        <PermissionGuard requires="programs.manage_programs">
          <Button icon={<PlusOutlined />} onClick={() => setAddingBlock(true)}>
            Thêm khối kiến thức
          </Button>
          <Button onClick={() => { setSelectedBlock(undefined); setModalOpen(true); }}>
            Thêm học phần
          </Button>
        </PermissionGuard>
      </Space>

      {addingBlock && (
        <Form form={blockForm} layout="inline" className="mb-3">
          <Form.Item name="name" rules={[{ required: true }]}>
            <Input placeholder="Tên khối kiến thức" />
          </Form.Item>
          <Form.Item name="min_credits" rules={[{ required: true }]}>
            <InputNumber placeholder="Min TC" min={0} />
          </Form.Item>
          <Form.Item name="max_credits">
            <InputNumber placeholder="Max TC" min={0} />
          </Form.Item>
          <Button type="primary" onClick={handleAddBlock}>Thêm</Button>
          <Button onClick={() => setAddingBlock(false)}>Hủy</Button>
        </Form>
      )}

      <Collapse items={blockItems} defaultActiveKey={blocks?.map((b) => b.id)} />

      {unblocked.length > 0 && (
        <div className="mt-4">
          <strong>Học phần chưa phân khối</strong>
          <Table<ProgramCourse> rowKey="id" columns={courseColumns} dataSource={unblocked} pagination={false} size="small" />
        </div>
      )}

      <Row gutter={16} className="mt-4">
        <Col><Statistic title="Bắt buộc (BB)" value={requiredCredits} suffix="TC" /></Col>
        <Col><Statistic title="Tự chọn (TC)" value={electiveCredits} suffix="TC" /></Col>
        <Col><Statistic title="Tổng" value={totalCredits} suffix="TC" /></Col>
      </Row>

      <CourseSearchModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSelect={handleAddCourse}
        excludeIds={existingCourseIds}
      />
    </div>
  );
}
