import { useParams, useNavigate } from 'react-router-dom';
import { Button, Card, Checkbox, Collapse, Form, Input, InputNumber, Spin, Tag } from 'antd';
import { useMemo } from 'react';

import PageHeader from '@/components/PageHeader';
import PermissionGuard from '@/components/PermissionGuard';
import { useRole, useCreateRole, useUpdateRole } from '@/hooks/useRoles';
import { usePermissions } from '@/hooks/usePermissions';
import type { PermissionItem, Role } from '@/types/api';

export default function RoleDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isNew = !id;

  const { data: role, isLoading } = useRole(id);
  const { data: permsData } = usePermissions();
  const createRole = useCreateRole();
  const updateRole = useUpdateRole();

  const [form] = Form.useForm();

  // Group permissions by module
  const permsByModule = useMemo(() => {
    const map: Record<string, PermissionItem[]> = {};
    for (const p of permsData?.results ?? []) {
      const mod = p.module || 'general';
      if (!map[mod]) map[mod] = [];
      map[mod].push(p);
    }
    return map;
  }, [permsData]);

  const handleSave = async (values: Record<string, unknown>) => {
    // Collect checked permission IDs from all modules
    const permissionIds: number[] = [];
    for (const mod of Object.keys(permsByModule)) {
      const checked = values[`perm_${mod}`] as number[] | undefined;
      if (checked) permissionIds.push(...checked);
    }

    const payload: Partial<Role> = {
      code: values.code as string,
      name: values.name as string,
      description: values.description as string,
      level: values.level as number,
      permission_ids: permissionIds,
    };

    if (isNew) {
      await createRole.mutateAsync(payload);
      navigate('/rbac/roles');
    } else {
      await updateRole.mutateAsync({ id: id!, data: payload });
    }
  };

  // Build initial values for permission checkboxes
  const initialValues = useMemo(() => {
    if (!role) return { level: 0 };
    const vals: Record<string, unknown> = {
      code: role.code,
      name: role.name,
      description: role.description,
      level: role.level,
    };
    // For each module, set checked permission IDs
    const rolePermIds = new Set(role.permissions?.map((p) => p.id) ?? []);
    for (const [mod, perms] of Object.entries(permsByModule)) {
      vals[`perm_${mod}`] = perms.filter((p) => rolePermIds.has(p.id)).map((p) => p.id);
    }
    return vals;
  }, [role, permsByModule]);

  const isSystemRole = role?.is_system_role ?? false;

  if (!isNew && isLoading) return <Spin className="flex justify-center mt-12" />;

  return (
    <div>
      <PageHeader
        title={isNew ? 'Tạo vai trò mới' : `Vai trò: ${role?.name ?? ''}`}
        actions={
          <>
            {isSystemRole && <Tag color="purple">Hệ thống</Tag>}
            <Button onClick={() => navigate('/rbac/roles')}>Quay lại</Button>
          </>
        }
      />

      <Form
        form={form}
        layout="vertical"
        initialValues={initialValues}
        onFinish={handleSave}
        key={role?.id ?? 'new'}
      >
        <Card title="Thông tin cơ bản" className="mb-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Form.Item name="code" label="Mã vai trò" rules={[{ required: true }]}>
              <Input disabled={isSystemRole} />
            </Form.Item>
            <Form.Item name="name" label="Tên vai trò" rules={[{ required: true }]}>
              <Input disabled={isSystemRole} />
            </Form.Item>
            <Form.Item name="description" label="Mô tả">
              <Input.TextArea disabled={isSystemRole} />
            </Form.Item>
            <Form.Item name="level" label="Level">
              <InputNumber min={0} max={100} disabled={isSystemRole} />
            </Form.Item>
          </div>
        </Card>

        <Card title="Ma trận quyền">
          <Collapse
            items={Object.entries(permsByModule).map(([mod, perms]) => ({
              key: mod,
              label: <span className="font-medium capitalize">{mod}</span>,
              children: (
                <Form.Item name={`perm_${mod}`} noStyle>
                  <Checkbox.Group disabled={isSystemRole}>
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
                      {perms.map((p) => (
                        <Checkbox key={p.id} value={p.id}>
                          {p.name} <span className="text-gray-400 text-xs">({p.code})</span>
                        </Checkbox>
                      ))}
                    </div>
                  </Checkbox.Group>
                </Form.Item>
              ),
            }))}
          />

          <div className="mt-4">
            <PermissionGuard requires="rbac.manage_roles">
              <Button
                type="primary"
                htmlType="submit"
                loading={createRole.isPending || updateRole.isPending}
                disabled={isSystemRole}
              >
                {isNew ? 'Tạo mới' : 'Cập nhật'}
              </Button>
            </PermissionGuard>
          </div>
        </Card>
      </Form>
    </div>
  );
}
