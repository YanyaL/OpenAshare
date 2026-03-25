import {
  AnalysisProgressResponse,
  AgentHistoryTurn,
  AgentResponse,
  GlobalNewsItem,
  HotspotDetailResponse,
  HotspotItem,
  NewsItem,
  PortfolioAnalysisResponse,
  PortfolioPosition,
  StockAnalysisResponse,
  StockSearchResult,
  UserSettingsResponse,
  WebSearchResult,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

/**
 * Server Components / RSC run in Node: relative fetch("/api/...") does not hit FastAPI.
 * Use absolute backend URL on server so searchStocks / getStockAnalysis work after "开始分析".
 */
function apiBaseUrl(): string {
  if (typeof window !== "undefined") {
    return "";
  }
  const serverBase =
    process.env.BACKEND_BASE_URL ??
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    "http://127.0.0.1:8000";
  return String(serverBase).replace(/\/$/, "");
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const base = apiBaseUrl();
  const url = base ? `${base}${path}` : path;
  let response: Response;
  try {
    response = await fetch(url, {
      ...init,
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
    });
  } catch {
    throw new Error(`无法连接后端服务 ${base || API_BASE_URL || "Next API 代理"}`);
  }
  if (!response.ok) {
    const raw = await response.text();
    let detail = raw;
    try {
      const parsed = JSON.parse(raw) as { detail?: string; message?: string };
      detail = parsed.detail || parsed.message || raw;
    } catch {
      // keep raw body
    }
    throw new ApiError(detail || `API request failed: ${response.status}`, response.status);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export function searchStocks(query: string): Promise<StockSearchResult[]> {
  return request(`/api/stocks/search?q=${encodeURIComponent(query)}`);
}

export function searchStocksWithOptions(
  query: string,
  options?: { requestId?: string },
): Promise<StockSearchResult[]> {
  const params = new URLSearchParams({ q: query });
  if (options?.requestId) {
    params.set("request_id", options.requestId);
  }
  return request(`/api/stocks/search?${params.toString()}`);
}

export function getStockAnalysis(
  code: string,
  options?: { includeAi?: boolean; requestId?: string; requestInit?: RequestInit },
): Promise<StockAnalysisResponse> {
  const includeAi = options?.includeAi ?? true;
  const params = new URLSearchParams();
  if (!includeAi) {
    params.set("include_ai", "false");
  }
  if (options?.requestId) {
    params.set("request_id", options.requestId);
  }
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return request(`/api/stocks/${encodeURIComponent(code)}/analysis${suffix}`, options?.requestInit);
}

export function getStockNews(code: string): Promise<NewsItem[]> {
  return request(`/api/stocks/${encodeURIComponent(code)}/news`);
}

export function getStockAnalysisProgress(requestId: string): Promise<AnalysisProgressResponse> {
  return request(`/api/stocks/progress/${encodeURIComponent(requestId)}`);
}

export function getHotspots(): Promise<HotspotItem[]> {
  return request("/api/hotspots");
}

export function getGlobalNews(): Promise<GlobalNewsItem[]> {
  return request("/api/news/global");
}

export function webSearch(query: string, limit = 8): Promise<WebSearchResult[]> {
  return request(`/api/web/search?q=${encodeURIComponent(query)}&limit=${limit}`);
}

export function getHotspotDetail(topic: string): Promise<HotspotDetailResponse> {
  return request(`/api/hotspots/${encodeURIComponent(topic)}`);
}

export function getPortfolioAnalysis(options?: { requestInit?: RequestInit }): Promise<PortfolioAnalysisResponse> {
  return request("/api/portfolio/analysis", options?.requestInit);
}

export function getUserSettings(): Promise<UserSettingsResponse> {
  return request("/api/settings");
}

export function updateUserSettings(payload: {
  llm_model: string;
  llm_base_url?: string | null;
  llm_api_key?: string | null;
}): Promise<UserSettingsResponse> {
  return request("/api/settings", {
    method: "PUT",
    body: JSON.stringify(payload),
  });
}

export function listPortfolioPositions(options?: { requestInit?: RequestInit }): Promise<PortfolioPosition[]> {
  return request("/api/portfolio", options?.requestInit);
}

export function createPortfolioPosition(position: PortfolioPosition): Promise<PortfolioPosition> {
  return request("/api/portfolio/positions", {
    method: "POST",
    body: JSON.stringify(position),
  });
}

export function updatePortfolioPosition(
  id: number,
  position: PortfolioPosition,
): Promise<PortfolioPosition> {
  return request(`/api/portfolio/positions/${id}`, {
    method: "PUT",
    body: JSON.stringify(position),
  });
}

export async function deletePortfolioPosition(id: number): Promise<void> {
  await request(`/api/portfolio/positions/${id}`, {
    method: "DELETE",
  });
}

/**
 * Agent goes through Next.js Route Handler POST /api/agent/query (app/api/agent/query/route.ts).
 * That handler proxies to FastAPI with a long timeout — avoids browser CORS to :8000 and
 * avoids rewrite ECONNRESET. Client always uses same-origin URL.
 */
const AGENT_REQUEST_TIMEOUT_MS = 130_000; // slightly longer than server proxy timeout

export async function queryAgent(query: string, history: AgentHistoryTurn[] = [], sessionId?: string): Promise<AgentResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), AGENT_REQUEST_TIMEOUT_MS);
  try {
    const response = await fetch("/api/agent/query", {
      method: "POST",
      cache: "no-store",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, history, session_id: sessionId }),
      signal: controller.signal,
    });
    const raw = await response.text();
    const data = raw ? (JSON.parse(raw) as AgentResponse) : ({} as AgentResponse);
    if (!response.ok) {
      const message =
        (data as { summary?: string; detail?: string }).summary ||
        (data as { summary?: string; detail?: string }).detail ||
        `API request failed: ${response.status}`;
      throw new ApiError(message, response.status);
    }
    return data;
  } catch (e) {
    if (e instanceof Error && e.name === "AbortError") {
      throw new Error("Agent request timed out. Is the API running? Try ./scripts/run_api.sh");
    }
    throw e instanceof Error ? e : new Error(String(e));
  } finally {
    clearTimeout(timeoutId);
  }
}
