import { useMemo } from 'react';
import { Table, Checkbox, Button, message } from 'antd';
import { SaveOutlined } from '@ant-design/icons';
import { useState } from 'react';
import type { ProgramObjective, ProgramLearningOutcome } from '@/types/api';

interface CheckboxMatrixProps {
  objectives: ProgramObjective[];
  plos: ProgramLearningOutcome[];
  mappings: { po_id: string; plo_id: string }[];
  onSave: (mappings: { po_id: string; plo_id: string }[]) => Promise<void>;
  readOnly?: boolean;
}

export default function CheckboxMatrix({
  objectives,
  plos,
  mappings: initialMappings,
  onSave,
  readOnly = false,
}: CheckboxMatrixProps) {
  const [dirty, setDirty] = useState(false);
  const [saving, setSaving] = useState(false);
  const [localMappings, setLocalMappings] = useState(initialMappings);

  const mappingSet = useMemo(() => {
    const s = new Set<string>();
    localMappings.forEach(({ po_id, plo_id }) => s.add(`${po_id}_${plo_id}`));
    return s;
  }, [localMappings]);

  const toggleCell = (poId: string, ploId: string) => {
    if (readOnly) return;
    const key = `${poId}_${ploId}`;
    let newMappings: { po_id: string; plo_id: string }[];
    if (mappingSet.has(key)) {
      newMappings = localMappings.filter((m) => !(m.po_id === poId && m.plo_id === ploId));
    } else {
      newMappings = [...localMappings, { po_id: poId, plo_id: ploId }];
    }
    setLocalMappings(newMappings);
    setDirty(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(localMappings);
      setDirty(false);
    } catch {
      message.error('Lỗi lưu ma trận');
    } finally {
      setSaving(false);
    }
  };

  const columns = [
    {
      title: 'PO \\ PLO',
      dataIndex: 'code',
      key: 'code',
      fixed: 'left' as const,
      width: 100,
    },
    ...plos.map((plo) => ({
      title: plo.code,
      key: plo.id,
      width: 60,
      align: 'center' as const,
      render: (_: unknown, record: ProgramObjective) => (
        <Checkbox
          checked={mappingSet.has(`${record.id}_${plo.id}`)}
          onChange={() => toggleCell(record.id, plo.id)}
          disabled={readOnly}
        />
      ),
    })),
  ];

  return (
    <div>
      <div className="mb-2 flex justify-between items-center">
        <strong>Ma trận PO-PLO</strong>
        {!readOnly && dirty && (
          <Button type="primary" size="small" icon={<SaveOutlined />} onClick={handleSave} loading={saving}>
            Lưu ma trận
          </Button>
        )}
      </div>
      <Table
        rowKey="id"
        columns={columns}
        dataSource={[...objectives].sort((a, b) => a.order - b.order)}
        pagination={false}
        size="small"
        bordered
        scroll={{ x: 'max-content' }}
      />
    </div>
  );
}
