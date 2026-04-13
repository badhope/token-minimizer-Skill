<template>
  <div class="skeleton-loader" :class="variant">
    <div v-if="variant === 'text'" class="skeleton-text"></div>
    <div v-else-if="variant === 'avatar'" class="skeleton-avatar"></div>
    <div v-else-if="variant === 'card'" class="skeleton-card">
      <div class="skeleton-card-header"></div>
      <div class="skeleton-card-body"></div>
    </div>
    <div v-else-if="variant === 'chart'" class="skeleton-chart"></div>
    <div v-else class="skeleton-box"></div>
  </div>
</template>

<script setup>
defineProps({
  variant: {
    type: String,
    default: 'box',
    validator: (v) => ['box', 'text', 'avatar', 'card', 'chart'].includes(v)
  }
})
</script>

<style scoped>
.skeleton-loader {
  animation: skeleton-pulse 1.5s ease-in-out infinite;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.skeleton-box {
  width: 100%;
  height: 100px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
}

.skeleton-text {
  height: 16px;
  width: 100%;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
  margin-bottom: 8px;
}

.skeleton-text:last-child {
  width: 60%;
}

.skeleton-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
}

.skeleton-card {
  padding: 20px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
}

.skeleton-card-header {
  height: 24px;
  width: 40%;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  margin-bottom: 16px;
}

.skeleton-card-body {
  height: 80px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.skeleton-chart {
  width: 100%;
  height: 300px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  position: relative;
  overflow: hidden;
}

.skeleton-chart::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(102, 126, 234, 0.1) 50%,
    transparent 100%
  );
  animation: skeleton-shimmer 1.5s infinite;
}

@keyframes skeleton-shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}
</style>
