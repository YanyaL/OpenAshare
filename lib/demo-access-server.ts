import { createHmac, timingSafeEqual } from "node:crypto";

import { DEMO_ACCESS_COOKIE_NAME, type DemoAccessStatus } from "@/lib/demo-access";

const COOKIE_MAX_AGE_SECONDS = 60 * 60 * 24 * 30;

function getDemoAccessCode() {
  return (process.env.DEMO_ACCESS_CODE ?? "").trim();
}

function getDemoAccessSecret() {
  return (process.env.DEMO_ACCESS_SECRET ?? process.env.DEMO_ACCESS_CODE ?? "").trim();
}

export function isDemoAccessEnabled() {
  return Boolean(getDemoAccessCode() && getDemoAccessSecret());
}

export function getDemoAccessStatusFromToken(token: string | undefined | null): DemoAccessStatus {
  if (!isDemoAccessEnabled()) {
    return {
      enabled: false,
      unlocked: true,
      expires_at: null,
    };
  }
  if (!token) {
    return {
      enabled: true,
      unlocked: false,
      expires_at: null,
    };
  }
  const parsed = parseDemoAccessToken(token);
  return {
    enabled: true,
    unlocked: parsed.unlocked,
    expires_at: parsed.expires_at,
  };
}

export function createDemoAccessToken(now = Date.now()): string {
  const issuedAt = Math.floor(now / 1000);
  const secret = getDemoAccessSecret();
  const signature = createHmac("sha256", secret).update(String(issuedAt)).digest("base64url");
  return `${issuedAt}.${signature}`;
}

export function parseDemoAccessToken(token: string | undefined | null): DemoAccessStatus {
  if (!isDemoAccessEnabled()) {
    return {
      enabled: false,
      unlocked: true,
      expires_at: null,
    };
  }
  if (!token) {
    return {
      enabled: true,
      unlocked: false,
      expires_at: null,
    };
  }
  const [issuedAtRaw, signature] = token.split(".");
  const issuedAt = Number(issuedAtRaw);
  if (!issuedAtRaw || !signature || !Number.isFinite(issuedAt)) {
    return {
      enabled: true,
      unlocked: false,
      expires_at: null,
    };
  }
  const secret = getDemoAccessSecret();
  const expected = createHmac("sha256", secret).update(String(Math.floor(issuedAt))).digest("base64url");
  const expectedBytes = Buffer.from(expected);
  const providedBytes = Buffer.from(signature);
  if (expectedBytes.length !== providedBytes.length || !timingSafeEqual(expectedBytes, providedBytes)) {
    return {
      enabled: true,
      unlocked: false,
      expires_at: null,
    };
  }
  const nowSeconds = Math.floor(Date.now() / 1000);
  if (issuedAt + COOKIE_MAX_AGE_SECONDS < nowSeconds) {
    return {
      enabled: true,
      unlocked: false,
      expires_at: new Date((issuedAt + COOKIE_MAX_AGE_SECONDS) * 1000).toISOString(),
    };
  }
  const expiresAt = new Date((issuedAt + COOKIE_MAX_AGE_SECONDS) * 1000).toISOString();
  return {
    enabled: true,
    unlocked: true,
    expires_at: expiresAt,
  };
}

export function buildDemoAccessCookieOptions(expiresAt: Date) {
  return {
    httpOnly: true,
    sameSite: "lax" as const,
    secure: process.env.NODE_ENV === "production",
    path: "/",
    expires: expiresAt,
  };
}

export function clearDemoAccessCookieOptions() {
  return {
    httpOnly: true,
    sameSite: "lax" as const,
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 0,
  };
}

export function buildDemoAccessExpiry(now = Date.now()) {
  return new Date(now + COOKIE_MAX_AGE_SECONDS * 1000);
}

export { DEMO_ACCESS_COOKIE_NAME };
