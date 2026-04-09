<template>
  <section class="section-block">
    <SectionHeading
      eyebrow="Design Studio"
      title="用选择代替大段输入，让这里更像设计工作台"
      description="先选纹样，再看扫图，再生成提案。结构、提示和结果区都按 Streamlit 工作台迁回，但继续保留 Vue 框架。"
    />

    <div class="grid-3 step-grid">
      <article v-for="item in steps" :key="item.title" class="soft-panel step-card">
        <div class="step-card__eyebrow">{{ item.step }}</div>
        <h3>{{ item.title }}</h3>
        <p>{{ item.desc }}</p>
      </article>
    </div>

    <div class="studio-layout">
      <div class="soft-panel studio-form">
        <label>
          <span>核心纹样</span>
          <select v-model="studio.pattern">
            <option v-for="item in patternNames" :key="item" :value="item">{{ item }}</option>
          </select>
        </label>

        <label>
          <span>设计方向</span>
          <input v-model="studio.theme" type="text" />
        </label>

        <label>
          <span>应用方向</span>
          <select v-model="studio.direction">
            <option v-for="item in directions" :key="item" :value="item">{{ item }}</option>
          </select>
        </label>

        <label>
          <span>风格倾向</span>
          <select v-model="studio.tone">
            <option v-for="item in tones" :key="item" :value="item">{{ item }}</option>
          </select>
        </label>

        <label>
          <span>补充说明</span>
          <textarea v-model="studio.note" rows="6"></textarea>
        </label>

        <details class="studio-advanced">
          <summary>高级设置</summary>
          <div class="studio-advanced__body">
            <label><input v-model="studio.allowWeb" type="checkbox" /> 允许联网补充</label>
            <label>
              <span>生成模式</span>
              <select v-model="studio.generationMode">
                <option value="快速模式（直连知识库）">快速模式（直连知识库）</option>
                <option value="标准模式（Agent 工作流）">标准模式（Agent 工作流）</option>
              </select>
            </label>
          </div>
        </details>

        <div class="studio-example-list">
          <strong>快速示例</strong>
          <button v-for="sample in examples" :key="sample.label" class="ghost-button" type="button" @click="applyExample(sample)">
            {{ sample.label }}
          </button>
        </div>

        <button class="soft-button studio-form__submit" type="button" :disabled="studio.loading" @click="studio.generateProposal()">
          {{ studio.loading ? '正在生成创意提案...' : '生成设计提案' }}
        </button>
      </div>

      <div class="studio-side">
        <article class="soft-panel studio-preview">
          <h3>纹样输入预览</h3>
          <p><strong>核心纹样：</strong>{{ studio.pattern }}</p>
          <p><strong>应用方向：</strong>{{ studio.direction }}</p>
          <p><strong>风格倾向：</strong>{{ studio.tone }}</p>
          <p><strong>图谱摘要：</strong>{{ currentPattern?.summary || '当前纹样暂无摘要。' }}</p>
          <p v-if="relatedScans.length"><strong>关联真实扫图：</strong>{{ relatedScans.slice(0, 3).map((item) => item.name).join('、') }}</p>
          <p v-else>当前纹样暂未关联真实扫图。</p>
          <p class="studio-preview__tip" v-if="studio.allowWeb">本次生成将优先使用本地知识库，并在必要时补充公开网络资料。</p>
          <p class="studio-preview__tip" v-else>本次生成仅使用本地知识库与当前图谱资料。</p>
          <p class="studio-preview__tip" v-if="studio.generationMode === '快速模式（直连知识库）'">快速模式会直接调用本地知识库总结，速度更快，适合先出初稿。</p>
          <p class="studio-preview__tip" v-else>标准模式会经过 Agent 工作流，并支持联网补充，内容通常更完整。</p>
        </article>

        <article class="soft-panel studio-linked">
          <h3>关联真实扫图</h3>
          <div v-if="relatedScans.length" class="studio-linked__list">
            <article v-for="item in relatedScans.slice(0, 2)" :key="item.name" class="studio-linked__item">
              <img :src="normalizeAssetPath(item.image)" :alt="item.name" />
              <p>{{ item.name }}｜{{ item.category }}</p>
            </article>
          </div>
          <p v-else class="studio-empty">当前暂无关联扫图。</p>
        </article>
      </div>
    </div>

    <div class="grid-2 studio-middle-grid">
      <article class="soft-panel studio-reference-card">
        <h3>图谱与扫图联动</h3>
        <p class="studio-reference-card__desc">先观察图谱卡片，再对照真实绣片，有助于提升提案质量。</p>
        <div v-if="currentPattern" class="studio-reference-card__pattern">
          <img :src="normalizeAssetPath(currentPattern.image)" :alt="currentPattern.name" />
          <div>
            <h4>{{ currentPattern.name }}</h4>
            <p>{{ currentPattern.category }}</p>
            <ul>
              <li v-for="feature in currentPattern.features" :key="feature">{{ feature }}</li>
            </ul>
          </div>
        </div>
        <RouterLink class="studio-reference-card__link" to="/atlas">进入图谱查看 {{ studio.pattern }}</RouterLink>
      </article>

      <article class="soft-panel studio-usage">
        <h3>使用建议</h3>
        <ul>
          <li>先从“选择核心纹样”开始，不建议一开始就输入太泛的主题。</li>
          <li>优先观察关联扫图中的层次、边饰和针脚，再写补充要求。</li>
          <li>如果要做比赛、课程或品牌方案，可把具体用途写进补充要求。</li>
          <li>开启联网后，系统会在本地资料不足时补充公开背景信息。</li>
        </ul>
      </article>
    </div>

    <div class="grid-2 studio-bottom-grid">
      <article class="soft-panel studio-usage">
        <h3>推荐操作方式</h3>
        <ol>
          <li>选择一个纹样，例如龙纹、太阳榕树纹或混沌花纹。</li>
          <li>查看右侧图谱摘要与关联真实扫图，先形成视觉判断。</li>
          <li>选择应用方向和风格，再补充具体场景要求。</li>
          <li>生成后把结果带回图谱或导览页面继续追问。</li>
        </ol>
      </article>

      <article class="soft-panel studio-usage">
        <h3>提示词参考</h3>
        <ul>
          <li>请围绕龙纹生成一组适合侗绣主题展主视觉的海报文案，强调中心构图与守护感。</li>
          <li>请围绕太阳榕树纹生成一组适合文旅包装的概念提案，突出向上生长与层级关系。</li>
          <li>请结合混沌花纹和真实扫图观察，生成适合课程工作坊的教学型策划文案。</li>
        </ul>
      </article>
    </div>

    <div class="studio-result-wrap">
      <ProposalResultPanel
        :generated="studio.generated"
        :title="studio.pattern"
        :body-text="studio.result.rawText"
        :citations="studio.citations as GuideCitation[]"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue';
import SectionHeading from '@/components/common/SectionHeading.vue';
import ProposalResultPanel from '@/components/studio/ProposalResultPanel.vue';
import { normalizeAssetPath } from '@/data/mock/patterns';
import { usePlatformContent } from '@/composables/usePlatformContent';
import { useStudioStore } from '@/stores/studio';
import type { GuideCitation } from '@/services/api';

const studio = useStudioStore();
const { content, ensureLoaded } = usePlatformContent();
const directions = ['海报视觉', '丝巾设计', '课程工作坊', '品牌包装'];
const tones = ['传统庄重', '轻盈现代', '几何理性', '节庆热烈'];
const steps = [
  { step: '步骤 1', title: '选择纹样', desc: '先从图谱母题中锁定一个核心纹样，明确本次共创的视觉中心。' },
  { step: '步骤 2', title: '参考扫图', desc: '查看与该纹样关联的真实刺绣扫图，提取针脚、层次和构图特征。' },
  { step: '步骤 3', title: '生成提案', desc: '结合主题、方向与风格倾向，生成可直接进入方案讨论的文案结果。' },
];
const examples = [
  {
    label: '展陈型示例',
    pattern: '龙纹',
    target: '海报视觉',
    tone: '传统庄重',
    extra: '希望用于侗绣主题展主视觉，突出守护感、中心构图与礼仪气质。',
  },
  {
    label: '文创型示例',
    pattern: '太阳榕树纹',
    target: '品牌包装',
    tone: '轻盈现代',
    extra: '希望保留树形向上生长的视觉特征，并适合茶礼或文旅伴手礼包装。',
  },
  {
    label: '教学型示例',
    pattern: '混沌花纹',
    target: '课程工作坊',
    tone: '几何理性',
    extra: '适合高校课程或研学工作坊，突出构图分析、纹样拆解和动手实践转化。',
  },
];

onMounted(async () => {
  await ensureLoaded();
});

const patternNames = computed(() => content.value?.patterns.map((item) => item.name) || []);
const currentPattern = computed(() => (content.value?.patterns || []).find((item) => item.name === studio.pattern) || null);
const relatedScans = computed(() =>
  (content.value?.patternScans || []).filter((item) => item.related_pattern === studio.pattern),
);

watch(
  patternNames,
  (names) => {
    if (!names.length) return;
    if (!names.includes(studio.pattern)) {
      studio.pattern = names[0];
    }
    if (!studio.theme || studio.theme.startsWith('围绕')) {
      studio.theme = `围绕${studio.pattern}展开当代转化`;
    }
  },
  { immediate: true },
);

function applyExample(sample: { pattern: string; target: string; tone: string; extra: string }) {
  studio.pattern = sample.pattern;
  studio.theme = `围绕${sample.pattern}展开当代转化`;
  studio.direction = sample.target as (typeof directions)[number];
  studio.tone = sample.tone as (typeof tones)[number];
  studio.note = sample.extra;
}
</script>

<style scoped lang="scss">
.step-grid {
  margin-bottom: 1.5rem;
}

.step-card {
  padding: 1.2rem;
}

.step-card__eyebrow {
  margin-bottom: 0.45rem;
  font-size: 0.8rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--xiu-accent);
}

.step-card h3,
.studio-preview h3,
.studio-linked h3,
.studio-usage h3,
.studio-reference-card h3,
.studio-reference-card h4 {
  margin: 0 0 0.5rem;
}

.step-card p,
.studio-preview p,
.studio-empty,
.studio-usage li,
.studio-reference-card__desc,
.studio-reference-card__pattern p,
.studio-reference-card__pattern li,
.studio-reference-card__link {
  margin: 0;
  color: var(--xiu-muted);
  line-height: 1.85;
}

.studio-layout {
  display: grid;
  grid-template-columns: 0.95fr 1.05fr;
  gap: var(--xiu-gap-lg);
}

.studio-form,
.studio-preview,
.studio-linked,
.studio-usage {
  padding: 1.4rem;
}

.studio-form {
  display: grid;
  gap: 1rem;
}

.studio-side {
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

input,
select,
textarea {
  width: 100%;
  border: 1px solid var(--xiu-line);
  border-radius: 18px;
  padding: 0.9rem 1rem;
  background: rgba(255, 255, 255, 0.65);
  color: var(--xiu-ink);
}

textarea {
  resize: vertical;
  min-height: 132px;
}

.studio-advanced summary {
  cursor: pointer;
  font-weight: 600;
}

.studio-advanced__body {
  display: grid;
  gap: 1rem;
  margin-top: 0.9rem;
}

.studio-example-list {
  display: grid;
  gap: 0.75rem;
}

.studio-form__submit {
  justify-self: start;
}

.studio-preview__tip {
  margin-top: 0.75rem;
}

.studio-linked__list {
  display: grid;
  gap: 1rem;
}

.studio-linked__item img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  display: block;
  margin-bottom: 0.7rem;
}

.studio-middle-grid {
  margin-top: 1.5rem;
}

.studio-reference-card {
  padding: 1.4rem;
}

.studio-reference-card__pattern {
  display: grid;
  grid-template-columns: 180px minmax(0, 1fr);
  gap: 1rem;
  margin-top: 0.95rem;
}

.studio-reference-card__pattern img {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  border-radius: 18px;
}

.studio-reference-card__pattern ul {
  margin: 0;
  padding-left: 1rem;
}

.studio-reference-card__link {
  display: inline-flex;
  margin-top: 1rem;
  padding-bottom: 0.12rem;
  border-bottom: 1px solid var(--xiu-line-strong);
}

.studio-bottom-grid {
  margin-top: 1.5rem;
}

.studio-usage ol,
.studio-usage ul {
  margin: 0;
  padding-left: 1.15rem;
}

.studio-result-wrap {
  margin-top: 1.5rem;
}

@media (max-width: 920px) {
  .studio-layout,
  .studio-bottom-grid,
  .studio-middle-grid,
  .step-grid,
  .studio-reference-card__pattern {
    grid-template-columns: 1fr;
  }
}
</style>
