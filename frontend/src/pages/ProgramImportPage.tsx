import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, Button, Progress, Card, Collapse, Typography, Space, Spin, Result } from 'antd';
import { InboxOutlined, CheckCircleOutlined } from '@ant-design/icons';

import PageHeader from '@/components/PageHeader';
import { useUploadImport, useImportStatus, useImportPreview, useConfirmImport } from '@/hooks/useImport';

const { Dragger } = Upload;

export default function ProgramImportPage() {
  const navigate = useNavigate();
  const [taskId, setTaskId] = useState<string | null>(null);

  const upload = useUploadImport();
  const { data: status } = useImportStatus(taskId ?? undefined);
  const { data: preview } = useImportPreview(
    status?.status === 'completed' ? taskId ?? undefined : undefined,
  );
  const confirm = useConfirmImport();

  const handleUpload = async (file: File) => {
    const result = await upload.mutateAsync(file);
    setTaskId(result.id);
    return false; // prevent auto upload
  };

  const handleConfirm = async () => {
    if (!taskId) return;
    const result = await confirm.mutateAsync(taskId);
    if (result.result_program) {
      navigate(`/programs/${result.result_program}`);
    }
  };

  // Step 1: Upload
  if (!taskId) {
    return (
      <div>
        <PageHeader title="Import Chương trình Đào tạo" subtitle="Upload file Word (.docx) để import CTĐT" />
        <Card style={{ maxWidth: 600 }}>
          <Dragger
            accept=".docx"
            maxCount={1}
            beforeUpload={handleUpload}
            showUploadList={false}
          >
            <p className="ant-upload-drag-icon"><InboxOutlined /></p>
            <p className="ant-upload-text">Kéo thả file .docx vào đây</p>
            <p className="ant-upload-hint">Hoặc click để chọn file. Chỉ hỗ trợ định dạng .docx</p>
          </Dragger>
          {upload.isPending && <Spin className="mt-4" />}
        </Card>
      </div>
    );
  }

  // Step 2: Processing
  if (status && (status.status === 'pending' || status.status === 'processing')) {
    return (
      <div>
        <PageHeader title="Đang xử lý file..." subtitle={status.file_name} />
        <Card style={{ maxWidth: 500, textAlign: 'center' }}>
          <Progress type="circle" percent={status.progress} />
          <Typography.Paragraph className="mt-4">Đang phân tích file Word...</Typography.Paragraph>
        </Card>
      </div>
    );
  }

  // Step 3: Failed
  if (status?.status === 'failed') {
    return (
      <div>
        <PageHeader title="Import thất bại" />
        <Result
          status="error"
          title="Không thể phân tích file"
          subTitle={status.error_message}
          extra={<Button type="primary" onClick={() => setTaskId(null)}>Thử lại</Button>}
        />
      </div>
    );
  }

  // Step 4: Preview & Confirm
  return (
    <div>
      <PageHeader
        title="Xem trước kết quả Import"
        subtitle={status?.file_name}
        actions={
          <Space>
            <Button onClick={() => setTaskId(null)}>Hủy</Button>
            <Button type="primary" icon={<CheckCircleOutlined />} onClick={handleConfirm} loading={confirm.isPending}>
              Xác nhận Import
            </Button>
          </Space>
        }
      />

      {preview && (
        <Collapse
          defaultActiveKey={Object.keys(preview)}
          items={Object.entries(preview).map(([key, value]) => ({
            key,
            label: key,
            children: (
              <pre style={{ maxHeight: 300, overflow: 'auto', fontSize: 12 }}>
                {JSON.stringify(value, null, 2)}
              </pre>
            ),
          }))}
        />
      )}
    </div>
  );
}
