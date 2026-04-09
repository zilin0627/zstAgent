<template>
  <section class="hero">
    <div class="hero__intro">
      <p class="hero__mark">侗绣文化体验与设计转化平台</p>
      <h1 class="hero__title">看见纹样，听懂文化，再走向设计转化</h1>
      <p class="hero__desc">
        这里不是功能堆叠式工具页，而是一个以侗绣纹样为线索展开的文化体验入口。
        你可以先看纹样、再听讲解，也可以继续进入设计工作台和文创展陈，理解传统图样如何被转化为今天可展示、可传播的内容。
      </p>

      <div class="hero__actions">
        <RouterLink class="hero__button hero__button--solid" to="/atlas">进入纹样图谱</RouterLink>
        <RouterLink class="hero__button" to="/guide">进入文化导览</RouterLink>
        <RouterLink class="hero__button" to="/studio">进入设计工作台</RouterLink>
      </div>
    </div>

    <div class="hero__media soft-panel">
      <img :src="assetUrl('assets/workflow/boards/board_1.png')" alt="侗绣平台主视觉展板" class="hero__image" />
      <div class="hero__media-meta">
        <div class="hero__summary">
          <strong>体验路径</strong>
          <p>看纹样｜听讲解｜做转化</p>
        </div>
        <div class="hero__summary">
          <strong>页面入口</strong>
          <p>图谱、导览、工作台、展陈、场景、方法</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { RouterLink } from 'vue-router';
import { assetUrl } from '@/services/api';
</script>

<style scoped lang="scss">
.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(320px, 0.95fr);
  gap: 2rem;
  padding: 0 0 1rem;
  border-bottom: 1px solid var(--xiu-line);
}

.hero__intro {
  display: grid;
  align-content: start;
  gap: 0.9rem;
}

.hero__mark {
  margin: 0;
  font-size: 0.78rem;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--xiu-accent);
}

.hero__title {
  margin: 0;
  font-size: var(--xiu-text-display);
  line-height: 1.02;
  max-width: 10ch;
  letter-spacing: -0.02em;
}

.hero__desc {
  margin: 0;
  max-width: 56ch;
  color: var(--xiu-muted);
  line-height: 1.95;
}

.hero__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
  margin-top: 0.35rem;
}

.hero__button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 46px;
  padding: 0.75rem 1.2rem;
  border: 1px solid var(--xiu-line-strong);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.5);
  color: var(--xiu-ink);
  transition: transform 180ms ease, background 180ms ease;
}

.hero__button:hover {
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 0.78);
}

.hero__button--solid {
  background: var(--xiu-primary);
  color: white;
  border-color: var(--xiu-primary);
}

.hero__button--solid:hover {
  background: color-mix(in srgb, var(--xiu-primary) 88%, black);
}

.hero__media {
  display: grid;
  gap: 1rem;
  padding: 1rem;
}

.hero__image {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  display: block;
  border-radius: 20px;
}

.hero__media-meta {
  display: grid;
  gap: 0.9rem;
}

.hero__summary strong {
  display: block;
  margin-bottom: 0.35rem;
  font-size: 0.98rem;
}

.hero__summary p {
  margin: 0;
  color: var(--xiu-muted);
  line-height: 1.8;
}

@media (max-width: 920px) {
  .hero {
    grid-template-columns: 1fr;
  }
}
</style>
