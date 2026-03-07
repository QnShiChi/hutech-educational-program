import { useParams } from 'react-router-dom';
import PageHeader from '@/components/PageHeader';
import { Typography } from 'antd';

export default function ApprovalDetailPage() {
  const { id } = useParams<{ id: string }>();

  return (
    <div>
      <PageHeader title="Chi tiết Phê duyệt" subtitle={`ID: ${id}`} />
      <Typography.Paragraph>Chi tiết phê duyệt sẽ được triển khai trong giai đoạn tiếp theo.</Typography.Paragraph>
    </div>
  );
}
