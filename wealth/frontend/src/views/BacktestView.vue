<template>
  <div class="backtest-view">
    <h1>策略回测</h1>
    <div class="config-panel">
      <div class="form-row">
        <label>股票代码</label>
        <input v-model="config.symbol" placeholder="如: 000001" />
      </div>
      <div class="form-row">
        <label>策略</label>
        <select v-model="config.strategy">
          <option v-for="s in strategies" :key="s.name" :value="s.name">{{ s.description }}</option>
        </select>
      </div>
      <div class="form-row">
        <label>开始日期</label>
        <input v-model="config.start_date" type="date" />
      </div>
      <div class="form-row">
        <label>结束日期</label>
        <input v-model="config.end_date" type="date" />
      </div>
      <div class="form-row">
        <label>初始资金</label>
        <input v-model.number="config.initial_capital" type="number" />
      </div>
      <button class="run-btn" @click="runBacktest">运行回测</button>
    </div>

    <div v-if="result" class="result-panel">
      <h2>回测结果: {{ result.strategy_name }}</h2>
      <div class="stats-grid">
        <div class="stat">
          <span class="label">总收益率</span>
          <span :class="result.total_return >= 0 ? 'up' : 'down'">{{ result.total_return.toFixed(2) }}%</span>
        </div>
        <div class="stat">
          <span class="label">年化收益率</span>
          <span :class="result.annualized_return >= 0 ? 'up' : 'down'">{{ result.annualized_return.toFixed(2) }}%</span>
        </div>
        <div class="stat">
          <span class="label">夏普比率</span>
          <span>{{ result.sharpe_ratio.toFixed(2) }}</span>
        </div>
        <div class="stat">
          <span class="label">最大回撤</span>
          <span class="down">{{ result.max_drawdown.toFixed(2) }}%</span>
        </div>
        <div class="stat">
          <span class="label">胜率</span>
          <span>{{ result.win_rate.toFixed(1) }}%</span>
        </div>
        <div class="stat">
          <span class="label">交易次数</span>
          <span>{{ result.total_trades }}</span>
        </div>
      </div>
      <div class="chart-container">
        <v-chart :option="equityChartOption" autoresize />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import * as echarts from 'echarts'
import { backtestApi, strategyApi } from '@/api'

const strategies = ref([])
const config = ref({
  symbol: '000001',
  strategy: 'macd',
  start_date: '2023-01-01',
  end_date: '2024-01-01',
  initial_capital: 100000
})
const result = ref(null)
const equityCurve = ref([])

const equityChartOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: '10%', right: '10%', bottom: '15%', top: '10%' },
  xAxis: { type: 'category', data: equityCurve.value.map(d => d.date) },
  yAxis: { type: 'value' },
  series: [{
    name: '账户价值',
    type: 'line',
    data: equityCurve.value.map(d => d.value),
    smooth: true,
    areaStyle: { color: 'rgba(102, 126, 234, 0.3)' }
  }]
}))

onMounted(async () => {
  try {
    const res = await strategyApi.list()
    strategies.value = res.strategies || []
  } catch (e) {
    console.error(e)
  }
})

const runBacktest = async () => {
  try {
    result.value = await backtestApi.run({
      ...config.value,
      start_date: config.value.start_date.replace(/-/g, ''),
      end_date: config.value.end_date.replace(/-/g, '')
    })
    equityCurve.value = await backtestApi.equityCurve({
      ...config.value,
      start_date: config.value.start_date.replace(/-/g, ''),
      end_date: config.value.end_date.replace(/-/g, '')
    })
  } catch (e) {
    console.error(e)
  }
}
</script>

<style lang="scss" scoped>
.backtest-view { padding: 40px; color: #fff; }
.config-panel {
  background: rgba(255,255,255,0.05);
  border-radius: 16px;
  padding: 24px;
  margin: 24px 0;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  .form-row {
    display: flex;
    flex-direction: column;
    gap: 8px;
    label { color: #888; font-size: 14px; }
    input, select {
      padding: 12px;
      border-radius: 8px;
      border: 1px solid rgba(255,255,255,0.2);
      background: rgba(255,255,255,0.05);
      color: #fff;
    }
  }
  .run-btn {
    grid-column: 1 / -1;
    padding: 16px;
    border-radius: 12px;
    border: none;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    font-size: 16px;
    cursor: pointer;
  }
}
.result-panel {
  margin-top: 32px;
  h2 { margin-bottom: 24px; }
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 32px;
  .stat {
    background: rgba(255,255,255,0.05);
    padding: 20px;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    .label { color: #888; font-size: 12px; }
    font-size: 20px;
    .up { color: #ef5350; }
    .down { color: #26a69a; }
  }
}
.chart-container { height: 400px; background: rgba(255,255,255,0.05); border-radius: 16px; }
</style>
