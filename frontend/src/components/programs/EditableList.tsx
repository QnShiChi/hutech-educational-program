import { useState } from 'react';
import { List, Button, Input, Space, Form, Popconfirm, Select } from 'antd';
import { PlusOutlined, DeleteOutlined, EditOutlined, SaveOutlined, CloseOutlined, HolderOutlined } from '@ant-design/icons';
import { DndContext, closestCenter, type DragEndEvent } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy, useSortable, arrayMove } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

import PermissionGuard from '@/components/PermissionGuard';

export interface EditableItem {
  id: string;
  code: string;
  description: string;
  order: number;
  bloom_level?: string;
}

interface EditableListProps {
  title: string;
  items: EditableItem[];
  showBloom?: boolean;
  onCreate: (data: Partial<EditableItem>) => Promise<void>;
  onUpdate: (id: string, data: Partial<EditableItem>) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  onReorder: (ids: string[]) => Promise<void>;
  permission: string;
}

function SortableItem({
  item,
  showBloom,
  onEdit,
  onDelete,
  permission,
}: {
  item: EditableItem;
  showBloom?: boolean;
  onEdit: (item: EditableItem) => void;
  onDelete: (id: string) => void;
  permission: string;
}) {
  const { attributes, listeners, setNodeRef, transform, transition } = useSortable({ id: item.id });
  const style = { transform: CSS.Transform.toString(transform), transition };

  return (
    <List.Item ref={setNodeRef} style={style} {...attributes}>
      <Space style={{ width: '100%' }}>
        <PermissionGuard requires={permission}>
          <HolderOutlined {...listeners} style={{ cursor: 'grab', color: '#999' }} />
        </PermissionGuard>
        <strong>{item.code}</strong>
        <span>{item.description}</span>
        {showBloom && item.bloom_level && <span style={{ color: '#888' }}>({item.bloom_level})</span>}
      </Space>
      <PermissionGuard requires={permission}>
        <Space>
          <Button type="link" size="small" icon={<EditOutlined />} onClick={() => onEdit(item)} />
          <Popconfirm title="Xóa mục này?" onConfirm={() => onDelete(item.id)}>
            <Button type="link" size="small" danger icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      </PermissionGuard>
    </List.Item>
  );
}

export default function EditableList({
  title,
  items,
  showBloom,
  onCreate,
  onUpdate,
  onDelete,
  onReorder,
  permission,
}: EditableListProps) {
  const [adding, setAdding] = useState(false);
  const [editingItem, setEditingItem] = useState<EditableItem | null>(null);
  const [form] = Form.useForm();

  const handleAdd = async () => {
    try {
      const values = await form.validateFields();
      await onCreate(values);
      form.resetFields();
      setAdding(false);
    } catch {
      // validation error
    }
  };

  const handleUpdate = async () => {
    if (!editingItem) return;
    try {
      const values = await form.validateFields();
      await onUpdate(editingItem.id, values);
      setEditingItem(null);
      form.resetFields();
    } catch {
      // validation error
    }
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over || active.id === over.id) return;
    const oldIndex = items.findIndex((i) => i.id === active.id);
    const newIndex = items.findIndex((i) => i.id === over.id);
    const reordered = arrayMove(items, oldIndex, newIndex);
    onReorder(reordered.map((i) => i.id));
  };

  const startEdit = (item: EditableItem) => {
    setEditingItem(item);
    setAdding(false);
    form.setFieldsValue(item);
  };

  const sortedItems = [...items].sort((a, b) => a.order - b.order);

  return (
    <div className="mb-6">
      <Space className="mb-2">
        <strong>{title}</strong>
        <PermissionGuard requires={permission}>
          <Button size="small" icon={<PlusOutlined />} onClick={() => { setAdding(true); setEditingItem(null); form.resetFields(); }}>
            Thêm
          </Button>
        </PermissionGuard>
      </Space>

      {(adding || editingItem) && (
        <Form form={form} layout="inline" className="mb-2">
          <Form.Item name="code" rules={[{ required: true, message: 'Nhập mã' }]}>
            <Input placeholder="Mã" style={{ width: 100 }} />
          </Form.Item>
          <Form.Item name="description" rules={[{ required: true, message: 'Nhập mô tả' }]}>
            <Input placeholder="Mô tả" style={{ width: 300 }} />
          </Form.Item>
          {showBloom && (
            <Form.Item name="bloom_level">
              <Select placeholder="Bloom" style={{ width: 140 }} allowClear
                options={['Nhớ', 'Hiểu', 'Áp dụng', 'Phân tích', 'Đánh giá', 'Sáng tạo'].map((b) => ({ value: b, label: b }))}
              />
            </Form.Item>
          )}
          <Form.Item>
            <Button type="primary" size="small" icon={<SaveOutlined />} onClick={editingItem ? handleUpdate : handleAdd}>
              {editingItem ? 'Cập nhật' : 'Thêm'}
            </Button>
          </Form.Item>
          <Form.Item>
            <Button size="small" icon={<CloseOutlined />} onClick={() => { setAdding(false); setEditingItem(null); form.resetFields(); }}>
              Hủy
            </Button>
          </Form.Item>
        </Form>
      )}

      <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <SortableContext items={sortedItems.map((i) => i.id)} strategy={verticalListSortingStrategy}>
          <List
            bordered
            size="small"
            dataSource={sortedItems}
            renderItem={(item) => (
              <SortableItem
                key={item.id}
                item={item}
                showBloom={showBloom}
                onEdit={startEdit}
                onDelete={(id) => onDelete(id)}
                permission={permission}
              />
            )}
          />
        </SortableContext>
      </DndContext>
    </div>
  );
}
