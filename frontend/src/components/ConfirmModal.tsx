import { Modal } from 'antd';
import { ExclamationCircleOutlined } from '@ant-design/icons';

interface ConfirmModalOptions {
  title?: string;
  content: string;
  onOk: () => void | Promise<void>;
  okText?: string;
  cancelText?: string;
  danger?: boolean;
}

/**
 * Show a confirmation modal (imperative API).
 *
 * Usage:
 *   confirmModal({ content: 'Xóa mục này?', onOk: () => handleDelete(id) });
 */
export function confirmModal({
  title = 'Xác nhận',
  content,
  onOk,
  okText = 'Đồng ý',
  cancelText = 'Hủy',
  danger = false,
}: ConfirmModalOptions) {
  Modal.confirm({
    title,
    icon: <ExclamationCircleOutlined />,
    content,
    okText,
    cancelText,
    okButtonProps: { danger },
    onOk,
  });
}
