import { useNavigate } from 'react-router-dom';
import { Form, Input, InputNumber, Select, Button, Card } from 'antd';

import PageHeader from '@/components/PageHeader';
import { useCreateProgram } from '@/hooks/usePrograms';
import { useDepartments } from '@/hooks/useDepartments';
import { DEGREE_LEVEL_LABELS, TRAINING_MODE_LABELS } from '@/types/api';
import type { TrainingProgram } from '@/types/api';

export default function ProgramNewPage() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const createProgram = useCreateProgram();
  const { data: deptData } = useDepartments({ page_size: 200 });

  const handleFinish = async (values: Partial<TrainingProgram>) => {
    try {
      const result = await createProgram.mutateAsync(values);
      navigate(`/programs/${result.id}`);
    } catch {
      // error already handled by hook
    }
  };

  return (
    <div>
      <PageHeader title="Tạo Chương trình Đào tạo mới" />

      <Card style={{ maxWidth: 800 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={handleFinish}
          initialValues={{ degree_level: 'cu_nhan', training_mode: 'chinh_quy', duration_years: 4 }}
        >
          <Form.Item name="code" label="Mã ngành" rules={[{ required: true, message: 'Vui lòng nhập mã ngành' }]}>
            <Input placeholder="VD: 7480201" />
          </Form.Item>

          <Form.Item name="name" label="Tên ngành (Tiếng Việt)" rules={[{ required: true, message: 'Vui lòng nhập tên ngành' }]}>
            <Input placeholder="VD: Công nghệ Thông tin" />
          </Form.Item>

          <Form.Item name="name_en" label="Tên ngành (Tiếng Anh)" rules={[{ required: true, message: 'Vui lòng nhập tên tiếng Anh' }]}>
            <Input placeholder="VD: Information Technology" />
          </Form.Item>

          <Form.Item name="department_id" label="Khoa / Bộ môn" rules={[{ required: true, message: 'Vui lòng chọn khoa' }]}>
            <Select
              showSearch
              placeholder="Chọn khoa / bộ môn"
              optionFilterProp="label"
              options={deptData?.results?.map((d) => ({ label: d.name, value: d.id })) ?? []}
            />
          </Form.Item>

          <Form.Item name="degree_level" label="Trình độ đào tạo" rules={[{ required: true }]}>
            <Select
              options={Object.entries(DEGREE_LEVEL_LABELS).map(([k, v]) => ({ value: k, label: v }))}
            />
          </Form.Item>

          <Form.Item name="training_mode" label="Hình thức đào tạo" rules={[{ required: true }]}>
            <Select
              options={Object.entries(TRAINING_MODE_LABELS).map(([k, v]) => ({ value: k, label: v }))}
            />
          </Form.Item>

          <Form.Item name="total_credits" label="Tổng số tín chỉ" rules={[{ required: true, message: 'Vui lòng nhập số tín chỉ' }]}>
            <InputNumber min={1} max={300} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item name="duration_years" label="Thời gian đào tạo (năm)" rules={[{ required: true }]}>
            <InputNumber min={1} max={10} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item name="effective_year" label="Năm áp dụng">
            <InputNumber min={2020} max={2050} style={{ width: '100%' }} placeholder="VD: 2025" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={createProgram.isPending} style={{ marginRight: 8 }}>
              Tạo chương trình
            </Button>
            <Button onClick={() => navigate('/programs')}>Hủy</Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
