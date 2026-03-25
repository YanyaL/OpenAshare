export const DEMO_ACCESS_COOKIE_NAME = "ashare_demo_access";
export const DEMO_ACCESS_STATUS_PATH = "/api/demo/access";

export const DEMO_ACCESS_REQUIRED_MESSAGE =
  "请先解锁演示访问，再使用 AI 分析、Agent 聊天、持仓管理和设置。";

export type DemoAccessStatus = {
  enabled: boolean;
  unlocked: boolean;
  expires_at: string | null;
};

