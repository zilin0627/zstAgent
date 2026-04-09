<template>
  <section class="section-block">
    <SectionHeading
      eyebrow="Showcase"
      title="从图案到日常物件"
      description="这一页不再放展板式主图，而是把重心交给作品本身。可以把它理解成一个轻量的作品陈列区：先看平面，再看产品，最后看生成延展。"
    />

    <div v-if="showcase" class="showcase-page">
      <div class="metric-row">
        <div v-for="item in showcase.metrics" :key="item[0]" class="soft-panel metric-box">
          <strong>{{ item[1] }}</strong>
          <span>{{ item[0] }}</span>
        </div>
      </div>

      <section class="section-block">
        <h3>分类查看</h3>
        <div class="showcase-tabs">
          <button v-for="item in views" :key="item" type="button" class="showcase-tabs__item" :class="{ 'showcase-tabs__item--active': currentView === item }" @click="currentView = item">
            {{ item }}
          </button>
        </div>
        <p class="showcase-caption">{{ currentCaption }}</p>

        <div v-if="currentView === '明信片'" class="grid-4">
          <article v-for="item in showcase.postcards" :key="item[0]" class="soft-panel showcase-card">
            <img :src="assetUrl(item[1])" :alt="item[0]" />
            <p>{{ item[0] }}</p>
          </article>
        </div>

        <div v-else-if="currentView === '产品样机'" class="grid-2">
          <article v-for="item in showcase.mockups" :key="item[0]" class="soft-panel showcase-card">
            <img :src="assetUrl(item[1])" :alt="item[0]" />
            <p>{{ item[0] }}</p>
          </article>
        </div>

        <div v-else class="grid-3">
          <article v-for="item in showcase.generated" :key="item[0]" class="soft-panel showcase-card">
            <img :src="assetUrl(item[1])" :alt="item[0]" />
            <p>{{ item[0] }}</p>
          </article>
        </div>
      </section>

      <div class="grid-2 showcase-bottom">
        <article class="soft-panel showcase-note">
          <h3>这些图还能继续怎么用</h3>
          <ul>
            <li>平面：海报、明信片、展陈物料</li>
            <li>周边：冰箱贴、手机壳、帆布包、笔记本</li>
            <li>礼赠：丝巾、礼盒包装、伴手礼</li>
            <li>活动：课程材料、主题视觉、节庆物料</li>
          </ul>
        </article>
        <article class="soft-panel showcase-note">
          <h3>浏览建议</h3>
          <p>先看平面，再看产品，最后看生成延展，会更容易比较纹样在不同载体中的变化。</p>
        </article>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import SectionHeading from '@/components/common/SectionHeading.vue';
import { assetUrl } from '@/services/api';
import { usePlatformContent } from '@/composables/usePlatformContent';

const { content, ensureLoaded } = usePlatformContent();
const views = ['明信片', '产品样机', '生成延展'];
const currentView = ref('明信片');

onMounted(async () => {
  await ensureLoaded();
});

const showcase = computed(() => content.value?.culturalShowcase || null);
const currentCaption = computed(() => {
  if (currentView.value === '明信片') return '先看平面作品，比较容易观察纹样本身的布局和装饰感。';
  if (currentView.value === '产品样机') return '再看产品样机，会更容易感受到纹样进入日常物件后的状态。';
  return '最后看生成延展，可以对比传统纹样和扩展风格之间的关系。';
});
</script>

<style scoped lang="scss">
.showcase-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 0.85rem;
}

.showcase-tabs__item {
  border: 1px solid var(--xiu-line);
  background: transparent;
  padding: 0.65rem 0.95rem;
  border-radius: 999px;
  cursor: pointer;
}

.showcase-tabs__item--active {
  background: var(--xiu-primary-soft);
  color: var(--xiu-primary);
}

.showcase-caption {
  margin: 0 0 1rem;
  color: var(--xiu-muted);
  line-height: 1.8;
}

.showcase-card,
.showcase-note {
  overflow: hidden;
  padding-bottom: 0.85rem;
}

.showcase-card img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  display: block;
}

.showcase-card p,
.showcase-note p {
  margin: 0.85rem 1rem 0;
  color: var(--xiu-muted);
  line-height: 1.8;
}

.showcase-note {
  padding: 1.1rem 1.2rem;
}

.showcase-note h3 {
  margin: 0 0 0.7rem;
}

.showcase-note ul {
  margin: 0;
  padding-left: 1.15rem;
  color: var(--xiu-muted);
  line-height: 1.9;
}

.showcase-bottom {
  margin-top: 1.25rem;
}
</style>
