<template>
  <div class="stock-detail">
    <div class="detail-header">
      <button class="back-btn" @click="$router.back()">
        <span class="back-icon">←</span>
        返回
      </button>
      <div class="stock-info">
        <div class="stock-title">
          <h1>{{ quote.symbol }}</h1>
          <span class="stock-name">{{ quote.name }}</span>
        </div>
        <div class="stock-tags">
          <span v-if="quote.change >= 0" class="tag tag-up">涨</span>
          <span v-else class="tag tag-down">跌</span>
        </div>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <LoadingSpinner text="加载行情数据..." />
    </div>

    <div v-else-if="error" class="error-container">
      <div class="error-icon">⚠</div>
      <p class="error-message">{{ error }}</p>
      <button class="btn btn-primary" @click="fetchQuote">重试</button>
    </div>

    <template v-else>
      <div class="quote-section">
        <div class="quote-main">
          <div class="price-display">
            <span class="current-price">{{ quote.current_price || '--' }}</span>
            <span :class="quote.change >= 0 ? 'price-change up' : 'price-change down'">
              {{ quote.change >= 0 ? '+' : '' }}{{ quote.change || 0 }}
              ({{ quote.change_pct >= 0 ? '+' : '' }}{{ quote.change_pct || 0 }}%)
            </span>
          </div>
        </div>

        <div class="quote-details">
          <div class="detail-item">
            <span class="detail-label">开盘</span>
            <span class="detail-value">{{ quote.open || '--' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">最高</span>
            <span class="detail-value highlight-up">{{ quote.high || '--' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">最低</span>
            <span class="detail-value highlight-down">{{ quote.low || '--' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">成交量</span>
            <span class="detail-value">{{ formatVolume(quote.volume) }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">成交额</span>
            <span class="detail-value">{{ formatAmount(quote.amount) }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">市值</span>
            <span class="detail-value">{{ quote.market_cap || '--' }}</span>
          </div>
        </div>
      </div>

      <div class="chart-section">
        <div class="chart-tabs">
          <button
            v-for="tab in chartTabs"
            :key="tab.key"
            :class="['chart-tab', { active: activeChart === tab.key }]"
            @click="activeChart = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>
        <div class="chart-container">
          <div v-if="chartLoading" class="chart-loading">
            <LoadingSpinner text="加载图表..." />
          </div>
          <v-chart v-else :option="currentChartOption" autoresize />
        </div>
        <div class="chart-timeframe">
          <button
            v-for="tf in timeframes"
            :key="tf.value"
            :class="['timeframe-btn', { active: selectedTimeframe === tf.value }]"
            @click="changeTimeframe(tf.value)"
          >
            {{ tf.label }}
          </button>
        </div>
      </div>

      <div class="indicators-section">
        <h2 class="section-title">技术指标</h2>
        <div v-if="indicatorsLoading" class="indicators-loading">
          <LoadingSpinner text="计算指标..." />
        </div>
        <div v-else class="indicators-grid">
          <div class="indicator-card" v-for="(ind, key) in displayedIndicators" :key="key">
            <span class="indicator-label">{{ ind.label }}</span>
            <span :class="['indicator-value', getIndicatorClass(ind.value, ind.threshold)]">
              {{ formatIndicator(ind.value) }}
            </span>
            <div class="indicator-bar">
              <div
                class="indicator-fill"
                :style="{ width: getIndicatorPercent(ind.value, ind.min, ind.max) + '%' }"
              ></div>
            </div>
          </div>
        </div>
      </div>

      <div class="news-section">
        <h2 class="section-title">相关新闻</h2>
        <div v-if="newsLoading" class="news-loading">
          <LoadingSpinner text="加载新闻..." />
        </div>
        <div v-else-if="news.length === 0" class="empty-news">
          <p>暂无相关新闻</p>
        </div>
        <div v-else class="news-list">
          <a v-for="item in news" :key="item.id" :href="item.url" target="_blank" class="news-item">
            <span class="news-title">{{ item.title }}</span>
            <span class="news-date">{{ item.date }}</span>
          </a>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import LoadingSpinner from '@/components/LoadingSpinner.vue'
import api from '@/api'

const route = useRoute()

const symbol = computed(() => route.params.symbol)
const loading = ref(true)
const chartLoading = ref(true)
const indicatorsLoading = ref(true)
const newsLoading = ref(true)
const error = ref('')

const quote = ref({})
const klineData = ref([])
const indicators = ref({})
const news = ref([])

const activeChart = ref('candlestick')
const selectedTimeframe = ref('day')

const chartTabs = [
  { key: 'candlestick', label: 'K线' },
  { key: 'line', label: '走势' },
  { key: 'volume', label: '成交量' },
]

const timeframes = [
  { label: '日', value: 'day' },
  { label: '周', value: 'week' },
  { label: '月', value: 'month' },
  { label: '60分钟', value: '60' },
]

const displayedIndicators = computed(() => {
  const ind = indicators.value
  return [
    { key: 'rsi', label: 'RSI', value: ind.rsi, min: 0, max: 100, threshold: 70 },
    { key: 'kdj_k', label: 'K', value: ind.kdj_k, min: 0, max: 100, threshold: 80 },
    { key: 'kdj_d', label: 'D', value: ind.kdj_d, min: 0, max: 100, threshold: 80 },
    { key: 'macd', label: 'MACD', value: ind.macd_dif, min: -1, max: 1, threshold: 0 },
    { key: '布林', label: 'BOLL', value: ind.bollinger_position, min: 0, max: 100, threshold: 80 },
  ].filter(i => i.value !== undefined)
})

const currentChartOption = computed(() => {
  if (activeChart.value === 'candlestick') {
    return getCandlestickOption()
  } else if (activeChart.value === 'line') {
    return getLineChartOption()
  } else {
    return getVolumeChartOption()
  }
})

function getCandlestickOption() {
  const data = klineData.value
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'cross' }
    },
    legend: {
      data: ['K线', 'MA5', 'MA10', 'MA20'],
      textStyle: { color: '#888' }
    },
    grid: [{ left: '10%', right: '8%', top: '10%', height: '60%' }],
    xAxis: [{
      type: 'category', data: data.map(d => d.date),
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#666' }
    }],
    yAxis: [{
      scale: true, splitLine: { lineStyle: { color: '#222' } },
      axisLine: { lineStyle: { color: '#333' } }
    }],
    series: [
      {
        name: 'K线', type: 'candlestick', data: data.map(d => [d.open, d.close, d.low, d.high]),
        itemStyle: { color: '#ef5350', color0: '#26a69a', borderColor: '#ef5350', borderColor0: '#26a69a' }
      },
      { name: 'MA5', type: 'line', data: data.map(d => d.ma5), smooth: true, lineStyle: { color: '#ff6b6b' } },
      { name: 'MA10', type: 'line', data: data.map(d => d.ma10), smooth: true, lineStyle: { color: '#4ecdc4' } },
      { name: 'MA20', type: 'line', data: data.map(d => d.ma20), smooth: true, lineStyle: { color: '#45b7d1' } },
    ]
  }
}

function getLineChartOption() {
  const data = klineData.value
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '10%', right: '8%', top: '10%', bottom: '15%' },
    xAxis: {
      type: 'category', data: data.map(d => d.date),
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#666' }
    },
    yAxis: {
      scale: true, splitLine: { lineStyle: { color: '#222' } },
      axisLine: { lineStyle: { color: '#333' } }
    },
    series: [{
      type: 'line', data: data.map(d => d.close), smooth: true,
      lineStyle: { color: '#667eea', width: 2 },
      areaStyle: { color: 'rgba(102, 126, 234, 0.2)' }
    }]
  }
}

function getVolumeChartOption() {
  const data = klineData.value
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis' },
    grid: { left: '10%', right: '8%', top: '10%', bottom: '15%' },
    xAxis: {
      type: 'category', data: data.map(d => d.date),
      axisLine: { lineStyle: { color: '#333' } },
      axisLabel: { color: '#666' }
    },
    yAxis: {
      splitLine: { lineStyle: { color: '#222' } },
      axisLine: { lineStyle: { color: '#333' } }
    },
    series: [{
      type: 'bar', data: data.map(d => ({
        value: d.volume,
        itemStyle: { color: d.close >= d.open ? '#ef5350' : '#26a69a' }
      })),
      barWidth: '80%'
    }]
  }
}

async function fetchQuote() {
  loading.value = true
  error.value = ''
  try {
    const response = await api.post('/stocks/quote/realtime', { symbol: symbol.value })
    quote.value = response.data
  } catch (e) {
    error.value = '获取行情数据失败'
    console.error(e)
  } finally {
    loading.value = false
  }
}

async function fetchKline() {
  chartLoading.value = true
  try {
    const response = await api.post('/stocks/kline', {
      symbol: symbol.value,
      period: selectedTimeframe.value,
      adjust: 'qfq'
    })
    klineData.value = response.data.map(d => ({
      date: d.timestamp?.split('T')[0] || d.date,
      open: d.open, high: d.high, low: d.low, close: d.close, volume: d.volume
    }))
  } catch (e) {
    console.error('Failed to fetch kline:', e)
  } finally {
    chartLoading.value = false
  }
}

async function fetchIndicators() {
  indicatorsLoading.value = true
  try {
    const response = await api.post('/indicators/calculate', {
      symbol: symbol.value,
      period: selectedTimeframe.value
    })
    if (response.data?.data?.length > 0) {
      const latest = response.data.data[response.data.data.length - 1]
      indicators.value = latest
    }
  } catch (e) {
    console.error('Failed to fetch indicators:', e)
  } finally {
    indicatorsLoading.value = false
  }
}

function formatVolume(vol) {
  if (!vol) return '--'
  if (vol >= 1e8) return (vol / 1e8).toFixed(2) + '亿'
  if (vol >= 1e4) return (vol / 1e4).toFixed(2) + '万'
  return vol.toFixed(0)
}

function formatAmount(amount) {
  if (!amount) return '--'
  if (amount >= 1e8) return (amount / 1e8).toFixed(2) + '亿'
  if (amount >= 1e4) return (amount / 1e4).toFixed(2) + '万'
  return amount.toFixed(0)
}

function formatIndicator(value) {
  if (value === undefined || value === null) return '--'
  return typeof value === 'number' ? value.toFixed(2) : value
}

function getIndicatorClass(value, threshold) {
  if (value === undefined) return ''
  if (threshold === 70 || threshold === 80) return value > threshold ? 'ind-overbought' : value < (100 - threshold) ? 'ind-oversold' : ''
  return value > threshold ? 'ind-positive' : value < threshold ? 'ind-negative' : ''
}

function getIndicatorPercent(value, min, max) {
  if (value === undefined) return 50
  return Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100))
}

function changeTimeframe(tf) {
  selectedTimeframe.value = tf
  fetchKline()
  fetchIndicators()
}

onMounted(() => {
  fetchQuote()
  fetchKline()
  fetchIndicators()
  newsLoading.value = false
})

watch(symbol, () => {
  fetchQuote()
  fetchKline()
  fetchIndicators()
})
</script>

<style scoped>
.stock-detail {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  animation: fade-in 0.3s ease;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.detail-header {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
}

.stock-info {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.stock-title {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.stock-title h1 {
  font-size: 28px;
  font-weight: 700;
}

.stock-name {
  font-size: 18px;
  color: #888;
}

.stock-tags {
  display: flex;
  gap: 8px;
}

.tag {
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
}

.tag-up { background: rgba(239, 83, 80, 0.2); color: #ef5350; }
.tag-down { background: rgba(38, 166, 154, 0.2); color: #26a69a; }

.quote-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
}

.quote-main {
  margin-bottom: 24px;
}

.price-display {
  display: flex;
  align-items: baseline;
  gap: 16px;
}

.current-price {
  font-size: 48px;
  font-weight: 700;
  font-family: 'Fira Code', monospace;
}

.price-change {
  font-size: 20px;
  font-weight: 500;
}

.price-change.up { color: #ef5350; }
.price-change.down { color: #26a69a; }

.quote-details {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: #666;
}

.detail-value {
  font-size: 16px;
  font-weight: 500;
  font-family: 'Fira Code', monospace;
}

.highlight-up { color: #ef5350; }
.highlight-down { color: #26a69a; }

.chart-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
}

.chart-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.chart-tab {
  padding: 8px 20px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #888;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.chart-tab.active {
  background: linear-gradient(135deg, #667eea, #764ba2);
  border-color: transparent;
  color: #fff;
}

.chart-tab:hover:not(.active) {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.chart-container {
  height: 450px;
  margin-bottom: 16px;
}

.chart-loading {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-timeframe {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.timeframe-btn {
  padding: 6px 16px;
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #666;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.timeframe-btn.active {
  background: rgba(102, 126, 234, 0.2);
  border-color: #667eea;
  color: #667eea;
}

.timeframe-btn:hover:not(.active) {
  color: #fff;
  border-color: rgba(255, 255, 255, 0.2);
}

.indicators-section {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
}

.indicators-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 16px;
}

.indicator-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.indicator-label {
  font-size: 13px;
  color: #888;
}

.indicator-value {
  font-size: 20px;
  font-weight: 600;
  font-family: 'Fira Code', monospace;
}

.ind-overbought { color: #ef5350; }
.ind-oversold { color: #26a69a; }
.ind-positive { color: #667eea; }
.ind-negative { color: #ffca28; }

.indicator-bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 2px;
  overflow: hidden;
}

.indicator-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.loading-container, .error-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 20px;
  text-align: center;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.error-message {
  color: #888;
  margin-bottom: 24px;
}

.empty-news {
  text-align: center;
  color: #666;
  padding: 40px;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.news-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  color: #fff;
  text-decoration: none;
  transition: all 0.2s;
}

.news-item:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.1);
}

.news-title {
  flex: 1;
  font-size: 14px;
}

.news-date {
  font-size: 12px;
  color: #666;
  margin-left: 16px;
  white-space: nowrap;
}

@media (max-width: 900px) {
  .quote-details { grid-template-columns: repeat(3, 1fr); }
  .indicators-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 600px) {
  .stock-detail { padding: 16px; }
  .detail-header { flex-direction: column; align-items: flex-start; }
  .quote-details { grid-template-columns: repeat(2, 1fr); }
  .indicators-grid { grid-template-columns: repeat(2, 1fr); }
  .current-price { font-size: 36px; }
  .chart-container { height: 300px; }
}
</style>
