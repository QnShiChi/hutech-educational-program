import { useState } from 'react';
import { Steps, Button, Space, Spin, Table, Modal, Input, Typography, Divider, Tag } from 'antd';
import { SendOutlined, CheckOutlined, CloseOutlined, HistoryOutlined } from '@ant-design/icons';

import PermissionGuard from '@/components/PermissionGuard';
import {
  useWorkflowStatus,
  useSubmitProgram,
  useApproveProgram,
  useRejectProgram,
  useVersions,
  useRollbackVersion,
} from '@/hooks/useWorkflow';
import { APPROVAL_STATUS_LABELS } from '@/types/api';
import type { WorkflowStep, ProgramVersion } from '@/types/api';

interface Props {
  programId: string;
}

const stepStatusMap: Record<string, 'wait' | 'process' | 'finish' | 'error'> = {
  pending: 'wait',
  approved: 'finish',
  rejected: 'error',
  returned: 'error',
};

export default function WorkflowTab({ programId }: Props) {
  const { data: workflow, isLoading: lw } = useWorkflowStatus(programId);
  const submit = useSubmitProgram(programId);
  const approve = useApproveProgram(programId);
  const reject = useRejectProgram(programId);
  const { data: versions, isLoading: lv } = useVersions(programId);
  const rollback = useRollbackVersion(programId);

  const [rejectOpen, setRejectOpen] = useState(false);
  const [rejectComment, setRejectComment] = useState('');

  if (lw || lv) return <Spin className="flex justify-center mt-10" />;

  const handleReject = async () => {
    if (!rejectComment.trim()) return;
    await reject.mutateAsync({ comment: rejectComment });
    setRejectOpen(false);
    setRejectComment('');
  };

  const workflowSteps = workflow?.steps ?? [];

  const versionColumns = [
    { title: 'Phiên bản', dataIndex: 'version_number', key: 'v', width: 100 },
    { title: 'Ngày tạo', dataIndex: 'created_at', key: 'date', render: (v: string) => new Date(v).toLocaleString('vi-VN') },
    { title: 'Ghi chú', dataIndex: 'comment', key: 'comment', ellipsis: true },
    {
      title: '',
      key: 'actions',
      width: 120,
      render: (_: unknown, record: ProgramVersion) => (
        <PermissionGuard requires="programs.manage_programs">
          <Button size="small" icon={<HistoryOutlined />} onClick={() => rollback.mutate(record.id)}>
            Khôi phục
          </Button>
        </PermissionGuard>
      ),
    },
  ];

  return (
    <div>
      {/* Workflow Actions */}
      <Space className="mb-4">
        <PermissionGuard requires="programs.submit_program">
          <Button type="primary" icon={<SendOutlined />} onClick={() => submit.mutate()} loading={submit.isPending}>
            Gửi phê duyệt
          </Button>
        </PermissionGuard>
        <PermissionGuard requires="programs.approve_program">
          <Button type="primary" style={{ background: '#52c41a' }} icon={<CheckOutlined />} onClick={() => approve.mutate({})} loading={approve.isPending}>
            Phê duyệt
          </Button>
        </PermissionGuard>
        <PermissionGuard requires="programs.approve_program">
          <Button danger icon={<CloseOutlined />} onClick={() => setRejectOpen(true)}>
            Từ chối
          </Button>
        </PermissionGuard>
      </Space>

      {/* Workflow Timeline */}
      {workflowSteps.length > 0 && (
        <div className="mb-6">
          <Typography.Title level={5}>Tiến trình phê duyệt</Typography.Title>
          <Steps
            direction="vertical"
            current={workflow?.current_step ?? 0}
            items={workflowSteps.map((step: WorkflowStep) => ({
              title: step.name,
              status: stepStatusMap[step.status] ?? 'wait',
              description: (
                <div>
                  <Tag>{APPROVAL_STATUS_LABELS[step.status]}</Tag>
                  {step.approver_name && <span> — {step.approver_name}</span>}
                  {step.decided_at && <span> ({new Date(step.decided_at).toLocaleString('vi-VN')})</span>}
                  {step.comment && <div style={{ color: '#888', marginTop: 4 }}>{step.comment}</div>}
                </div>
              ),
            }))}
          />
        </div>
      )}

      <Divider />

      {/* Version History */}
      <Typography.Title level={5}>Lịch sử phiên bản</Typography.Title>
      <Table<ProgramVersion>
        rowKey="id"
        columns={versionColumns}
        dataSource={versions ?? []}
        pagination={{ pageSize: 10 }}
        size="small"
      />

      {/* Reject Modal */}
      <Modal
        title="Từ chối chương trình"
        open={rejectOpen}
        onCancel={() => setRejectOpen(false)}
        onOk={handleReject}
        confirmLoading={reject.isPending}
        okText="Xác nhận từ chối"
        okButtonProps={{ danger: true }}
      >
        <Input.TextArea
          value={rejectComment}
          onChange={(e) => setRejectComment(e.target.value)}
          placeholder="Lý do từ chối (bắt buộc)"
          rows={4}
        />
      </Modal>
    </div>
  );
}
