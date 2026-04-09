<template>
  <section class="section-block home-intro">
    <HeroSection />
  </section>

  <section class="section-block home-paths">
    <div class="home-section-head">
      <p class="home-section-mark">体验路径</p>
      <h2>先看纹样、再听讲解，也可以继续进入设计工作台和文创展陈。</h2>
    </div>
    <div class="home-path-list">
      <article v-for="item in paths" :key="item.title" class="home-path-item">
        <span>{{ item.step }}</span>
        <div>
          <h3>{{ item.title }}</h3>
          <p>{{ item.desc }}</p>
        </div>
      </article>
    </div>
  </section>

  <section class="section-block home-value-grid">
    <article>
      <p class="home-section-mark">平台价值</p>
      <h2>以侗绣纹样为线索展开文化体验、理解与设计转化。</h2>
    </article>
    <article v-for="item in values" :key="item.title">
      <h3>{{ item.title }}</h3>
      <p>{{ item.desc }}</p>
    </article>
  </section>

  <section class="section-block home-modules">
    <div class="home-section-head">
      <p class="home-section-mark">页面入口</p>
      <h2>从纹样内容、文化理解到设计转化与应用展示，按旧版结构继续浏览。</h2>
    </div>
    <div class="home-module-list">
      <article v-for="item in modules" :key="item.title" class="home-module-item">
        <div class="home-module-item__meta">{{ item.tag }}</div>
        <div class="home-module-item__body">
          <h3>{{ item.title }}</h3>
          <p>{{ item.desc }}</p>
        </div>
        <RouterLink :to="item.to" class="home-module-item__link">进入</RouterLink>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';
import HeroSection from '@/components/home/HeroSection.vue';

const paths = [
  { step: '路径一', title: '看纹样', desc: '先从典型图样、关键词和扫图观察中建立第一印象。' },
  { step: '路径二', title: '听讲解', desc: '通过文化导览理解图样背后的构成特点、寓意和使用场景。' },
  { step: '路径三', title: '做转化', desc: '进入设计工作台和文创展陈，继续完成设计延展与展示表达。' },
];

const values = [
  { title: '整理纹样内容', desc: '把典型纹样、扫图观察和图像特征组织成更容易浏览的内容结构。' },
  { title: '帮助观众理解', desc: '用导览、问答和展签式表达降低理解门槛，让观众先看懂再深入。' },
  { title: '支持设计转化', desc: '把纹样进一步带到设计工作台、文创展陈和真实应用场景中。' },
];

const modules = [
  { tag: '纹样内容', title: '纹样图谱', desc: '查看典型侗绣纹样的分类、图像特征与少量关键词。', to: '/atlas' },
  { tag: '文化理解', title: '文化导览', desc: '通过预设问题、导览结果和展签式内容理解纹样背景。', to: '/guide' },
  { tag: '设计转化', title: '设计工作台', desc: '选择纹样、方向和风格，快速生成更适合方案讨论的设计提案。', to: '/studio' },
  { tag: '文创展陈', title: '文创展陈', desc: '按平面、产品和生成延展分组浏览作品，强化展陈感与作品感。', to: '/showcase' },
  { tag: '应用展示', title: '场景落地', desc: '展示平台如何进入展馆、课堂、品牌和传播等真实场景。', to: '/scenarios' },
  { tag: '方法说明', title: '幕后方法', desc: '解释为什么做、如何整理、AI 做了什么，以及最终输出了什么。', to: '/method' },
];
</script>

<style scoped lang="scss">
.home-intro {
  margin-bottom: 2.5rem;
}

.home-section-head {
  display: grid;
  gap: 0.45rem;
  margin-bottom: 1.5rem;
}

.home-section-head h2,
.home-value-grid h2 {
  margin: 0;
  font-size: var(--xiu-text-h2);
  line-height: 1.28;
  max-width: 20ch;
}

.home-section-mark {
  margin: 0;
  font-size: 0.76rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--xiu-accent);
}

.home-path-list,
.home-module-list {
  border-top: 1px solid var(--xiu-line);
}

.home-path-item,
.home-module-item {
  display: grid;
  grid-template-columns: 110px minmax(0, 1fr);
  gap: 1.25rem;
  padding: 1rem 0;
  border-bottom: 1px solid var(--xiu-line);
}

.home-module-item {
  grid-template-columns: 120px minmax(0, 1fr) auto;
  align-items: start;
}

.home-path-item span,
.home-module-item__meta {
  font-size: 0.82rem;
  color: var(--xiu-accent);
}

.home-path-item h3,
.home-module-item h3,
.home-value-grid h3 {
  margin: 0 0 0.35rem;
  font-size: 1.1rem;
}

.home-path-item p,
.home-module-item p,
.home-value-grid p {
  margin: 0;
  color: var(--xiu-muted);
  line-height: 1.9;
}

.home-module-item__link {
  align-self: center;
  padding-bottom: 0.12rem;
  border-bottom: 1px solid var(--xiu-line-strong);
  font-size: 0.95rem;
}

.home-value-grid {
  display: grid;
  grid-template-columns: 1.15fr 1fr 1fr 1fr;
  gap: 1.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--xiu-line);
}

@media (max-width: 920px) {
  .home-value-grid,
  .home-path-item,
  .home-module-item {
    grid-template-columns: 1fr;
  }

  .home-module-item__link {
    justify-self: start;
  }
}
</style>
