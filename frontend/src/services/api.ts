import { useAppStore } from '../store/appStore';

const API_URL = process.env.EXPO_PUBLIC_API_URL || 'http://127.0.0.1:8001';

const PUBLIC_API_PREFIXES = ['/api/v1/auth', '/api/v1/geo', '/api/v1/config', '/api/v1/webhook'];

function shouldAttachToken(path: string, explicitToken?: string): string | undefined {
  if (explicitToken) return explicitToken;
  if (PUBLIC_API_PREFIXES.some((p) => path.startsWith(p))) return undefined;
  return useAppStore.getState().token ?? undefined;
}

type RequestOptions = {
  token?: string;
  headers?: Record<string, string>;
  skipAuthRedirect?: boolean;
};

type OnUnauthorized = () => void;
let onUnauthorized: OnUnauthorized | null = null;

export function setUnauthorizedHandler(handler: OnUnauthorized | null) {
  onUnauthorized = handler;
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown,
  options: RequestOptions = {}
): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  const token = shouldAttachToken(path, options.token);
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const resp = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (resp.status === 401 && !options.skipAuthRedirect) {
    onUnauthorized?.();
    throw new Error('Unauthorized');
  }

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    const detail = err.detail;
    const message =
      typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? detail.map((d: { msg?: string }) => d.msg).join(', ')
          : `HTTP ${resp.status}`;
    throw new Error(message);
  }

  if (resp.status === 204) {
    return undefined as T;
  }

  const text = await resp.text();
  return (text ? JSON.parse(text) : undefined) as T;
}

export const api = {
  get: <T>(path: string, options?: RequestOptions) => request<T>('GET', path, undefined, options),
  post: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>('POST', path, body, options),
  patch: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>('PATCH', path, body, options),
  put: <T>(path: string, body?: unknown, options?: RequestOptions) =>
    request<T>('PUT', path, body, options),
  delete: <T>(path: string, options?: RequestOptions) =>
    request<T>('DELETE', path, undefined, options),
};

export { API_URL };

export async function apiFetch<T>(
  path: string,
  options: RequestInit & { token?: string; skipAuthRedirect?: boolean } = {}
): Promise<T> {
  const { token, skipAuthRedirect, method = 'GET', body, ...rest } = options;
  return request<T>(
    method,
    path,
    body !== undefined ? JSON.parse(body as string) : undefined,
    { token, skipAuthRedirect, headers: rest.headers as Record<string, string> }
  );
}

export async function switchRole(token: string, role: 'housewife' | 'young_mom') {
  return api.post<{
    role: string;
    features: Array<{ id: string; title_key: string; icon: string; route: string }>;
    token_balance: number;
    shared_data: { district?: string };
  }>('/api/v1/roles/switch', { role }, { token });
}

export function initApiAuth() {
  setUnauthorizedHandler(() => {
    useAppStore.getState().setToken(null);
  });
}
