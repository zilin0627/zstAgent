<template>
  <section class="section-block">
    <SectionHeading
      eyebrow="Pattern Atlas"
      title="先筛选，再逐个展开看会更轻松"
      description="这一页把典型母题和真实扫图放在一起，方便从图像观察进入进一步理解。为了减少反复跳转，我保留了筛选、导览入口和共创入口，但尽量让结构更清楚。"
    />

    <div class="atlas-overview grid-2">
      <article class="soft-panel atlas-note">
        <h3>浏览提示</h3>
        <ul>
          <li>先按类型筛选，减少一次看到太多内容。</li>
          <li>先看图片和摘要，再决定要不要进入导览。</li>
          <li>如果想做设计延展，再进入 AI 共创。</li>
        </ul>
      </article>
      <div class="metric-row">
        <div class="soft-panel metric-box">
          <strong>{{ patterns.length }}</strong>
          <span>已展示纹样</span>
        </div>
        <div class="soft-panel metric-box">
          <strong>5 类</strong>
          <span>图谱类型</span>
        </div>
        <div class="soft-panel metric-box">
          <strong>已开发</strong>
          <span>了解</span>
        </div>
        <div class="soft-panel metric-box">
          <strong>已开发</strong>
          <span>进入共创</span>
        </div>
      </div>
    </div>
  </section>

  <section class="section-block">
    <div class="atlas-filter soft-panel">
      <button
        v-for="item in patternCategories"
        :key="item"
        type="button"
        class="atlas-filter__chip"
        :class="{ 'atlas-filter__chip--active': currentCategory === item }"
        @click="currentCategory = item"
      >
        {{ item }}
      </button>
    </div>
  </section>

  <section class="section-block">
    <div v-if="loading" class="soft-panel state-panel">正在加载纹样图谱...</div>
    <div v-else-if="error" class="soft-panel state-panel">{{ error }}</div>
    <div v-else-if="!filteredPatterns.length" class="soft-panel state-panel">当前筛选条件下暂无纹样卡片。</div>
    <div v-else class="grid-2">
      <PatternCard v-for="item in filteredPatterns" :key="item.name" :item="item" />
    </div>
  </section>

  <section class="section-block">
    <SectionHeading
      eyebrow="刺绣扫图"
      title="从真实绣片扫描中观察针脚、材质与构图细节"
      description="按钮逻辑延续 Streamlit：可以带着扫图线索去导览，也可以把扫图观察直接带入设计工作台。"
    />
    <div class="atlas-filter soft-panel">
      <button
        v-for="item in scanCategories"
        :key="item"
        type="button"
        class="atlas-filter__chip"
        :class="{ 'atlas-filter__chip--active': currentScanCategory === item }"
        @click="currentScanCategory = item"
      >
        {{ item }}
      </button>
    </div>

    <div class="grid-3 scans-grid">
      <article v-for="item in filteredScans" :key="item.name" class="soft-panel scan-card">
        <img :src="normalizeAssetPath(item.image)" :alt="item.name" class="scan-card__image" />
        <div class="scan-card__body">
          <h3>{{ item.name }}</h3>
          <span>类别：{{ item.category }}｜对应图谱：{{ item.related_pattern }}</span>
          <p>{{ item.caption }}</p>
          <div class="scan-card__actions">
            <button type="button" class="ghost-button" @click="goToGuideByScan(item.related_pattern)">查看关联纹样</button>
            <button type="button" class="ghost-button" @click="goToStudioByScan(item)">以这张扫图进入共创</button>
          </div>
        </div>
      </article>
    </div>
  </section>

  <section class="section-block atlas-details grid-2">
    <article class="soft-panel atlas-note">
      <h3>图谱阅读维度</h3>
      <ul>
        <li>纹样名称与类型</li>
        <li>核心构图关系</li>
        <li>局部线条与重复节奏</li>
        <li>常见载体与视觉位置</li>
        <li>适合延展的设计方向</li>
      </ul>
    </article>
    <article class="soft-panel atlas-note">
      <h3>延伸入口</h3>
      <ul>
        <li>进入文化导览，获取讲解词和展签说明</li>
        <li>进入文创展陈，查看纹样转化案例</li>
        <li>进入 AI 共创实验，生成概念提案</li>
        <li>进入场景应用，思考展陈与传播方式</li>
      </ul>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import SectionHeading from '@/components/common/SectionHeading.vue';
import PatternCard from '@/components/pattern/PatternCard.vue';
import { patternCategories, scanCategories, normalizeAssetPath, type PatternScanItem } from '@/data/mock/patterns';
import { usePlatformContent } from '@/composables/usePlatformContent';
import { useStudioStore } from '@/stores/studio';

const router = useRouter();
const studio = useStudioStore();
const currentCategory = ref('全部');
const currentScanCategory = ref('全部');
const { content, loading, error, ensureLoaded } = usePlatformContent();

onMounted(() => {
  ensureLoaded();
});

const patterns = computed(() => content.value?.patterns || []);
const scans = computed(() => content.value?.patternScans || []);

const filteredPatterns = computed(() => {
  if (currentCategory.value === '全部') return patterns.value;
  return patterns.value.filter((item) => item.category === currentCategory.value);
});

const filteredScans = computed(() => {
  if (currentScanCategory.value === '全部') return scans.value;
  return scans.value.filter((item) => item.category === currentScanCategory.value);
});

function goToGuideByScan(patternName: string) {
  router.push({
    path: '/guide',
    query: {
      prompt: `请介绍侗族刺绣中的${patternName}，并结合真实绣片说明它在构图和工艺表现上的特点。`,
    },
  });
}

function goToStudioByScan(item: PatternScanItem) {
  studio.pattern = item.related_pattern;
  studio.theme = `围绕${item.name}展开当代转化`;
  studio.direction = '海报视觉';
  studio.tone = '传统庄重';
  studio.note = `请结合真实扫图《${item.name}》展开创意提案，重点吸收其${item.caption}`;
  router.push('/studio');
}
</script>

<style scoped lang="scss">
.atlas-overview {
  align-items: start;
}

.atlas-note {
  padding: 1.2rem 1.25rem;
}

.atlas-note h3 {
  margin: 0 0 0.75rem;
}

.atlas-note ul {
  margin: 0;
  padding-left: 1.15rem;
  color: var(--xiu-muted);
  line-height: 1.9;
}

.atlas-filter {
  padding: 0.8rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem;
}

.atlas-filter__chip {
  border: none;
  padding: 0.72rem 1rem;
  border-radius: 999px;
  background: transparent;
  color: var(--xiu-muted);
  cursor: pointer;
}

.atlas-filter__chip--active {
  background: var(--xiu-primary-soft);
  color: var(--xiu-primary);
}

.state-panel {
  padding: 1.25rem;
}

.scans-grid {
  margin-top: 1.2rem;
}

.scan-card {
  overflow: hidden;
}

.scan-card__image {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
}

.scan-card__body {
  padding: 1rem 1.1rem 1.2rem;
}

.scan-card__body h3 {
  margin: 0 0 0.35rem;
}

.scan-card__body span {
  color: var(--xiu-accent);
  font-size: 0.82rem;
}

.scan-card__body p {
  margin: 0.65rem 0 0;
  color: var(--xiu-muted);
  line-height: 1.8;
}

.scan-card__actions {
  display: grid;
  gap: 0.7rem;
  margin-top: 1rem;
}

.atlas-details {
  align-items: stretch;
}
</style>
