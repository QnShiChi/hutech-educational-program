import type { ReactNode } from 'react';
import { Typography, Space, Flex } from 'antd';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  /** Action buttons placed on the right */
  actions?: ReactNode;
}

export default function PageHeader({ title, subtitle, actions }: PageHeaderProps) {
  return (
    <Flex justify="space-between" align="center" className="mb-4">
      <div>
        <Typography.Title level={4} style={{ margin: 0 }}>
          {title}
        </Typography.Title>
        {subtitle && (
          <Typography.Text type="secondary">{subtitle}</Typography.Text>
        )}
      </div>
      {actions && <Space>{actions}</Space>}
    </Flex>
  );
}
