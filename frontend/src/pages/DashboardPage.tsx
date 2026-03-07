import { Typography } from 'antd';

const { Title, Paragraph } = Typography;

export default function DashboardPage() {
  return (
    <div>
      <Title level={2}>Dashboard</Title>
      <Paragraph>
        Chào mừng đến với hệ thống quản lý Chương trình Đào tạo HUTECH.
      </Paragraph>
    </div>
  );
}
