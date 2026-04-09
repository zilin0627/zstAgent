export type PatternItem = {
  name: string;
  category: string;
  image: string;
  tags: string[];
  carrier: string;
  keywords: string[];
  summary: string;
  features: string[];
};

export type PatternScanItem = {
  name: string;
  category: string;
  related_pattern: string;
  image: string;
  caption: string;
};

export type CulturalShowcase = {
  hero_board: string;
  metrics: [string, string][];
  postcards: [string, string][];
  mockups: [string, string][];
  generated: [string, string][];
};

export type AIWorkflow = {
  steps: string[];
  boards: [string, string, string[]][];
  work_summary: string[];
  page_summary: string[];
  metrics: [string, string][];
};

export type GuideCitation = {
  index?: number;
  source?: string;
  page?: number | null;
  snippet?: string;
};

export type GuideResponse = {
  answer: string;
  citations?: { citations?: GuideCitation[] } | GuideCitation[] | null;
};

export type StudioResponse = GuideResponse;

export type PlatformContent = {
  patterns: PatternItem[];
  patternScans: PatternScanItem[];
  culturalShowcase: CulturalShowcase;
  aiWorkflow: AIWorkflow;
  guideSampleQuestions: string[];
  guideModes: string[];
  scenarioApplications: { title: string; subtitle: string; desc: string }[];
  bSideUsers: string[];
  cSideUsers: string[];
  businessModels: string[];
};

export function assetUrl(path: string) {
  if (!path) return path;
  if (/^https?:\/\//.test(path)) return path;
  if (path.startsWith('/')) return `${ASSET_BASE}${path}`;
  return `${ASSET_BASE}/${path}`;
}

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
const ASSET_BASE = API_BASE.replace(/\/$/, '');

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
    ...init,
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function fetchPlatformContent() {
  return apiFetch<PlatformContent>('/api/platform/content');
}

export function requestGuideQuery(payload: {
  prompt: string;
  mode: string;
  strategy: string;
  audience: string;
  citations_enabled: boolean;
  allow_web: boolean;
}) {
  return apiFetch<GuideResponse>('/api/guide/query', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function requestStudioGenerate(payload: {
  pattern_name: string;
  theme: string;
  target: string;
  tone: string;
  extra: string;
  allow_web: boolean;
  generation_mode: string;
}) {
  return apiFetch<StudioResponse>('/api/studio/generate', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}
