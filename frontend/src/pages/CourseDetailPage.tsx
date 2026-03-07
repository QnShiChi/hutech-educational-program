import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Form, Input, InputNumber, Select, Button, Card, Spin, Result, Space } from 'antd';
import { SaveOutlined, ArrowLeftOutlined } from '@ant-design/icons';

import PageHeader from '@/components/PageHeader';
import PermissionGuard from '@/components/PermissionGuard';
import { useCourse, useUpdateCourse } from '@/hooks/useCourses';
import { COURSE_TYPE_LABELS } from '@/types/api';

export default function CourseDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const { data: course, isLoading, error } = useCourse(id);
  const updateCourse = useUpdateCourse();
  const [editing, setEditing] = useState(false);

  if (isLoading) return <Spin size="large" className="flex justify-center mt-20" />;
  if (error || !course) return <Result status="404" title="Không tìm thấy học phần" />;

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      await updateCourse.mutateAsync({ id: course.id, data: values });
      setEditing(false);
    } catch {}
  };

  return (
    <div>
      <PageHeader
        title={`${course.code} — ${course.name}`}
        actions={
          <Space>
            <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/courses')}>
              Quay lại
            </Button>
            <PermissionGuard requires="programs.manage_courses">
              {!editing && (
                <Button type="primary" onClick={() => { setEditing(true); form.setFieldsValue(course); }}>
                  Chỉnh sửa
                </Button>
              )}
            </PermissionGuard>
          </Space>
        }
      />

      <Card style={{ maxWidth: 700 }}>
        <Form
          form={form}
          layout="vertical"
          initialValues={course}
          disabled={!editing}
        >
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
          <Form.Item name="theory_hours" label="Số tiết lý thuyết">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="practice_hours" label="Số tiết thực hành">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="self_study_hours" label="Số tiết tự học">
            <InputNumber min={0} style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="course_type" label="Loại học phần" rules={[{ required: true }]}>
            <Select options={Object.entries(COURSE_TYPE_LABELS).map(([k, v]) => ({ value: k, label: v }))} />
          </Form.Item>
          <Form.Item name="description" label="Mô tả">
            <Input.TextArea rows={4} />
          </Form.Item>

          {editing && (
            <Space>
              <Button type="primary" icon={<SaveOutlined />} onClick={handleSave} loading={updateCourse.isPending}>
                Lưu
              </Button>
              <Button onClick={() => setEditing(false)}>Hủy</Button>
            </Space>
          )}
        </Form>
      </Card>
    </div>
  );
}
