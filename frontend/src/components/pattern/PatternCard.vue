<template>
  <article class="pattern-card soft-panel">
    <img :src="normalizeAssetPath(item.image)" :alt="item.name" class="pattern-card__image" />
    <div class="pattern-card__body">
      <div class="pattern-card__meta">{{ item.category }}｜{{ item.tags.join(' / ') }}</div>
      <h3>{{ item.name }}</h3>
      <p>{{ item.summary }}</p>
      <p class="pattern-card__carrier"><strong>常见载体：</strong>{{ item.carrier }}</p>
      <div class="pattern-card__chips">
        <span v-for="keyword in item.keywords" :key="keyword">{{ keyword }}</span>
      </div>
      <button class="ghost-button pattern-card__toggle" type="button" @click="expanded = !expanded">
        {{ expanded ? '收起细节' : '查看图案特征' }}
      </button>
      <Transition name="fade-up">
        <div v-if="expanded" class="pattern-card__detail">
          <strong>图案特征</strong>
          <ul>
            <li v-for="feature in item.features" :key="feature">{{ feature }}</li>
          </ul>
        </div>
      </Transition>
      <div class="pattern-card__actions">
        <button class="ghost-button" type="button" @click="goGuide">了解 {{ item.name }}</button>
        <button class="ghost-button" type="button" @click="goStudio">进入共创</button>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useStudioStore } from '@/stores/studio';
import type { PatternItem } from '@/data/mock/patterns';
import { normalizeAssetPath } from '@/data/mock/patterns';

const props = defineProps<{
  item: PatternItem;
}>();

const expanded = ref(false);
const router = useRouter();
const studio = useStudioStore();

function goGuide() {
  router.push({
    path: '/guide',
    query: {
      prompt: `请介绍侗族刺绣中的${props.item.name}，重点说明构成特点、视觉特征和常见应用。`,
    },
  });
}

function goStudio() {
  studio.pattern = props.item.name;
  studio.theme = `围绕${props.item.name}展开当代转化`;
  studio.direction = '海报视觉';
  studio.tone = '传统庄重';
  studio.note = `希望围绕${props.item.name}展开当代转化，保留其核心构图特征与文化气质。`;
  router.push('/studio');
}
</script>

<style scoped lang="scss">
.pattern-card {
  overflow: hidden;
}

.pattern-card__image {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
}

.pattern-card__body {
  padding: 1.15rem;
}

.pattern-card__meta {
  font-size: 0.82rem;
  color: var(--xiu-accent);
  margin-bottom: 0.45rem;
}

h3 {
  margin: 0 0 0.5rem;
  font-size: 1.3rem;
}

p {
  margin: 0;
  color: var(--xiu-muted);
  line-height: 1.8;
}

.pattern-card__carrier {
  margin-top: 0.7rem;
}

.pattern-card__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin: 0.95rem 0;
}

.pattern-card__chips span {
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  background: var(--xiu-primary-soft);
  color: var(--xiu-primary);
  font-size: 0.88rem;
}

.pattern-card__toggle {
  margin-top: 0.25rem;
}

.pattern-card__detail {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--xiu-line);
  display: grid;
  gap: 0.45rem;
}

.pattern-card__actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.7rem;
  margin-top: 1rem;
}

ul {
  margin: 0;
  padding-left: 1.1rem;
  color: var(--xiu-muted);
}

@media (max-width: 640px) {
  .pattern-card__actions {
    grid-template-columns: 1fr;
  }
}
</style>
