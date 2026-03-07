import { Tag } from 'antd';
import {
  PROGRAM_STATUS_LABELS,
  APPROVAL_STATUS_LABELS,
  type ProgramStatus,
  type ApprovalStatus,
} from '@/types/api';

const statusColorMap: Record<string, string> = {
  // program statuses
  draft: 'default',
  review: 'processing',
  approved: 'success',
  active: 'blue',
  archived: 'warning',
  // approval statuses
  pending: 'processing',
  rejected: 'error',
  returned: 'orange',
};

interface StatusTagProps {
  status: ProgramStatus | ApprovalStatus | string;
  /** Optional custom label override */
  label?: string;
}

export default function StatusTag({ status, label }: StatusTagProps) {
  const text =
    label ??
    PROGRAM_STATUS_LABELS[status as ProgramStatus] ??
    APPROVAL_STATUS_LABELS[status as ApprovalStatus] ??
    status;

  const color = statusColorMap[status] ?? 'default';

  return <Tag color={color}>{text}</Tag>;
}
