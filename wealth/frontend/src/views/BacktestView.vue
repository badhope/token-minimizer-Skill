<template>
  <div class="backtest-view">
    <div class="page-header">
      <h1 class="page-title">策略回测</h1>
      <p class="page-subtitle">验证交易策略的有效性和历史表现</p>
    </div>

    <div class="config-panel">
      <div class="config-header">
        <h2>回测配置</h2>
      </div>
      <div class="config-grid">
        <div class="form-row">
          <label>股票代码</label>
          <input v-model="config.symbol" placeholder="如: 000001" class="input" />
        </div>
        <div class="form-row">
          <label>交易策略</label>
          <select v-model="config.strategy" class="input">
            <option v-for="s in strategies" :key="s.name" :value="s.name">
              {{ s.description }}
            </option>
          </select>
        </div>
        <div class="form-row">
          <label>开始日期</label>
          <input v-model="config.start_date" type="date" class="input" />
        </div>
        <div class="form-row">
          <label>结束日期</label>
          <input v-model="config.end_date" type="date" class="input" />
        </div>
        <div class="form-row">
          <label>初始资金 (元)</label>
          <input v-model.number="config.initial_capital" type="number" class="input" />
        </div>
        <div class="form-row form-row-btn">
          <button class="btn btn-primary run-btn" @click="runBacktest" :disabled="loading">
            <span v-if="loading" class="spinner"></span>
            {{ loading ? '回测中...' : '运行回测' }}
          </button>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <LoadingSpinner text="正在执行回测，请稍候..." />
    </div>

    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠</div>
      <p class="error-message">{{ error }}</p>
      <button class="btn btn-secondary" @click="error = ''">关闭</button>
    </div>

    <div v-else-if="result" class="result-panel">
      <div class="result-header">
        <h2>回测结果: <span class="strategy-name">{{ result.strategy_name }}</span></h2>
        <div class="result-badge" :class="result.total_return >= 0 ? 'positive' : 'negative'">
          {{ result.total_return >= 0 ? '盈利' : '亏损' }}
        </div>
      </div>

      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon">📈</div>
          <div class="stat-info">
            <span class="stat-label">总收益率</span>
            <span :class="['stat-value', result.total_return >= 0 ? 'up' : 'down']">
              {{ result.total_return >= 0 ? '+' : '' }}{{ result.total_return.toFixed(2) }}%
            </span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-info">
            <span class="stat-label">年化收益率</span>
            <span :class="['stat-value', result.annualized_return >= 0 ? 'up' : 'down']">
              {{ result.annualized_return >= 0 ? '+' : '' }}{{ result.annualized_return.toFixed(2) }}%
            </span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">⚡</div>
          <div class="stat-info">
            <span class="stat-label">夏普比率</span>
            <span class="stat-value">{{ result.sharpe_ratio.toFixed(2) }}</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">📉</div>
          <div class="stat-info">
            <span class="stat-label">最大回撤</span>
            <span class="stat-value down">{{ result.max_drawdown.toFixed(2) }}%</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🎯</div>
          <div class="stat-info">
            <span class="stat-label">胜率</span>
            <span class="stat-value">{{ result.win_rate.toFixed(1) }}%</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🔄</div>
          <div class="stat-info">
            <span class="stat-label">交易次数</span>
            <span class="stat-value">{{ result.total_trades }}</span>
          </div>
        </div>
      </div>

      <div class="chart-section">
        <h3>资金曲线</h3>
        <div class="chart-container">
          <v-chart :option="equityChartOption" autoresize />
        </div>
      </div>

      <div v-if="result.trades && result.trades.length > 0" class="trades-section">
        <h3>交易记录</h3>
        <div class="trades-table">
          <table>
            <thead>
              <tr>
                <th>日期</th>
                <th>类型</th>
                <th>价格</th>
                <th>数量</th>
                <th>金额</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(trade, idx) in result.trades.slice(0, 10)" :key="idx">
                <td>{{ trade.date }}</td>
                <td>
                  <span :class="['trade-type', trade.type === 'buy' ? 'buy' : 'sell']">
                    {{ trade.type === 'buy' ? '买入' : '卖出' }}
                  </span>
                </td>
                <td>{{ trade.price }}</td>
                <td>{{ trade.quantity }}</td>
                <td>{{ trade.amount }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
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
const loading = ref(false)
const error = ref('')

const equityChartOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' }
  },
  grid: { left: '10%', right: '8%', top: '10%', bottom: '15%' },
  xAxis: {
    type: 'category',
    data: equityCurve.value.map(d => d.date),
    axisLine: { lineStyle: { color: '#333' } },
    axisLabel: { color: '#666' }
  },
  yAxis: {
    type: 'value',
    splitLine: { lineStyle: { color: '#222' } },
    axisLine: { lineStyle: { color: '#333' } }
  },
  series: [{
    name: '账户价值',
    type: 'line',
    data: equityCurve.value.map(d => d.value),
    smooth: true,
    lineStyle: { color: '#667eea', width: 2 },
    areaStyle: { color: 'rgba(102, 126, 234, 0.2)' }
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
  loading.value = true
  error.value = ''
  try {
    const res = await backtestApi.run({
      ...config.value,
      start_date: config.value.start_date.replace(/-/g, ''),
      end_date: config.value.end_date.replace(/-/g, '')
    })
    result.value = res

    const equity = await backtestApi.equityCurve({
      ...config.value,
      start_date: config.value.start_date.replace(/-/g, ''),
      end_date: config.value.end_date.replace(/-/g, '')
    })
    equityCurve.value = equity
  } catch (e) {
    error.value = e.response?.data?.detail || '回测执行失败'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.backtest-view {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  animation: page-enter 0.4s ease;
}

@keyframes page-enter {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  margin-bottom: 32px;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 8px;
}

.page-subtitle {
  color: #888;
  font-size: 16px;
}

.config-panel {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
}

.config-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
}

.config-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-row label {
  color: #888;
  font-size: 13px;
  font-weight: 500;
}

.form-row-btn {
  display: flex;
  align-items: flex-end;
}

.input {
  padding: 12px 16px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  font-size: 14px;
  transition: all 0.2s;
}

.input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.input::placeholder {
  color: #555;
}

.run-btn {
  width: 100%;
  padding: 14px;
  border-radius: 10px;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s;
}

.run-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.run-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-container {
  display: flex;
  justify-content: center;
  padding: 80px 20px;
}

.error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
  text-align: center;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-message {
  color: #888;
  margin-bottom: 24px;
  font-size: 16px;
}

.result-panel {
  animation: fade-in 0.4s ease;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.result-header h2 {
  font-size: 20px;
  font-weight: 600;
}

.strategy-name {
  color: #667eea;
}

.result-badge {
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
}

.result-badge.positive {
  background: rgba(38, 166, 154, 0.2);
  color: #26a69a;
}

.result-badge.negative {
  background: rgba(239, 83, 80, 0.2);
  color: #ef5350;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: flex-start;
  gap: 12px;
  transition: all 0.2s;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.08);
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 24px;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  color: #666;
  font-size: 12px;
}

.stat-value {
  font-size: 18px;
  font-weight: 700;
  font-family: 'Fira Code', monospace;
}

.stat-value.up { color: #ef5350; }
.stat-value.down { color: #26a69a; }

.chart-section, .trades-section {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
}

.chart-section h3, .trades-section h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 20px;
}

.chart-container {
  height: 400px;
}

.trades-table {
  overflow-x: auto;
}

.trades-table table {
  width: 100%;
  border-collapse: collapse;
}

.trades-table th,
.trades-table td {
  padding: 12px 16px;
  text-align: left;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.trades-table th {
  color: #666;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.trades-table td {
  font-size: 14px;
  color: #ccc;
}

.trade-type {
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.trade-type.buy {
  background: rgba(239, 83, 80, 0.2);
  color: #ef5350;
}

.trade-type.sell {
  background: rgba(38, 166, 154, 0.2);
  color: #26a69a;
}

@media (max-width: 1200px) {
  .stats-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 900px) {
  .config-grid { grid-template-columns: repeat(2, 1fr); }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 600px) {
  .backtest-view { padding: 16px; }
  .config-grid { grid-template-columns: 1fr; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .chart-container { height: 300px; }
  .page-title { font-size: 24px; }
}
</style>
