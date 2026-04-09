<template>
  <section class="section-block">
    <SectionHeading
      eyebrow="Method"
      title="解释为什么做、怎么整理、AI 做了什么，以及最终输出了什么"
      description="这一页不是给所有人都必须详细看完的，而是给想继续了解过程的人一个更清晰的入口。它会展示纹样筛选、标签整理、模型训练和生成延展之间的大致关系。"
    />

    <div v-if="workflow" class="method-page">
      <div class="grid-2 method-intro">
        <article class="soft-panel method-note">
          <h3>从整理到生成</h3>
          <p>先整理纹样和标签，再构建生成时需要的描述方式，最后把结果延展到展示和设计应用中。</p>
          <ul>
            <li>先整理纹样和标签。</li>
            <li>再构建生成时需要的描述方式。</li>
            <li>最后把结果延展到展示和设计应用中。</li>
          </ul>
        </article>
        <article class="soft-panel method-note">
          <h3>补充说明</h3>
          <p>这里后续可替换为你的训练流程图、参数对比图或板块总结页，让方法展示更完整。</p>
        </article>
      </div>

      <section class="section-block">
        <h3>工作流</h3>
        <div class="grid-5 workflow-steps">
          <article v-for="step in workflow.steps" :key="step" class="soft-panel workflow-step">{{ step }}</article>
        </div>
      </section>

      <section class="section-block">
        <h3>展板查看</h3>
        <div class="grid-3">
          <article v-for="item in workflow.boards" :key="item[0]" class="soft-panel board-card">
            <img :src="assetUrl(item[1])" :alt="item[0]" />
            <h4>{{ item[0] }}</h4>
            <p>{{ item[2].join('｜') }}</p>
          </article>
        </div>
      </section>

      <div class="grid-2 method-summary">
        <article class="soft-panel summary-card">
          <h3>这部分我做了什么</h3>
          <ul>
            <li v-for="line in workflow.work_summary" :key="line">{{ line }}</li>
          </ul>
        </article>
        <article class="soft-panel summary-card">
          <h3>页面内直接展示</h3>
          <ul>
            <li v-for="line in workflow.page_summary" :key="line">{{ line }}</li>
          </ul>
        </article>
      </div>

      <div class="grid-2 method-summary">
        <article class="soft-panel summary-card">
          <h3>可以继续补充什么</h3>
          <ul>
            <li>`纹样演示初稿9.18.pptx`：适合补流程图和方法示意</li>
            <li>`侗绣纹样数据集整理.pdf`：适合补数据来源说明</li>
            <li>`详细标签分析.docx`：适合补标签整理依据</li>
          </ul>
        </article>
        <article class="soft-panel summary-card">
          <h3>这一页适合谁看</h3>
          <ul>
            <li>对普通观众来说，可以简单看看“这些图是怎么一步步来的”。</li>
            <li>对课程、展示或比赛场景来说，可以把它当作过程说明页。</li>
            <li>对设计相关用户来说，它也能帮助理解生成逻辑与延展方式。</li>
          </ul>
        </article>
      </div>

      <div class="metric-row method-metrics">
        <div v-for="item in workflow.metrics" :key="item[0]" class="soft-panel metric-box">
          <strong>{{ item[1] }}</strong>
          <span>{{ item[0] }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import SectionHeading from '@/components/common/SectionHeading.vue';
import { assetUrl } from '@/services/api';
import { usePlatformContent } from '@/composables/usePlatformContent';

const { content, ensureLoaded } = usePlatformContent();

onMounted(async () => {
  await ensureLoaded();
});

const workflow = computed(() => content.value?.aiWorkflow || null);
</script>

<style scoped lang="scss">
.method-intro,
.method-summary,
.method-metrics {
  margin-top: 1.25rem;
}

.method-note,
.summary-card {
  padding: 1.2rem 1.25rem;
}

.method-note h3,
.summary-card h3,
.board-card h4 {
  margin: 0 0 0.6rem;
}

.method-note p,
.method-note ul,
.summary-card ul,
.board-card p {
  margin: 0;
  color: var(--xiu-muted);
  line-height: 1.8;
}

.method-note ul,
.summary-card ul {
  padding-left: 1.15rem;
}

.workflow-steps {
  gap: 0.8rem;
}

.workflow-step {
  padding: 1rem;
  text-align: center;
  font-weight: 600;
}

.board-card {
  overflow: hidden;
  padding-bottom: 0.9rem;
}

.board-card img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  display: block;
}

.board-card h4,
.board-card p {
  margin-left: 1rem;
  margin-right: 1rem;
}
</style>
