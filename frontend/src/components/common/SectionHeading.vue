<template>
  <div class="section-heading">
    <span v-if="eyebrow" class="section-heading__eyebrow">{{ eyebrow }}</span>
    <h2 class="section-heading__title">{{ title }}</h2>
    <p v-if="description" class="section-heading__desc">{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  description?: string;
  eyebrow?: string;
}>();
</script>

<style scoped lang="scss">
.section-heading__title {
  font-weight: 600;
}
</style>
