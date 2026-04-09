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

export const patternCategories = ['全部', '动物纹', '人物纹', '植物纹 / 天体纹', '组合纹', '几何纹 / 花卉纹'];
export const scanCategories = ['全部', '龙纹类', '花纹类', '盘型类', '树纹类'];

export function normalizeAssetPath(path: string) {
  if (/^https?:\/\//.test(path)) return path;
  const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
  const normalizedBase = apiBase.replace(/\/$/, '');
  if (path.startsWith('/assets/')) return `${normalizedBase}${path}`;
  if (path.startsWith('assets/')) return `${normalizedBase}/${path}`;
  return path.startsWith('/') ? path : `/${path}`;
}
