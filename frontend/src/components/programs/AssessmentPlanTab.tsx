import { useState, useMemo } from 'react';
import { Table, Input, Select, Button, Spin, Space } from 'antd';
import { SaveOutlined } from '@ant-design/icons';

import {
  useAssessmentPlans,
  useBulkUpsertAssessmentPlans,
  usePLOs,
  useProgramCourses,
} from '@/hooks/useProgramDetail';
import type { PLOAssessmentPlan, ProgramLearningOutcome } from '@/types/api';

interface Props {
  programId: string;
}

export default function AssessmentPlanTab({ programId }: Props) {
  const { data: plans, isLoading: lp } = useAssessmentPlans(programId);
  const { data: plos, isLoading: lplo } = usePLOs(programId);
  const { data: courses } = useProgramCourses(programId);
  const bulkSave = useBulkUpsertAssessmentPlans(programId);

  const [editedRows, setEditedRows] = useState<Map<string, Partial<PLOAssessmentPlan>>>(new Map());

  if (lp || lplo) return <Spin className="flex justify-center mt-10" />;

  const updateField = (id: string, field: string, value: string) => {
    setEditedRows((prev) => {
      const next = new Map(prev);
      const existing = next.get(id) ?? {};
      next.set(id, { ...existing, [field]: value });
      return next;
    });
  };

  const getFieldValue = (plan: PLOAssessmentPlan, field: keyof PLOAssessmentPlan) => {
    const edited = editedRows.get(plan.id);
    if (edited && field in edited) return edited[field] as string;
    return plan[field] as string;
  };

  const handleSave = async () => {
    const mergedPlans = (plans ?? []).map((p) => {
      const edits = editedRows.get(p.id);
      return edits ? { ...p, ...edits } : p;
    });
    await bulkSave.mutateAsync({ plans: mergedPlans });
    setEditedRows(new Map());
  };

  const courseOptions = courses?.map((pc) => ({
    value: pc.id,
    label: `${pc.course.code} — ${pc.course.name}`,
  })) ?? [];

  const ploMap = useMemo(() => {
    const map = new Map<string, ProgramLearningOutcome>();
    (plos ?? []).forEach((p) => map.set(p.id, p));
    return map;
  }, [plos]);

  const columns = [
    {
      title: 'PLO',
      key: 'plo',
      width: 80,
      render: (_: unknown, r: PLOAssessmentPlan) => ploMap.get(r.plo)?.code ?? r.plo,
    },
    {
      title: 'HP lấy mẫu',
      key: 'sample_course',
      width: 200,
      render: (_: unknown, r: PLOAssessmentPlan) => (
        <Select
          value={getFieldValue(r, 'sample_course') || undefined}
          onChange={(v) => updateField(r.id, 'sample_course', v)}
          options={courseOptions}
          size="small"
          allowClear
          style={{ width: '100%' }}
          showSearch
          optionFilterProp="label"
        />
      ),
    },
    {
      title: 'Minh chứng',
      key: 'evidence',
      render: (_: unknown, r: PLOAssessmentPlan) => (
        <Input
          value={getFieldValue(r, 'evidence')}
          onChange={(e) => updateField(r.id, 'evidence', e.target.value)}
          size="small"
        />
      ),
    },
    {
      title: 'Công cụ',
      key: 'tool',
      render: (_: unknown, r: PLOAssessmentPlan) => (
        <Input
          value={getFieldValue(r, 'tool')}
          onChange={(e) => updateField(r.id, 'tool', e.target.value)}
          size="small"
        />
      ),
    },
    {
      title: 'Tiêu chuẩn',
      key: 'standard',
      render: (_: unknown, r: PLOAssessmentPlan) => (
        <Input
          value={getFieldValue(r, 'standard')}
          onChange={(e) => updateField(r.id, 'standard', e.target.value)}
          size="small"
        />
      ),
    },
    {
      title: 'Lịch',
      key: 'schedule',
      width: 120,
      render: (_: unknown, r: PLOAssessmentPlan) => (
        <Input
          value={getFieldValue(r, 'schedule')}
          onChange={(e) => updateField(r.id, 'schedule', e.target.value)}
          size="small"
        />
      ),
    },
  ];

  return (
    <div>
      <Space className="mb-3">
        <Button
          type="primary"
          icon={<SaveOutlined />}
          onClick={handleSave}
          loading={bulkSave.isPending}
          disabled={editedRows.size === 0}
        >
          Lưu tất cả ({editedRows.size} thay đổi)
        </Button>
      </Space>

      <Table<PLOAssessmentPlan>
        rowKey="id"
        columns={columns}
        dataSource={plans ?? []}
        pagination={false}
        size="small"
        bordered
        scroll={{ x: 'max-content' }}
      />
    </div>
  );
}
