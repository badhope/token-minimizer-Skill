<template>
  <div class="alerts-view">
    <h1>价格预警</h1>
    <div class="create-panel">
      <input v-model="newAlert.symbol" placeholder="股票代码" />
      <select v-model="newAlert.alert_type">
        <option value="PRICE_ABOVE">价格上穿</option>
        <option value="PRICE_BELOW">价格下穿</option>
        <option value="PERCENT_CHANGE">涨跌幅</option>
      </select>
      <input v-model.number="newAlert.threshold_value" placeholder="阈值" type="number" />
      <button @click="createAlert">创建预警</button>
    </div>
    <div class="alerts-list">
      <div v-for="alert in alerts" :key="alert.alert_id" class="alert-item">
        <div class="alert-info">
          <span class="symbol">{{ alert.symbol }}</span>
          <span class="type">{{ alert.alert_type }}</span>
        </div>
        <div class="condition">{{ alert.condition }}</div>
        <div :class="'level ' + alert.level.toLowerCase()">{{ alert.level }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { alertApi } from '@/api'

const alerts = ref([])
const newAlert = ref({
  symbol: '',
  alert_type: 'PRICE_ABOVE',
  condition: '',
  threshold_value: 0,
  level: 'WARNING'
})

const loadAlerts = async () => {
  try {
    const res = await alertApi.list()
    alerts.value = res.alerts || []
  } catch (e) {
    console.error(e)
  }
}

const createAlert = async () => {
  try {
    newAlert.value.condition = `${newAlert.value.symbol} ${newAlert.value.alert_type}`
    await alertApi.create(newAlert.value)
    await loadAlerts()
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadAlerts)
</script>

<style lang="scss" scoped>
.alerts-view { padding: 40px; color: #fff; }
.create-panel {
  display: flex;
  gap: 16px;
  margin: 24px 0;
  input, select {
    padding: 12px 16px;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.2);
    background: rgba(255,255,255,0.05);
    color: #fff;
  }
  button {
    padding: 12px 32px;
    border-radius: 8px;
    border: none;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    cursor: pointer;
  }
}
.alerts-list { display: flex; flex-direction: column; gap: 12px; }
.alert-item {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 20px 24px;
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  .symbol { font-weight: bold; font-size: 18px; margin-right: 12px; }
  .type { color: #888; }
  .condition { flex: 1; color: #aaa; }
  .level {
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 12px;
    &.info { background: rgba(33,150,243,0.2); color: #2196f3; }
    &.warning { background: rgba(255,152,0,0.2); color: #ff9800; }
    &.critical { background: rgba(244,67,54,0.2); color: #f44336; }
  }
}
</style>
