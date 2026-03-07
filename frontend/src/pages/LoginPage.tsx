import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, Typography, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import apiClient from '@/services/apiClient';
import { useAuthStore } from '@/store/authStore';
import type { User, TokenPair } from '@/types/api';

const { Title } = Typography;

export default function LoginPage() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const { setTokens, setUser } = useAuthStore();

  const onFinish = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      // 1. Get tokens
      const { data: tokens } = await apiClient.post<TokenPair>('/auth/token/', values);
      setTokens(tokens.access, tokens.refresh);

      // 2. Fetch user profile + permissions
      const { data: user } = await apiClient.get<User>('/rbac/users/me/', {
        headers: { Authorization: `Bearer ${tokens.access}` },
      });
      setUser(user);

      message.success(`Xin chào, ${user.name || user.username}!`);
      navigate('/');
    } catch {
      message.error('Sai tên đăng nhập hoặc mật khẩu');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <Card className="w-96 shadow-lg">
        <div className="text-center mb-6">
          <Title level={3} style={{ color: '#003399', marginBottom: 4 }}>
            HUTECH Program
          </Title>
          <Typography.Text type="secondary">
            Hệ thống quản lý Chương trình Đào tạo
          </Typography.Text>
        </div>
        <Form onFinish={onFinish} autoComplete="off" size="large">
          <Form.Item
            name="username"
            rules={[{ required: true, message: 'Vui lòng nhập tên đăng nhập' }]}
          >
            <Input prefix={<UserOutlined />} placeholder="Tên đăng nhập" />
          </Form.Item>
          <Form.Item
            name="password"
            rules={[{ required: true, message: 'Vui lòng nhập mật khẩu' }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Mật khẩu" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              Đăng nhập
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
