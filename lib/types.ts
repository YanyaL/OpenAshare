export type StockSearchResult = {
  name: string;
  code: string;
  market: string;
  category: string;
  score: number;
  match_type: string;
};

export type StockAnalysisResponse = {
  stock_name: string;
  stock_code: string;
  market: string;
  quote: {
    stock_name: string;
    stock_code: string;
    current_price: number;
    change: number;
    change_pct: number;
    open_price: number;
    high_price: number;
    low_price: number;
    volume: number;
    amplitude_pct: number;
    timestamp: string;
  };
  technical_indicators: Record<string, number | null>;
  signal_summary: {
    overall_score: number;
    overall_signal: string;
    categories: Record<string, unknown>;
  };
  technical_commentary: string[];
  ai_insight: {
    enabled: boolean;
    content?: string | null;
    provider?: string | null;
    model?: string | null;
    error?: string | null;
  };
  chart_series: Array<{
    date: string;
    open: number | null;
    high: number | null;
    low: number | null;
    close: number | null;
    volume: number | null;
  }>;
  metadata: Record<string, unknown>;
};

export type AnalysisProgressResponse = {
  request_id: string;
  status: "pending" | "completed" | "error" | "unknown";
  stage: string;
  progress_pct: number;
  message: string;
  stock_code?: string | null;
  include_ai: boolean;
  updated_at?: string | null;
};

export type NewsItem = {
  id: string;
  stock_code: string;
  stock_name: string;
  source: string;
  published_at: string;
  title: string;
  summary: string;
  relation_type: string;
  sentiment: "bullish" | "bearish" | "neutral";
  impact_level: number;
  ai_takeaway?: string | null;
  url?: string | null;
};

export type GlobalNewsItem = {
  id: string;
  title: string;
  summary: string;
  source: string;
  published_at: string;
  category: string;
  topic: string;
  region: string;
  sentiment: "bullish" | "bearish" | "neutral";
  impact_level: number;
  url?: string | null;
  related_symbols: string[];
};

export type WebSearchResult = {
  id: string;
  title: string;
  snippet: string;
  url: string;
  source: string;
  published_at?: string | null;
  provider: string;
  query: string;
};

export type HotspotItem = {
  topic_name: string;
  heat_score: number;
  reason: string;
  trend_direction: "up" | "down" | "flat";
  ai_summary?: string | null;
  source: string;
  related_stocks: Array<{
    stock_name: string;
    stock_code: string;
    reason: string;
  }>;
};

export type HotspotDetailResponse = {
  topic: HotspotItem;
  related_news: NewsItem[];
  history: Array<{
    date: string;
    score: number;
    count: number;
  }>;
};

export type PortfolioPosition = {
  id?: number;
  stock_code: string;
  stock_name: string;
  cost_price: number;
  quantity: number;
  weight_pct?: number | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type PortfolioAnalysisResponse = {
  total_cost: number;
  total_market_value: number;
  total_pnl: number;
  total_pnl_pct: number;
  concentration_risk: string;
  technical_risk: string;
  rebalance_suggestions: string[];
  positions: Array<{
    position: PortfolioPosition;
    current_price: number;
    market_value: number;
    pnl: number;
    pnl_pct: number;
    risk_level: string;
    signal_summary: {
      overall_score: number;
      overall_signal: string;
    };
    suggestion: string;
  }>;
};

export type AgentResponse = {
  intent: string;
  summary: string;
  actions: string[];
  citations: string[];
  payload: {
    _meta?: {
      tools_used: string[];
      cache_hits: string[];
      rewritten_query?: string;
      slots?: {
        current_stock?: {
          name: string;
          code: string;
        } | null;
        current_topic?: string | null;
        current_market_scope?: string;
        requested_action?: string;
        comparison_mode?: string | null;
        time_horizon?: string;
        follow_up?: boolean;
      };
      memory_profile?: {
        preferred_market?: string | null;
        last_stock_code?: string | null;
        last_stock_name?: string | null;
        active_goal?: string | null;
        pinned_memory?: string[];
        watchlist?: Array<{
          code: string;
          name?: string | null;
        }>;
      };
      heartbeat?: {
        ran?: boolean;
        summary_text?: string | null;
        memory_markdown_path?: string | null;
        heartbeat_count?: number;
        last_heartbeat_at?: string | null;
      };
    };
    stock?: {
      name: string;
      code: string;
    };
    news?: NewsItem[];
    hotspots?: HotspotItem[];
    global_news?: GlobalNewsItem[];
    web_results?: WebSearchResult[];
  } & Partial<StockAnalysisResponse> &
    Partial<PortfolioAnalysisResponse> &
    Record<string, unknown>;
};

export type AgentHistoryTurn = {
  role: "user" | "agent";
  content: string;
  intent?: string | null;
  stock_code?: string | null;
  stock_name?: string | null;
};

export type ModelOption = {
  value: string;
  label: string;
  description?: string | null;
};

export type UserSettingsResponse = {
  llm_model: string;
  llm_model_source: "env" | "user";
  llm_base_url?: string | null;
  llm_configured: boolean;
  updated_at?: string | null;
  model_options: ModelOption[];
};
