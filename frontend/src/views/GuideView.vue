<template>
  <section class="section-block">
    <SectionHeading
      eyebrow="Guide"
      title="优先使用预设问题和结果展示，让它更像导览机与展签助手"
      description="保留 Streamlit 里的示例问题、模式切换、引用出处和问答结果结构，但继续用 Vue 页面承载。"
    />

    <div class="guide-preset-grid">
      <button v-for="question in topQuestions" :key="question" class="ghost-button" type="button" @click="applyPrompt(question)">
        {{ question }}
      </button>
    </div>
    <div class="guide-preset-grid guide-preset-grid--two">
      <button v-for="question in extraQuestions" :key="question" class="ghost-button" type="button" @click="applyPrompt(question)">
        {{ question }}
      </button>
    </div>

    <div class="guide-layout">
      <div class="soft-panel guide-panel">
        <label>
          <span>模式</span>
          <select v-model="mode">
            <option v-for="item in guideModes" :key="item" :value="item">{{ item }}</option>
          </select>
        </label>

        <label>
          <span>回答策略</span>
          <select v-model="strategy">
            <option value="快速导览（直连RAG）">快速导览（直连RAG）</option>
            <option value="智能导览（Agent）">智能导览（Agent）</option>
          </select>
        </label>

        <p class="guide-tip" v-if="strategy === '快速导览（直连RAG）'">
          快速导览模式下仅使用本地知识库，响应更快；如果当前模式不是“导览讲解”，后端会自动切换为 Agent。
        </p>
        <p class="guide-tip" v-else-if="allowWeb">
          智能导览将优先本地检索，必要时再联网补充。
        </p>

        <label>
          <span>受众</span>
          <select v-model="audience">
            <option value="大众观众">大众观众</option>
            <option value="学生/入门">学生/入门</option>
            <option value="专业观众">专业观众</option>
          </select>
        </label>

        <div class="guide-toggles">
          <label><input v-model="citationsEnabled" type="checkbox" /> 展示参考资料与出处</label>
          <label><input v-model="allowWeb" :disabled="strategy === '快速导览（直连RAG）'" type="checkbox" /> 允许联网补充</label>
        </div>

        <label>
          <span>问题输入</span>
          <textarea v-model="prompt" rows="5"></textarea>
        </label>

        <button class="soft-button" type="button" :disabled="loading || !prompt.trim()" @click="submitGuideQuery">
          {{ loading ? '思考中...' : '开始导览' }}
        </button>
      </div>

      <div class="soft-panel guide-result">
        <div class="guide-result__eyebrow">导览结果</div>
        <div v-if="history.length" class="guide-history">
          <article v-for="(item, index) in history" :key="`${index}-${item.prompt}`" class="guide-history__item">
            <div class="guide-history__role">问题</div>
            <p class="guide-history__question">{{ item.prompt }}</p>
            <div class="guide-history__role">回答</div>
            <p class="guide-result__answer">{{ item.answer }}</p>
            <div v-if="item.citations.length" class="guide-result__citations">
              <strong>参考资料与出处</strong>
              <ul>
                <li v-for="citation in item.citations" :key="`${citation.source}-${citation.index}`">
                  <span>{{ citation.source || 'unknown' }}</span>
                  <em v-if="citation.page !== undefined && citation.page !== null">（page {{ citation.page }}）</em>
                  <p>{{ citation.snippet || '无摘要' }}</p>
                </li>
              </ul>
            </div>
          </article>
        </div>
        <p v-else class="guide-result__placeholder">提交问题后，这里会显示导览结果和对应出处。</p>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import SectionHeading from '@/components/common/SectionHeading.vue';
import { usePlatformContent } from '@/composables/usePlatformContent';
import { requestGuideQuery, type GuideCitation } from '@/services/api';

const route = useRoute();
const { content, ensureLoaded } = usePlatformContent();
const mode = ref('导览讲解');
const strategy = ref('快速导览（直连RAG）');
const audience = ref('大众观众');
const citationsEnabled = ref(true);
const allowWeb = ref(false);
const prompt = ref('');
const loading = ref(false);
const history = ref<{ prompt: string; answer: string; citations: GuideCitation[] }[]>([]);

onMounted(async () => {
  await ensureLoaded();
  hydratePromptFromRoute();
});

watch(
  () => route.query.prompt,
  () => {
    hydratePromptFromRoute();
  },
);

const sampleQuestions = computed(() => content.value?.guideSampleQuestions || []);
const topQuestions = computed(() => sampleQuestions.value.slice(0, 3));
const extraQuestions = computed(() => sampleQuestions.value.slice(3));
const guideModes = computed(() => content.value?.guideModes || ['导览讲解', '展签文案', '深度研究', 'FAQ生成']);

function applyPrompt(question: string) {
  prompt.value = question;
}

function hydratePromptFromRoute() {
  const routePrompt = route.query.prompt;
  if (typeof routePrompt === 'string' && routePrompt.trim()) {
    prompt.value = routePrompt;
  }
}

async function submitGuideQuery() {
  loading.value = true;
  try {
    const response = await requestGuideQuery({
      prompt: prompt.value,
      mode: mode.value,
      strategy: strategy.value,
      audience: audience.value,
      citations_enabled: citationsEnabled.value,
      allow_web: strategy.value === '快速导览（直连RAG）' ? false : allowWeb.value,
    });
    const citations = Array.isArray(response.citations)
      ? response.citations
      : response.citations?.citations || [];
    history.value.push({
      prompt: prompt.value,
      answer: response.answer,
      citations,
    });
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped lang="scss">
.guide-preset-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  margin-bottom: 1rem;
}

.guide-preset-grid--two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-bottom: 1.5rem;
}

.guide-layout {
  display: grid;
  grid-template-columns: 0.95fr 1.05fr;
  gap: var(--xiu-gap-lg);
}

.guide-panel,
.guide-result {
  padding: 1.35rem;
}

.guide-panel {
  display: grid;
  gap: 1rem;
}

label {
  display: grid;
  gap: 0.5rem;
}

span,
strong {
  font-weight: 600;
}

select,
textarea {
  width: 100%;
  border: 1px solid var(--xiu-line);
  border-radius: 18px;
  padding: 0.9rem 1rem;
  background: rgba(255, 255, 255, 0.65);
  color: var(--xiu-ink);
}

.guide-tip {
  margin: -0.2rem 0 0;
  color: var(--xiu-muted);
  line-height: 1.8;
}

.guide-toggles {
  display: grid;
  gap: 0.45rem;
  color: var(--xiu-muted);
}

.guide-result__eyebrow,
.guide-history__role {
  font-size: 0.8rem;
  letter-spacing: 0.1em;
  color: var(--xiu-accent);
  text-transform: uppercase;
}

.guide-history {
  display: grid;
  gap: 1.5rem;
}

.guide-history__item {
  padding-bottom: 1.2rem;
  border-bottom: 1px solid var(--xiu-line);
}

.guide-history__question,
.guide-result__placeholder,
.guide-result__answer,
.guide-result__citations p {
  margin: 0.45rem 0 0;
  color: var(--xiu-muted);
  line-height: 1.85;
  white-space: pre-wrap;
}

.guide-result__citations {
  margin-top: 1rem;
}

.guide-result__citations ul {
  padding-left: 1.1rem;
}

.guide-result__citations li + li {
  margin-top: 0.7rem;
}

.guide-result__citations span {
  color: var(--xiu-ink);
}

.guide-result__citations em {
  color: var(--xiu-muted);
  font-style: normal;
  margin-left: 0.25rem;
}

@media (max-width: 920px) {
  .guide-preset-grid,
  .guide-preset-grid--two,
  .guide-layout {
    grid-template-columns: 1fr;
  }
}
</style>
