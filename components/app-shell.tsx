"use client";

import {
  CSSProperties,
  createContext,
  PointerEvent as ReactPointerEvent,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { AgentChat } from "@/components/agent-chat";
import { useDemoAccess } from "@/components/demo-access-provider";

type AppShellContextValue = {
  sidebarOpen: boolean;
  toggleSidebar: () => void;
  isMobile: boolean;
  sidebarWidth: number;
  setSidebarWidth: (width: number) => void;
  isResizing: boolean;
  startResize: (event: ReactPointerEvent<HTMLButtonElement>) => void;
};

const AppShellContext = createContext<AppShellContextValue | null>(null);

function clampSidebarWidth(nextWidth: number) {
  if (typeof window === "undefined") {
    return nextWidth;
  }
  const maxWidth = Math.min(640, Math.max(360, window.innerWidth - 96));
  return Math.min(maxWidth, Math.max(360, nextWidth));
}

export function AppShellProvider({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isMobile, setIsMobile] = useState(false);
  const [sidebarWidth, setSidebarWidth] = useState(420);
  const [isResizing, setIsResizing] = useState(false);
  const resizeStateRef = useRef<{ startX: number; startWidth: number } | null>(null);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(max-width: 640px)");

    const applyMode = () => {
      const mobile = mediaQuery.matches;
      setIsMobile(mobile);
      setSidebarOpen(!mobile);
    };

    applyMode();
    mediaQuery.addEventListener("change", applyMode);
    return () => mediaQuery.removeEventListener("change", applyMode);
  }, []);

  useEffect(() => {
    if (isMobile) {
      setIsResizing(false);
    }
  }, [isMobile]);

  function toggleSidebar() {
    setSidebarOpen((open) => !open);
  }

  function startResize(event: ReactPointerEvent<HTMLButtonElement>) {
    if (isMobile || !sidebarOpen) {
      return;
    }
    event.preventDefault();
    resizeStateRef.current = {
      startX: event.clientX,
      startWidth: sidebarWidth,
    };
    setIsResizing(true);

    const handlePointerMove = (moveEvent: PointerEvent) => {
      const state = resizeStateRef.current;
      if (!state) {
        return;
      }
      const delta = moveEvent.clientX - state.startX;
      setSidebarWidth(clampSidebarWidth(state.startWidth - delta));
    };

    const handlePointerUp = () => {
      resizeStateRef.current = null;
      setIsResizing(false);
      window.removeEventListener("pointermove", handlePointerMove);
      window.removeEventListener("pointerup", handlePointerUp);
    };

    window.addEventListener("pointermove", handlePointerMove);
    window.addEventListener("pointerup", handlePointerUp);
  }

  const value = useMemo(
    () => ({
      sidebarOpen,
      toggleSidebar,
      isMobile,
      sidebarWidth,
      setSidebarWidth: (width: number) => setSidebarWidth(clampSidebarWidth(width)),
      isResizing,
      startResize,
    }),
    [isMobile, isResizing, sidebarOpen, sidebarWidth],
  );

  return <AppShellContext.Provider value={value}>{children}</AppShellContext.Provider>;
}

function useAppShell() {
  const value = useContext(AppShellContext);
  if (!value) {
    throw new Error("useAppShell must be used within AppShellProvider");
  }
  return value;
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLanding = pathname === "/";
  const { sidebarOpen, isMobile, sidebarWidth, isResizing, startResize } = useAppShell();
  const shellStyle = {
    "--sidebar-width": `${sidebarWidth}px`,
  } as CSSProperties;

  if (isLanding) {
    return (
      <div className="app-shell landing-shell">
        <div className="main-content">{children}</div>
      </div>
    );
  }

  return (
    <div
      className={`app-shell ${sidebarOpen ? "sidebar-open" : "sidebar-closed"} ${isMobile ? "mobile-shell" : ""} ${
        isResizing ? "resizing" : ""
      }`}
      style={shellStyle}
      data-mobile={isMobile ? "true" : "false"}
      data-resizing={isResizing ? "true" : "false"}
    >
      <div className="main-content">{children}</div>
      <aside
        className={`agent-sidebar ${sidebarOpen ? "open" : "closed"}`}
        id="agent-sidebar"
        aria-hidden={!sidebarOpen}
        data-state={sidebarOpen ? "open" : "closed"}
      >
        {sidebarOpen && !isMobile ? (
          <button
            type="button"
            className="agent-sidebar-resizer"
            onPointerDown={startResize}
            aria-label="拖动调整 Agent 宽度"
            title="拖动调整宽度"
          />
        ) : null}
        <div className="sidebar-body">
          <AgentChat compact />
        </div>
      </aside>
    </div>
  );
}

const NAV_ITEMS = [
  { href: "/work", label: "工作台" },
  { href: "/stocks", label: "单股分析" },
  { href: "/charts", label: "K 线图" },
  { href: "/portfolio", label: "持仓页" },
  { href: "/news", label: "消息页" },
  { href: "/hotspots", label: "热点页" },
  { href: "/settings", label: "设置" },
] as const;

export function Nav() {
  const pathname = usePathname();
  const [pendingHref, setPendingHref] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [visible, setVisible] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { unlocked, loaded, openDialog, revoke } = useDemoAccess();
  const { sidebarOpen, toggleSidebar } = useAppShell();

  const activePath = useMemo(() => pathname ?? "/", [pathname]);
  const isLanding = activePath === "/";

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [activePath]);

  useEffect(() => {
    if (!pendingHref) {
      return;
    }
    setVisible(true);
    setProgress(12);
    const timer = window.setInterval(() => {
      setProgress((value) => (value >= 88 ? value : value + Math.max(3, (92 - value) * 0.12)));
    }, 120);
    return () => window.clearInterval(timer);
  }, [pendingHref]);

  useEffect(() => {
    if (!pendingHref || activePath !== pendingHref) {
      return;
    }
    setProgress(100);
    const doneTimer = window.setTimeout(() => {
      setVisible(false);
      setProgress(0);
      setPendingHref(null);
    }, 220);
    return () => window.clearTimeout(doneTimer);
  }, [activePath, pendingHref]);

  function handleNavStart(href: string) {
    if (href === activePath) {
      setMobileMenuOpen(false);
      return;
    }
    setPendingHref(href);
    setMobileMenuOpen(false);
  }

  return (
    <nav className="nav">
      <div className={`nav-progress ${visible ? "visible" : ""}`} aria-hidden="true">
        <span style={{ transform: `scaleX(${progress / 100})` }} />
      </div>
      <div className="nav-inner">
        <Link href="/" className="logo" onClick={() => handleNavStart("/")}>
          <span className="logo-mark" aria-hidden="true">
            OA
          </span>
          <span className="logo-text">
            <span className="logo-name">OpenAshare</span>
            <span className="logo-tag">A 股原生智能引擎</span>
          </span>
        </Link>

        <div className="nav-actions">
          {isLanding ? (
            <Link href="/work" className="nav-landing-link" onClick={() => handleNavStart("/work")}>
              进入工作台
            </Link>
          ) : (
            <>
              <button
                type="button"
                className="nav-menu-toggle"
                aria-expanded={mobileMenuOpen}
                aria-controls="nav-links-panel"
                onClick={() => setMobileMenuOpen((open) => !open)}
              >
                {mobileMenuOpen ? "关闭菜单" : "菜单"}
              </button>
              <button
                type="button"
                className={`nav-agent-toggle ${sidebarOpen ? "open" : "closed"}`}
                aria-expanded={sidebarOpen}
                aria-controls="agent-sidebar"
                onClick={toggleSidebar}
              >
                <span className="nav-agent-toggle-label">Agent</span>
                <span className="nav-agent-toggle-state">{sidebarOpen ? "收起" : "展开"}</span>
              </button>
              <div id="nav-links-panel" className={`nav-links-panel ${mobileMenuOpen ? "open" : ""}`}>
                <div className="nav-links">
                  {NAV_ITEMS.map((item) => (
                    <Link
                      key={item.href}
                      href={item.href}
                      onClick={() => handleNavStart(item.href)}
                      className={activePath === item.href ? "active" : undefined}
                    >
                      {item.label}
                    </Link>
                  ))}
                  <button
                    type="button"
                    className={`nav-demo-button ${unlocked ? "active" : ""}`}
                    onClick={() => {
                      setMobileMenuOpen(false);
                      openDialog();
                    }}
                  >
                    {loaded ? (unlocked ? "演示已解锁" : "解锁演示") : "检查访问"}
                  </button>
                  {unlocked ? (
                    <button type="button" className="nav-demo-link" onClick={revoke}>
                      退出演示
                    </button>
                  ) : null}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
