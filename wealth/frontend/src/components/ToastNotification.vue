<template>
  <Teleport to="body">
    <TransitionGroup name="toast" tag="div" class="toast-container">
      <div
        v-for="toast in toasts"
        :key="toast.id"
        :class="['toast-item', `toast-${toast.type}`]"
      >
        <div class="toast-icon">
          <span v-if="toast.type === 'success'">✓</span>
          <span v-else-if="toast.type === 'error'">✕</span>
          <span v-else-if="toast.type === 'warning'">⚠</span>
          <span v-else>ℹ</span>
        </div>
        <div class="toast-content">
          <p v-if="toast.title" class="toast-title">{{ toast.title }}</p>
          <p class="toast-message">{{ toast.message }}</p>
        </div>
        <button class="toast-close" @click="removeToast(toast.id)">×</button>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

const toasts = ref([])
let toastId = 0

function addToast({ type = 'info', title = '', message, duration = 4000 }) {
  const id = ++toastId
  toasts.value.push({ id, type, title, message })

  if (duration > 0) {
    setTimeout(() => removeToast(id), duration)
  }

  return id
}

function removeToast(id) {
  const index = toasts.value.findIndex(t => t.id === id)
  if (index > -1) {
    toasts.value.splice(index, 1)
  }
}

function success(message, title = '') {
  return addToast({ type: 'success', message, title })
}

function error(message, title = '错误') {
  return addToast({ type: 'error', message, title })
}

function warning(message, title = '警告') {
  return addToast({ type: 'warning', message, title })
}

function info(message, title = '') {
  return addToast({ type: 'info', message, title })
}

defineExpose({ addToast, removeToast, success, error, warning, info })
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.toast-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: var(--bg-secondary, #131722);
  border-radius: 12px;
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  min-width: 320px;
  max-width: 420px;
}

.toast-success {
  border-left: 4px solid var(--success, #26a69a);
}

.toast-error {
  border-left: 4px solid var(--error, #ef5350);
}

.toast-warning {
  border-left: 4px solid var(--warning, #ffca28);
}

.toast-info {
  border-left: 4px solid var(--primary, #667eea);
}

.toast-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 14px;
  flex-shrink: 0;
}

.toast-success .toast-icon {
  background: rgba(38, 166, 154, 0.2);
  color: var(--success, #26a69a);
}

.toast-error .toast-icon {
  background: rgba(239, 83, 80, 0.2);
  color: var(--error, #ef5350);
}

.toast-warning .toast-icon {
  background: rgba(255, 202, 40, 0.2);
  color: var(--warning, #ffca28);
}

.toast-info .toast-icon {
  background: rgba(102, 126, 234, 0.2);
  color: var(--primary, #667eea);
}

.toast-content {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
}

.toast-message {
  font-size: 14px;
  color: var(--text-secondary, #a0a0a0);
  line-height: 1.4;
}

.toast-close {
  background: none;
  border: none;
  color: var(--text-muted, #666);
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: color 0.2s;
}

.toast-close:hover {
  color: var(--text-primary, #fff);
}

.toast-enter-active {
  animation: toast-in 0.3s ease;
}

.toast-leave-active {
  animation: toast-out 0.3s ease;
}

@keyframes toast-in {
  from {
    opacity: 0;
    transform: translateX(100%);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes toast-out {
  from {
    opacity: 1;
    transform: translateX(0);
  }
  to {
    opacity: 0;
    transform: translateX(100%);
  }
}
</style>
