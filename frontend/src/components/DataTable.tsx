import { useState, useMemo } from 'react';
import { Table, Input, Space, type TableProps } from 'antd';
import { SearchOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

interface DataTableProps<T extends object> extends Omit<TableProps<T>, 'columns'> {
  columns: ColumnsType<T>;
  /** Column keys to search within (client-side filter) */
  searchableColumns?: string[];
  /** Placeholder for search input */
  searchPlaceholder?: string;
}

export default function DataTable<T extends object>({
  columns,
  dataSource,
  searchableColumns = [],
  searchPlaceholder = 'Tìm kiếm...',
  ...rest
}: DataTableProps<T>) {
  const [searchText, setSearchText] = useState('');

  const filteredData = useMemo(() => {
    if (!searchText || searchableColumns.length === 0 || !dataSource) {
      return dataSource;
    }
    const lower = searchText.toLowerCase();
    return dataSource.filter((record) =>
      searchableColumns.some((key) => {
        const value = (record as Record<string, unknown>)[key];
        return value != null && String(value).toLowerCase().includes(lower);
      }),
    );
  }, [dataSource, searchText, searchableColumns]);

  return (
    <Space direction="vertical" className="w-full" size="middle">
      {searchableColumns.length > 0 && (
        <Input
          prefix={<SearchOutlined />}
          placeholder={searchPlaceholder}
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          allowClear
          style={{ maxWidth: 320 }}
        />
      )}
      <Table<T>
        columns={columns}
        dataSource={filteredData}
        pagination={{ showSizeChanger: true, showTotal: (total) => `Tổng: ${total}` }}
        scroll={{ x: 'max-content' }}
        size="middle"
        {...rest}
      />
    </Space>
  );
}
