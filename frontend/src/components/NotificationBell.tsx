import { useState } from 'react';
import { Badge, Dropdown, List, Button, Empty, Typography, Spin } from 'antd';
import { BellOutlined } from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/services/apiClient';
import type { PaginatedResponse, Notification } from '@/types/api';

export default function NotificationBell() {
  const [open, setOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: ['notifications', { is_read: false }],
    queryFn: () =>
      apiClient
        .get<PaginatedResponse<Notification>>('/notifications/', {
          params: { is_read: false, page_size: 10 },
        })
        .then((r) => r.data),
    refetchInterval: 30_000, // poll every 30s
  });

  const markRead = useMutation({
    mutationFn: (id: string) => apiClient.patch(`/notifications/${id}/`, { is_read: true }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notifications'] }),
  });

  const unreadCount = data?.count ?? 0;

  const menu = (
    <div className="w-80 max-h-96 overflow-auto rounded-lg bg-white shadow-lg border border-gray-200">
      <div className="p-3 border-b flex justify-between items-center">
        <Typography.Text strong>Thông báo</Typography.Text>
        {unreadCount > 0 && (
          <Typography.Text type="secondary" className="text-xs">
            {unreadCount} chưa đọc
          </Typography.Text>
        )}
      </div>
      {isLoading ? (
        <div className="p-6 text-center"><Spin /></div>
      ) : !data?.results.length ? (
        <Empty description="Không có thông báo" className="py-6" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      ) : (
        <List
          dataSource={data.results}
          renderItem={(item) => (
            <List.Item
              className="px-3 cursor-pointer hover:bg-gray-50"
              onClick={() => markRead.mutate(item.id)}
            >
              <List.Item.Meta
                title={<Typography.Text className="text-sm">{item.title}</Typography.Text>}
                description={
                  <Typography.Text type="secondary" className="text-xs">
                    {item.message}
                  </Typography.Text>
                }
              />
            </List.Item>
          )}
        />
      )}
    </div>
  );

  return (
    <Dropdown
      dropdownRender={() => menu}
      trigger={['click']}
      open={open}
      onOpenChange={setOpen}
      placement="bottomRight"
    >
      <Button type="text" icon={<Badge count={unreadCount} size="small"><BellOutlined className="text-lg" /></Badge>} />
    </Dropdown>
  );
}
