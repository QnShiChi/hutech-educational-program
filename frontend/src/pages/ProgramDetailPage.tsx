import { useParams } from 'react-router-dom';
import { Tabs, Spin, Result } from 'antd';

import PageHeader from '@/components/PageHeader';
import StatusTag from '@/components/StatusTag';
import { useProgram } from '@/hooks/usePrograms';

import GeneralInfoTab from '@/components/programs/GeneralInfoTab';
import ObjectivesOutcomesTab from '@/components/programs/ObjectivesOutcomesTab';
import CoursesTab from '@/components/programs/CoursesTab';
import CoursePLOMatrix from '@/components/programs/CoursePLOMatrix';
import SemesterPlanTab from '@/components/programs/SemesterPlanTab';
import AssessmentPlanTab from '@/components/programs/AssessmentPlanTab';
import WorkflowTab from '@/components/programs/WorkflowTab';

export default function ProgramDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: program, isLoading, error } = useProgram(id);

  if (isLoading) return <Spin size="large" className="flex justify-center mt-20" />;
  if (error || !program) return <Result status="404" title="Không tìm thấy chương trình đào tạo" />;

  const tabItems = [
    { key: 'general', label: 'Thông tin chung', children: <GeneralInfoTab program={program} /> },
    { key: 'objectives', label: 'Mục tiêu & CĐR', children: <ObjectivesOutcomesTab programId={program.id} /> },
    { key: 'courses', label: 'Khối KT & Học phần', children: <CoursesTab programId={program.id} /> },
    { key: 'matrix', label: 'Ma trận HP-PLO-PI', children: <CoursePLOMatrix programId={program.id} /> },
    { key: 'semester', label: 'Kế hoạch giảng dạy', children: <SemesterPlanTab programId={program.id} /> },
    { key: 'assessment', label: 'Đánh giá PLO', children: <AssessmentPlanTab programId={program.id} /> },
    { key: 'workflow', label: 'Phê duyệt & Lịch sử', children: <WorkflowTab programId={program.id} /> },
  ];

  return (
    <div>
      <PageHeader
        title={program.name}
        subtitle={`${program.code} — v${program.version}`}
        actions={<StatusTag status={program.status} />}
      />
      <Tabs items={tabItems} destroyInactiveTabPane />
    </div>
  );
}
