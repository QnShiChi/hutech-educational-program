import type { ThemeConfig } from 'antd';

/**
 * HUTECH brand colors + Ant Design theme configuration.
 * Primary: HUTECH Blue  #003399
 * Accent: HUTECH Red    #CC0000
 */
const themeConfig: ThemeConfig = {
  token: {
    colorPrimary: '#003399',
    colorLink: '#003399',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#CC0000',
    borderRadius: 6,
    fontFamily:
      '-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans",sans-serif',
  },
  components: {
    Layout: {
      siderBg: '#001529',
      headerBg: '#ffffff',
      bodyBg: '#f0f2f5',
    },
    Menu: {
      darkItemBg: '#001529',
      darkItemSelectedBg: '#003399',
    },
  },
};

export default themeConfig;
