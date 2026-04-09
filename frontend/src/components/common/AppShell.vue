<template>
  <div class="shell">
    <header class="shell__header">
      <div class="shell__header-inner">
        <RouterLink class="shell__brand" to="/">
          <span class="shell__brand-mark">DONG EMBROIDERY</span>
          <span class="shell__brand-title">绣见侗韵</span>
        </RouterLink>
        <nav class="shell__nav">
          <RouterLink
            v-for="item in navItems"
            :key="item.to"
            :to="item.to"
            class="shell__nav-link"
            :class="{ 'shell__nav-link--active': route.path === item.to }"
          >
            {{ item.label }}
          </RouterLink>
        </nav>
      </div>
    </header>

    <main class="shell__main">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { RouterLink, useRoute } from 'vue-router';

const route = useRoute();

const navItems = [
  { label: '首页', to: '/' },
  { label: '纹样图谱', to: '/atlas' },
  { label: '文化导览', to: '/guide' },
  { label: '设计工作台', to: '/studio' },
  { label: '文创展陈', to: '/showcase' },
  { label: '场景落地', to: '/scenarios' },
  { label: '幕后方法', to: '/method' },
];
</script>
