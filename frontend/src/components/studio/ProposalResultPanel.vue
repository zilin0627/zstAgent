<template>
  <aside class="result-panel soft-panel">
    <template v-if="generated">
      <div class="result-panel__eyebrow">创意结果区</div>
      <h3>{{ title }}</h3>
      <section>
        <strong>提案结果文本</strong>
        <textarea class="result-panel__textarea" :value="bodyText" rows="12" readonly></textarea>
      </section>
      <section v-if="sections.length" class="result-panel__sections">
        <article v-for="section in sections" :key="section.title" class="result-panel__section">
          <strong>{{ section.title }}</strong>
          <p class="result-panel__text">{{ section.body }}</p>
        </article>
      </section>
      <section v-if="citations.length">
        <strong>本次创意参考资料</strong>
        <ul>
          <li v-for="item in citations" :key="`${item.source}-${item.index}`">
            <span>{{ item.source || 'unknown' }}</span>
            <em v-if="item.page !== undefined && item.page !== null">（page {{ item.page }}）</em>
            <p>{{ item.snippet || '无摘要' }}</p>
          </li>
        </ul>
      </section>
    </template>
    <template v-else>
      <div class="result-panel__empty">
        <span class="result-panel__eyebrow">创意结果区</span>
        <h3>完成纹样选择后点击“生成设计提案”</h3>
        <p>这里会显示概念标题、主文案、设计转化建议以及本次检索到的参考资料。</p>
      </div>
    </template>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { GuideCitation } from '@/services/api';

const props = defineProps<{
  generated: boolean;
  title: string;
  bodyText: string;
  citations: GuideCitation[];
}>();

type ProposalSection = {
  title: string;
  body: string;
};

const sections = computed<ProposalSection[]>(() => parseSections(props.bodyText));

function parseSections(text: string) {
  if (!text.trim()) return [];
  const matches = [...text.matchAll(/(^|\n)\s*(\d+[\.、]\s*[^\n：:]+[：:]?)/g)];
  if (!matches.length) return [];

  return matches
    .map((match, index) => {
      const full = match[0];
      const heading = match[2]?.trim().replace(/[：:]$/, '') || '创意提案';
      const start = (match.index || 0) + full.length;
      const end = index + 1 < matches.length ? matches[index + 1].index || text.length : text.length;
      const body = text.slice(start, end).trim();
      return { title: heading, body };
    })
    .filter((item) => item.body);
}
</script>

<style scoped lang="scss">
.result-panel {
  padding: 1.4rem;
  min-height: 100%;
  display: grid;
  gap: 1rem;
}

.result-panel__eyebrow {
  font-size: 0.8rem;
  letter-spacing: 0.1em;
  color: var(--xiu-accent);
  text-transform: uppercase;
}

h3 {
  margin: 0;
  font-size: 1.5rem;
}

strong {
  display: block;
  margin-bottom: 0.35rem;
}

p,
ul {
  margin: 0;
  color: var(--xiu-muted);
  line-height: 1.85;
}

ul {
  padding-left: 1.15rem;
}

li + li {
  margin-top: 0.7rem;
}

li span {
  color: var(--xiu-ink);
  font-weight: 600;
}

li em {
  color: var(--xiu-muted);
  font-style: normal;
  margin-left: 0.25rem;
}

.result-panel__text {
  white-space: pre-wrap;
}

.result-panel__textarea {
  width: 100%;
  border: 1px solid var(--xiu-line);
  border-radius: 18px;
  padding: 0.9rem 1rem;
  background: rgba(255, 255, 255, 0.55);
  color: var(--xiu-ink);
  line-height: 1.7;
  resize: vertical;
}

.result-panel__sections {
  display: grid;
  gap: 0.9rem;
}

.result-panel__section {
  padding-top: 0.85rem;
  border-top: 1px solid var(--xiu-line);
}

.result-panel__empty {
  align-self: center;
}
</style>
