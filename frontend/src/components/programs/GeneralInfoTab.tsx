import { useState } from 'react';
import { Form, Input, InputNumber, Select, Button, Descriptions, Space } from 'antd';
import { EditOutlined, SaveOutlined, CloseOutlined } from '@ant-design/icons';

import PermissionGuard from '@/components/PermissionGuard';
import StatusTag from '@/components/StatusTag';
import { useUpdateProgram } from '@/hooks/usePrograms';
import { useSubmitProgram } from '@/hooks/useWorkflow';
import { useDepartments } from '@/hooks/useDepartments';
import { DEGREE_LEVEL_LABELS, TRAINING_MODE_LABELS } from '@/types/api';
import type { TrainingProgram } from '@/types/api';

interface Props {
  program: TrainingProgram;
}

export default function GeneralInfoTab({ program }: Props) {
  const [editing, setEditing] = useState(false);
  const [form] = Form.useForm();
  const updateProgram = useUpdateProgram();
  const submitProgram = useSubmitProgram(program.id);
  const { data: deptData } = useDepartments({ page_size: 200 });

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      await updateProgram.mutateAsync({ id: program.id, data: values });
      setEditing(false);
    } catch {
      // validation or API error
    }
  };

  if (editing) {
    return (
      <Form form={form} layout="vertical" initialValues={program} style={{ maxWidth: 700 }}>
        <Form.Item name="code" label="Mã ngành" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="name" label="Tên ngành" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="name_en" label="Tên tiếng Anh" rules={[{ required: true }]}>
          <Input />
        </Form.Item>
        <Form.Item name="department_id" label="Khoa">
          <Select
            showSearch
            optionFilterProp="label"
            options={deptData?.results?.map((d) => ({ label: d.name, value: d.id })) ?? []}
          />
        </Form.Item>
        <Form.Item name="degree_level" label="Trình độ">
          <Select options={Object.entries(DEGREE_LEVEL_LABELS).map(([k, v]) => ({ value: k, label: v }))} />
        </Form.Item>
        <Form.Item name="training_mode" label="Hình thức">
          <Select options={Object.entries(TRAINING_MODE_LABELS).map(([k, v]) => ({ value: k, label: v }))} />
        </Form.Item>
        <Form.Item name="total_credits" label="Tổng tín chỉ">
          <InputNumber min={1} style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item name="duration_years" label="Thời gian (năm)">
          <InputNumber min={1} max={10} style={{ width: '100%' }} />
        </Form.Item>
        <Form.Item name="effective_year" label="Năm áp dụng">
          <InputNumber min={2020} max={2050} style={{ width: '100%' }} />
        </Form.Item>
        <Space>
          <Button type="primary" icon={<SaveOutlined />} onClick={handleSave} loading={updateProgram.isPending}>
            Lưu
          </Button>
          <Button icon={<CloseOutlined />} onClick={() => setEditing(false)}>Hủy</Button>
        </Space>
      </Form>
    );
  }

  return (
    <div>
      <Space className="mb-4">
        <PermissionGuard requires="programs.manage_programs">
          <Button icon={<EditOutlined />} onClick={() => setEditing(true)}>
            Chỉnh sửa
          </Button>
        </PermissionGuard>
        <PermissionGuard requires="programs.submit_program">
          {program.status === 'draft' && (
            <Button type="primary" onClick={() => submitProgram.mutate()} loading={submitProgram.isPending}>
              Gửi phê duyệt
            </Button>
          )}
        </PermissionGuard>
      </Space>

      <Descriptions bordered column={2}>
        <Descriptions.Item label="Mã ngành">{program.code}</Descriptions.Item>
        <Descriptions.Item label="Trạng thái"><StatusTag status={program.status} /></Descriptions.Item>
        <Descriptions.Item label="Tên ngành">{program.name}</Descriptions.Item>
        <Descriptions.Item label="Tên tiếng Anh">{program.name_en}</Descriptions.Item>
        <Descriptions.Item label="Khoa">{program.department?.name ?? '—'}</Descriptions.Item>
        <Descriptions.Item label="Trình độ">{DEGREE_LEVEL_LABELS[program.degree_level]}</Descriptions.Item>
        <Descriptions.Item label="Hình thức">{TRAINING_MODE_LABELS[program.training_mode]}</Descriptions.Item>
        <Descriptions.Item label="Tổng tín chỉ">{program.total_credits}</Descriptions.Item>
        <Descriptions.Item label="Thời gian đào tạo">{program.duration_years} năm</Descriptions.Item>
        <Descriptions.Item label="Năm áp dụng">{program.effective_year ?? '—'}</Descriptions.Item>
        <Descriptions.Item label="Phiên bản">{program.version}</Descriptions.Item>
      </Descriptions>
    </div>
  );
}
