import { Typography } from 'antd';

const { Title, Paragraph } = Typography;

export default function SettingsPage() {
  return (
    <div>
      <Title level={2}>Cài đặt</Title>
      <Paragraph>Cài đặt hệ thống sẽ hiển thị ở đây.</Paragraph>
    </div>
  );
}
