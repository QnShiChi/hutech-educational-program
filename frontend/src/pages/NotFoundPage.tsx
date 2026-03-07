import { useNavigate } from 'react-router-dom';
import { Result, Button } from 'antd';

export default function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="flex h-screen items-center justify-center">
      <Result
        status="404"
        title="404"
        subTitle="Trang bạn tìm kiếm không tồn tại."
        extra={
          <Button type="primary" onClick={() => navigate('/')}>
            Về trang chủ
          </Button>
        }
      />
    </div>
  );
}
