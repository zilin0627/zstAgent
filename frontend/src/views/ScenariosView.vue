<template>
  <section class="section-block">
    <SectionHeading
      eyebrow="Scenarios"
      title="展示平台如何在展馆、课堂、品牌和传播场景中被真正使用"
      description="如果把这个平台理解成一个内容入口，那么场景页更像是在回答：这些内容除了浏览之外，还能在哪里被看到、被使用、被继续展开。"
    />

    <div class="grid-2 scenario-intro">
      <article class="soft-panel scenario-note">
        <h3>常见使用方式</h3>
        <p>
          如果把这个平台理解成一个内容入口，那么场景页更像是在回答：这些内容除了浏览之外，还能在哪里被看到、被使用、被继续展开。
        </p>
      </article>
      <article class="soft-panel scenario-note">
        <h3>补充说明</h3>
        <p>这里后续很适合补展馆设计图、课程页面截图或文创商城界面，让场景感更强。</p>
      </article>
    </div>

    <div class="grid-4 scenario-app-grid">
      <article v-for="item in scenarioApplications" :key="item.title" class="soft-panel scenario-card">
        <h3>{{ item.title }}</h3>
        <strong>{{ item.subtitle }}</strong>
        <p>{{ item.desc }}</p>
      </article>
    </div>

    <div class="grid-2 scenario-roadmap">
      <article class="soft-panel scenario-list-card">
        <h3>内容如何进入场景</h3>
        <ol>
          <li>先从图谱或导览中理解纹样与文化线索。</li>
          <li>再根据主题需要选择更合适的视觉元素。</li>
          <li>接着延展到海报、包装、课程或展览说明中。</li>
          <li>最后形成更完整的展示、教学或传播内容。</li>
        </ol>
      </article>
      <article class="soft-panel scenario-list-card">
        <h3>为什么值得继续展开</h3>
        <ul>
          <li>在展览里，它可以帮助观众更容易看懂纹样。</li>
          <li>在课堂里，它可以把知识讲解与图像观察结合起来。</li>
          <li>在设计里，它可以作为视觉灵感和延展参考。</li>
          <li>在传播里，它可以形成更完整的内容表达。</li>
        </ul>
      </article>
    </div>

    <div class="grid-3 scenario-lists">
      <article class="soft-panel scenario-list-card">
        <h3>适合的合作对象</h3>
        <ul>
          <li v-for="item in bSideUsers" :key="item">{{ item }}</li>
        </ul>
      </article>
      <article class="soft-panel scenario-list-card">
        <h3>适合的观看者</h3>
        <ul>
          <li v-for="item in cSideUsers" :key="item">{{ item }}</li>
        </ul>
      </article>
      <article class="soft-panel scenario-list-card">
        <h3>可以延展的方向</h3>
        <ul>
          <li v-for="item in businessModels" :key="item">{{ item }}</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue';
import SectionHeading from '@/components/common/SectionHeading.vue';
import { usePlatformContent } from '@/composables/usePlatformContent';

const { content, ensureLoaded } = usePlatformContent();

onMounted(async () => {
  await ensureLoaded();
});

const scenarioApplications = computed(() => content.value?.scenarioApplications || []);
const bSideUsers = computed(() => content.value?.bSideUsers || []);
const cSideUsers = computed(() => content.value?.cSideUsers || []);
const businessModels = computed(() => content.value?.businessModels || []);
</script>

<style scoped lang="scss">
.scenario-intro,
.scenario-app-grid,
.scenario-roadmap,
.scenario-lists {
  margin-top: 1.25rem;
}

.scenario-card,
.scenario-list-card,
.scenario-note {
  padding: 1.35rem;
}

.scenario-card strong {
  display: block;
  color: var(--xiu-accent);
  margin-bottom: 0.55rem;
}

h3 {
  margin: 0 0 0.45rem;
}

p,
ul,
ol {
  margin: 0;
  color: var(--xiu-muted);
  line-height: 1.8;
}

.scenario-list-card ul,
.scenario-list-card ol {
  padding-left: 1.15rem;
}
</style>
