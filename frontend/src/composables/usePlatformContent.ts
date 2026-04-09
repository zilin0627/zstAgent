import { ref } from 'vue';
import type { PlatformContent } from '@/services/api';
import { fetchPlatformContent } from '@/services/api';

const content = ref<PlatformContent | null>(null);
const loading = ref(false);
const loaded = ref(false);
const error = ref<string | null>(null);

export function usePlatformContent() {
  async function ensureLoaded() {
    if (loaded.value || loading.value) return;
    loading.value = true;
    error.value = null;
    try {
      content.value = await fetchPlatformContent();
      loaded.value = true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载平台内容失败';
    } finally {
      loading.value = false;
    }
  }

  return {
    content,
    loading,
    loaded,
    error,
    ensureLoaded,
  };
}
