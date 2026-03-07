import { useState, useCallback, useMemo } from 'react';
import { Button, Drawer, Form, Input, Select, Tree, Spin, Empty } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import type { DataNode, TreeProps } from 'antd/es/tree';

import PageHeader from '@/components/PageHeader';
import PermissionGuard from '@/components/PermissionGuard';
import { confirmModal } from '@/components/ConfirmModal';
import { useDepartmentTree, useCreateDepartment, useUpdateDepartment, useDeleteDepartment } from '@/hooks/useDepartments';
import type { DepartmentTree } from '@/types/api';

const DEPARTMENT_TYPES = [
  { label: 'Trường', value: 'truong' },
  { label: 'Khoa', value: 'khoa' },
  { label: 'Phòng ban', value: 'phong_ban' },
  { label: 'Bộ môn', value: 'bo_mon' },
  { label: 'Trung tâm', value: 'trung_tam' },
];

function toTreeData(nodes: DepartmentTree[]): DataNode[] {
  return nodes.map((n) => ({
    key: n.id,
    title: (
      <span>
        {n.name} <span className="text-gray-400 text-xs">({n.code})</span>
        {!n.is_active && <span className="text-red-400 text-xs ml-1">[Vô hiệu]</span>}
      </span>
    ),
    children: n.children?.length ? toTreeData(n.children) : undefined,
    // store raw data for editing
    rawData: n,
  }));
}

function findNode(nodes: DepartmentTree[], id: string): DepartmentTree | null {
  for (const n of nodes) {
    if (n.id === id) return n;
    if (n.children?.length) {
      const found = findNode(n.children, id);
      if (found) return found;
    }
  }
  return null;
}

export default function DepartmentsPage() {
  const { data: treeData, isLoading } = useDepartmentTree();
  const createDept = useCreateDepartment();
  const updateDept = useUpdateDepartment();
  const deleteDept = useDeleteDepartment();

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editId, setEditId] = useState<string | null>(null);
  const [parentId, setParentId] = useState<string | null>(null);
  const [selectedKey, setSelectedKey] = useState<string | null>(null);
  const [form] = Form.useForm();

  const treeNodes = useMemo(() => toTreeData(treeData ?? []), [treeData]);

  // Build flat list for TreeSelect options
  const flattenTree = useCallback((nodes: DepartmentTree[], prefix = ''): { label: string; value: string }[] => {
    const result: { label: string; value: string }[] = [];
    for (const n of nodes) {
      result.push({ label: prefix + n.name, value: n.id });
      if (n.children?.length) {
        result.push(...flattenTree(n.children, prefix + '  '));
      }
    }
    return result;
  }, []);

  const parentOptions = useMemo(() => flattenTree(treeData ?? []), [treeData, flattenTree]);

  const openCreate = (parentKey?: string) => {
    setEditId(null);
    setParentId(parentKey ?? null);
    form.resetFields();
    form.setFieldsValue({ parent: parentKey ?? null, is_active: true });
    setDrawerOpen(true);
  };

  const openEdit = (id: string) => {
    const node = findNode(treeData ?? [], id);
    if (!node) return;
    setEditId(id);
    setParentId(null);
    form.setFieldsValue({
      code: node.code,
      name: node.name,
      name_en: node.name_en,
      type: node.type,
      parent: null, // parent is removed in DepartmentTree type
      is_active: node.is_active,
    });
    setDrawerOpen(true);
  };

  const handleDelete = (id: string) => {
    confirmModal({
      content: 'Xóa đơn vị này? Các đơn vị con cũng sẽ bị ảnh hưởng.',
      danger: true,
      onOk: async () => { await deleteDept.mutateAsync(id); },
    });
  };

  const handleSave = async (values: Record<string, unknown>) => {
    if (editId) {
      await updateDept.mutateAsync({ id: editId, data: values });
    } else {
      await createDept.mutateAsync({ ...values, parent: (parentId ?? values.parent) as string | null });
    }
    setDrawerOpen(false);
    form.resetFields();
  };

  const onSelect: TreeProps['onSelect'] = (keys) => {
    setSelectedKey(keys[0] as string ?? null);
  };

  if (isLoading) return <Spin className="flex justify-center mt-12" />;

  return (
    <div>
      <PageHeader
        title="Khoa / Phòng ban"
        subtitle="Cơ cấu tổ chức"
        actions={
          <PermissionGuard requires="rbac.manage_departments">
            <Button type="primary" icon={<PlusOutlined />} onClick={() => openCreate()}>
              Tạo đơn vị
            </Button>
          </PermissionGuard>
        }
      />

      <div className="flex gap-4 mb-4">
        <PermissionGuard requires="rbac.manage_departments">
          {selectedKey && (
            <>
              <Button icon={<PlusOutlined />} onClick={() => openCreate(selectedKey)}>
                Tạo đơn vị con
              </Button>
              <Button icon={<EditOutlined />} onClick={() => openEdit(selectedKey)}>
                Sửa
              </Button>
              <Button danger icon={<DeleteOutlined />} onClick={() => handleDelete(selectedKey)}>
                Xóa
              </Button>
            </>
          )}
        </PermissionGuard>
      </div>

      {treeNodes.length > 0 ? (
        <Tree
          showLine
          defaultExpandAll
          treeData={treeNodes}
          onSelect={onSelect}
          selectedKeys={selectedKey ? [selectedKey] : []}
        />
      ) : (
        <Empty description="Chưa có đơn vị nào" />
      )}

      <Drawer
        title={editId ? 'Chỉnh sửa đơn vị' : 'Tạo đơn vị mới'}
        open={drawerOpen}
        onClose={() => { setDrawerOpen(false); form.resetFields(); }}
        width={400}
        extra={
          <Button type="primary" onClick={() => form.submit()} loading={createDept.isPending || updateDept.isPending}>
            {editId ? 'Cập nhật' : 'Tạo mới'}
          </Button>
        }
      >
        <Form form={form} layout="vertical" onFinish={handleSave}>
          <Form.Item name="code" label="Mã đơn vị" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="name" label="Tên đơn vị" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="name_en" label="Tên tiếng Anh">
            <Input />
          </Form.Item>
          <Form.Item name="type" label="Loại" rules={[{ required: true }]}>
            <Select options={DEPARTMENT_TYPES} />
          </Form.Item>
          <Form.Item name="parent" label="Đơn vị cha">
            <Select allowClear placeholder="Không (Gốc)" options={parentOptions} />
          </Form.Item>
        </Form>
      </Drawer>
    </div>
  );
}
