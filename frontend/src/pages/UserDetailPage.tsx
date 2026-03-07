import { useParams, useNavigate } from 'react-router-dom';
import { Button, Card, Form, Input, Select, Switch, Table, Modal, Spin } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { useState } from 'react';

import PageHeader from '@/components/PageHeader';
import PermissionGuard from '@/components/PermissionGuard';
import { confirmModal } from '@/components/ConfirmModal';
import { useUser, useCreateUser, useUpdateUser, useAssignRole, useRemoveRole } from '@/hooks/useUsers';
import { useRoles } from '@/hooks/useRoles';
import { useDepartments } from '@/hooks/useDepartments';
import type { UserRole } from '@/types/api';

export default function UserDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isNew = !id;

  const { data: user, isLoading } = useUser(id);
  const createUser = useCreateUser();
  const updateUser = useUpdateUser();
  const assignRole = useAssignRole();
  const removeRole = useRemoveRole();

  const { data: rolesData } = useRoles({ page_size: 100 });
  const { data: deptsData } = useDepartments({ page_size: 200 });

  const [form] = Form.useForm();
  const [assignModal, setAssignModal] = useState(false);
  const [assignForm] = Form.useForm();

  const handleSave = async (values: Record<string, unknown>) => {
    if (isNew) {
      await createUser.mutateAsync(values);
      navigate('/rbac/users');
    } else {
      await updateUser.mutateAsync({ id: id!, data: values });
    }
  };

  const handleAssign = async (values: { role: string; department?: string }) => {
    await assignRole.mutateAsync({ userId: id!, data: values });
    setAssignModal(false);
    assignForm.resetFields();
  };

  const handleRemoveRole = (roleId: string) => {
    confirmModal({
      content: 'Xóa vai trò này khỏi người dùng?',
      danger: true,
      onOk: async () => { await removeRole.mutateAsync({ userId: id!, roleId }); },
    });
  };

  const roleColumns = [
    { title: 'Vai trò', dataIndex: 'role_name', key: 'role_name' },
    { title: 'Đơn vị', dataIndex: 'department_name', key: 'department_name' },
    { title: 'Ngày gán', dataIndex: 'created_at', key: 'created_at', render: (d: string) => new Date(d).toLocaleDateString('vi-VN') },
    {
      title: 'Hành động',
      key: 'actions',
      render: (_: unknown, record: UserRole) => (
        <PermissionGuard requires="rbac.manage_users">
          <Button type="link" danger icon={<DeleteOutlined />} onClick={() => handleRemoveRole(record.id)}>
            Xóa
          </Button>
        </PermissionGuard>
      ),
    },
  ];

  if (!isNew && isLoading) return <Spin className="flex justify-center mt-12" />;

  return (
    <div>
      <PageHeader
        title={isNew ? 'Tạo người dùng mới' : `Chỉnh sửa: ${user?.name || user?.username}`}
        actions={
          <Button onClick={() => navigate('/rbac/users')}>Quay lại</Button>
        }
      />

      <Card title="Thông tin cá nhân" className="mb-4">
        <Form
          form={form}
          layout="vertical"
          initialValues={isNew ? { is_active: true } : user}
          onFinish={handleSave}
          key={user?.id ?? 'new'}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Form.Item name="username" label="Tên đăng nhập" rules={[{ required: true }]}>
              <Input disabled={!isNew} />
            </Form.Item>
            <Form.Item name="email" label="Email" rules={[{ required: true, type: 'email' }]}>
              <Input />
            </Form.Item>
            <Form.Item name="first_name" label="Họ">
              <Input />
            </Form.Item>
            <Form.Item name="last_name" label="Tên">
              <Input />
            </Form.Item>
            <Form.Item name="employee_id" label="Mã nhân viên">
              <Input />
            </Form.Item>
            <Form.Item name="phone" label="Số điện thoại">
              <Input />
            </Form.Item>
            <Form.Item name="department_id" label="Đơn vị">
              <Select
                allowClear
                placeholder="Chọn đơn vị"
                options={deptsData?.results?.map((d) => ({ label: d.name, value: d.id })) ?? []}
              />
            </Form.Item>
            <Form.Item name="is_active" label="Trạng thái" valuePropName="checked">
              <Switch checkedChildren="Hoạt động" unCheckedChildren="Vô hiệu" />
            </Form.Item>
          </div>
          {isNew && (
            <Form.Item name="password" label="Mật khẩu" rules={[{ required: true, min: 8 }]}>
              <Input.Password />
            </Form.Item>
          )}
          <PermissionGuard requires="rbac.manage_users">
            <Button type="primary" htmlType="submit" loading={createUser.isPending || updateUser.isPending}>
              {isNew ? 'Tạo mới' : 'Cập nhật'}
            </Button>
          </PermissionGuard>
        </Form>
      </Card>

      {!isNew && (
        <Card
          title="Vai trò"
          extra={
            <PermissionGuard requires="rbac.manage_users">
              <Button type="primary" icon={<PlusOutlined />} onClick={() => setAssignModal(true)}>
                Gán vai trò
              </Button>
            </PermissionGuard>
          }
        >
          <Table<UserRole>
            rowKey="id"
            columns={roleColumns}
            dataSource={(user as unknown as Record<string, unknown>)?.user_roles as UserRole[] | undefined}
            pagination={false}
            size="small"
          />
        </Card>
      )}

      {/* Assign role modal */}
      <Modal
        title="Gán vai trò"
        open={assignModal}
        onCancel={() => { setAssignModal(false); assignForm.resetFields(); }}
        onOk={() => assignForm.submit()}
        confirmLoading={assignRole.isPending}
      >
        <Form form={assignForm} layout="vertical" onFinish={handleAssign}>
          <Form.Item name="role" label="Vai trò" rules={[{ required: true, message: 'Chọn vai trò' }]}>
            <Select
              placeholder="Chọn vai trò"
              options={rolesData?.results?.map((r) => ({ label: r.name, value: r.id })) ?? []}
            />
          </Form.Item>
          <Form.Item name="department" label="Phạm vi đơn vị">
            <Select
              allowClear
              placeholder="Toàn hệ thống"
              options={deptsData?.results?.map((d) => ({ label: d.name, value: d.id })) ?? []}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
