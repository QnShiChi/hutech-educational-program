import { useState, useMemo } from 'react';
import { Card, Row, Col, Button, Spin, Badge, Tooltip } from 'antd';
import { SaveOutlined, WarningOutlined } from '@ant-design/icons';
import { DndContext, closestCenter, type DragEndEvent } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy, useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';

import { useProgramCourses, useSemesterPlan, useUpdateSemesterPlan } from '@/hooks/useProgramDetail';
import type { ProgramCourse, SemesterPlanEntry } from '@/types/api';

interface Props {
  programId: string;
}

const SEMESTERS = [1, 2, 3, 4, 5, 6, 7, 8];

function CourseCard({ course, hasWarning }: { course: ProgramCourse; hasWarning?: boolean }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: course.id,
    data: { semester: course.semester },
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
    cursor: 'grab',
    padding: '4px 8px',
    margin: '4px 0',
    background: '#fafafa',
    borderRadius: 4,
    border: '1px solid #d9d9d9',
    fontSize: 12,
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span><strong>{course.course.code}</strong> — {course.course.name}</span>
        {hasWarning && (
          <Tooltip title="Học phần tiên quyết chưa được xếp trước">
            <WarningOutlined style={{ color: '#faad14' }} />
          </Tooltip>
        )}
      </div>
      <span style={{ color: '#888' }}>{course.course.credits} TC</span>
    </div>
  );
}

export default function SemesterPlanTab({ programId }: Props) {
  const { data: courses, isLoading: lc } = useProgramCourses(programId);
  const { data: planData, isLoading: lp } = useSemesterPlan(programId);
  const updatePlan = useUpdateSemesterPlan(programId);

  const [localPlan, setLocalPlan] = useState<SemesterPlanEntry[]>([]);
  const [dirty, setDirty] = useState(false);

  // Initialize from plan data
  useMemo(() => {
    if (planData?.plan) {
      setLocalPlan(planData.plan);
    }
  }, [planData]);

  if (lc || lp) return <Spin className="flex justify-center mt-10" />;
  if (!courses) return null;

  const getSemester = (courseId: string) =>
    localPlan.find((p) => p.course_id === courseId)?.semester ??
    courses.find((c) => c.id === courseId)?.semester ??
    0;

  const coursesBySemester = (sem: number) =>
    courses.filter((c) => getSemester(c.id) === sem);

  const unassigned = courses.filter((c) => getSemester(c.id) === 0 || !localPlan.some((p) => p.course_id === c.id));

  const creditsForSemester = (sem: number) =>
    coursesBySemester(sem).reduce((s, c) => s + c.course.credits, 0);

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    if (!over) return;
    const courseId = active.id as string;
    const targetSemester = Number(over.id);
    if (isNaN(targetSemester)) return;

    setLocalPlan((prev) => {
      const next = prev.filter((p) => p.course_id !== courseId);
      next.push({ course_id: courseId, semester: targetSemester });
      return next;
    });
    setDirty(true);
  };

  const handleSave = async () => {
    await updatePlan.mutateAsync({ plan: localPlan });
    setDirty(false);
  };

  return (
    <div>
      <div className="mb-3 flex justify-between">
        <strong>Kế hoạch giảng dạy theo học kỳ</strong>
        {dirty && (
          <Button type="primary" icon={<SaveOutlined />} onClick={handleSave} loading={updatePlan.isPending}>
            Lưu kế hoạch
          </Button>
        )}
      </div>

      <DndContext collisionDetection={closestCenter} onDragEnd={handleDragEnd}>
        <Row gutter={[8, 8]}>
          {SEMESTERS.map((sem) => (
            <Col key={sem} span={3}>
              <Card
                title={`HK ${sem}`}
                size="small"
                extra={<Badge count={creditsForSemester(sem)} style={{ backgroundColor: '#1677ff' }} overflowCount={999} />}
                style={{ minHeight: 300 }}
              >
                <SortableContext
                  id={String(sem)}
                  items={coursesBySemester(sem).map((c) => c.id)}
                  strategy={verticalListSortingStrategy}
                >
                  <div id={String(sem)} style={{ minHeight: 50 }}>
                    {coursesBySemester(sem).map((c) => (
                      <CourseCard key={c.id} course={c} />
                    ))}
                  </div>
                </SortableContext>
              </Card>
            </Col>
          ))}
        </Row>

        {unassigned.length > 0 && (
          <Card title="Chưa xếp lịch" size="small" className="mt-4">
            <Row gutter={[8, 8]}>
              {unassigned.map((c) => (
                <Col key={c.id} span={6}>
                  <CourseCard course={c} />
                </Col>
              ))}
            </Row>
          </Card>
        )}
      </DndContext>
    </div>
  );
}
