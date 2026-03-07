import { useState, useCallback } from 'react';
import { Table, Select, Button, Space, Spin } from 'antd';
import { SaveOutlined, DownloadOutlined } from '@ant-design/icons';
import * as XLSX from 'xlsx';

import {
  useProgramCourses,
  usePLOs,
  useCoursePLOMatrix,
  useUpdateCoursePLOMatrix,
} from '@/hooks/useProgramDetail';
import type { ContributionLevel, ProgramCourse } from '@/types/api';

interface Props {
  programId: string;
}

const LEVEL_OPTIONS = [
  { value: '', label: '—' },
  { value: 'I', label: 'I' },
  { value: 'T', label: 'T' },
  { value: 'R', label: 'R' },
];

const LEVEL_COLORS: Record<string, string> = {
  I: '#f6ffed',
  T: '#fffbe6',
  R: '#fff7e6',
};

export default function CoursePLOMatrix({ programId }: Props) {
  const { data: courses, isLoading: lc } = useProgramCourses(programId);
  const { data: plos, isLoading: lp } = usePLOs(programId);
  const { data: contributions, isLoading: lm } = useCoursePLOMatrix(programId);
  const updateMatrix = useUpdateCoursePLOMatrix(programId);

  const [dirtyMap, setDirtyMap] = useState<Map<string, ContributionLevel>>(new Map());

  const getLevel = useCallback(
    (courseId: string, piId: string): ContributionLevel => {
      const key = `${courseId}_${piId}`;
      if (dirtyMap.has(key)) return dirtyMap.get(key)!;
      const existing = contributions?.find((c) => c.program_course === courseId && c.pi === piId);
      return existing?.level ?? '';
    },
    [contributions, dirtyMap],
  );

  const setLevel = (courseId: string, piId: string, level: ContributionLevel) => {
    setDirtyMap((prev) => {
      const next = new Map(prev);
      next.set(`${courseId}_${piId}`, level);
      return next;
    });
  };

  const handleSave = async () => {
    if (dirtyMap.size === 0) return;
    const allContributions = [];
    for (const [key, level] of dirtyMap) {
      const [program_course, pi] = key.split('_');
      allContributions.push({ program_course, pi, level });
    }
    try {
      await updateMatrix.mutateAsync({ contributions: allContributions });
      setDirtyMap(new Map());
    } catch {}
  };

  const handleExport = () => {
    if (!courses || !plos) return;
    const header = ['Mã HP', 'Tên HP', ...plos.map((p) => p.code)];
    const rows = courses.map((pc) => [
      pc.course.code,
      pc.course.name,
      ...plos.map((plo) => getLevel(pc.id, plo.id) || ''),
    ]);
    const ws = XLSX.utils.aoa_to_sheet([header, ...rows]);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Matrix');
    XLSX.writeFile(wb, 'ma-tran-hp-plo.xlsx');
  };

  if (lc || lp || lm) return <Spin className="flex justify-center mt-10" />;
  if (!courses || !plos) return null;

  // Build columns: PLO groups with PI sub-columns
  // Since we may not have separate PI data, use contributions to infer PI per PLO
  const ploColumns = plos.map((plo) => {
    return {
      title: plo.code,
      key: plo.id,
      width: 70,
      align: 'center' as const,
      render: (_: unknown, record: ProgramCourse) => {
        const level = getLevel(record.id, plo.id);
        return (
          <Select
            value={level}
            onChange={(v) => setLevel(record.id, plo.id, v as ContributionLevel)}
            options={LEVEL_OPTIONS}
            size="small"
            style={{ width: 55, backgroundColor: LEVEL_COLORS[level] || 'transparent' }}
            variant="borderless"
          />
        );
      },
    };
  });

  const columns = [
    { title: 'Mã HP', key: 'code', fixed: 'left' as const, width: 100, render: (_: unknown, r: ProgramCourse) => r.course.code },
    { title: 'Tên HP', key: 'name', fixed: 'left' as const, width: 200, ellipsis: true, render: (_: unknown, r: ProgramCourse) => r.course.name },
    ...ploColumns,
  ];

  return (
    <div>
      <Space className="mb-3">
        <Button type="primary" icon={<SaveOutlined />} onClick={handleSave} loading={updateMatrix.isPending} disabled={dirtyMap.size === 0}>
          Lưu thay đổi ({dirtyMap.size})
        </Button>
        <Button icon={<DownloadOutlined />} onClick={handleExport}>
          Xuất Excel
        </Button>
      </Space>

      <Table<ProgramCourse>
        rowKey="id"
        columns={columns}
        dataSource={courses}
        pagination={false}
        size="small"
        bordered
        scroll={{ x: 'max-content', y: 500 }}
        sticky
      />
    </div>
  );
}
