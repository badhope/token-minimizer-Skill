<template>
  <div class="stock-detail">
    <div class="header">
      <button class="back" @click="$router.back()">返回</button>
      <h1>{{ quote.symbol }} {{ quote.name }}</h1>
    </div>
    <div class="quote-card">
      <div class="price">{{ quote.current_price }}</div>
      <div :class="quote.change >= 0 ? 'up' : 'down'">
        {{ quote.change >= 0 ? '+' : '' }}{{ quote.change }} ({{ quote.change_pct }}%)
      </div>
      <div class="details">
        <span>开盘: {{ quote.open }}</span>
        <span>最高: {{ quote.high }}</span>
        <span>最低: {{ quote.low }}</span>
        <span>成交量: {{ formatVolume(quote.volume) }}</span>
      </div>
    </div>
    <div class="chart-container">
      <v-chart :option="chartOption" autoresize />
    </div>
    <div class="indicators">
      <h3>技术指标</h3>
      <div class="indicator-grid" v-if="indicators.length">
        <div v-for="ind in indicators" :key="ind.timestamp" class="indicator-item">
          <span class="label">{{ ind.macd_dif ? 'MACD' : ind.kdj_k ? 'KDJ' : ind.rsi ? 'RSI' : '' }}</span>
          <span>{{ ind.macd_dif || ind.kdj_k || ind.rsi || '' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import * as echarts from 'echarts'
import { stockApi, indicatorApi } from '@/api'

const route = useRoute()
const symbol = computed(() => route.params.symbol)
const quote = ref({})
const klineData = ref([])
const indicators = ref([])

const formatVolume = (v) => {
  if (!v) return '0'
  if (v >= 1e8) return (v / 1e8).toFixed(2) + '亿'
  if (v >= 1e4) return (v / 1e4).toFixed(2) + '万'
  return v
}

const chartOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  grid: { left: '10%', right: '10%', bottom: '15%', top: '10%' },
  xAxis: { type: 'category', data: klineData.value.map(d => d.timestamp) },
  yAxis: [
    { type: 'value', scale: true },
    { type: 'value', scale: true, show: false }
  ],
  series: [
    {
      name: 'K线',
      type: 'candlestick',
      data: klineData.value.map(d => [d.open, d.close, d.low, d.high]),
      itemStyle: { color: '#ef5350', color0: '#26a69a' }
    },
    {
      name: 'MA5',
      type: 'line',
      data: klineData.value.map(d => d.ma5),
      smooth: true,
      lineStyle: { width: 1 },
      symbol: 'none'
    },
    {
      name: 'MA10',
      type: 'line',
      data: klineData.value.map(d => d.ma10),
      smooth: true,
      lineStyle: { width: 1 },
      symbol: 'none'
    }
  ]
}))

onMounted(async () => {
  try {
    quote.value = await stockApi.realtime(symbol.value)
    const kline = await stockApi.kline({ symbol: symbol.value, period: 'daily' })
    klineData.value = kline
    indicators.value = await indicatorApi.calculate({ symbol: symbol.value })
  } catch (e) {
    console.error(e)
  }
})
</script>

<style lang="scss" scoped>
.stock-detail { padding: 40px; color: #fff; }
.header {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;
  .back {
    padding: 8px 16px;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.2);
    background: transparent;
    color: #fff;
    cursor: pointer;
  }
  h1 { font-size: 28px; }
}
.quote-card {
  background: rgba(255,255,255,0.05);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 32px;
  .price { font-size: 48px; font-weight: bold; }
  .up { color: #ef5350; font-size: 20px; }
  .down { color: #26a69a; font-size: 20px; }
  .details {
    display: flex;
    gap: 24px;
    margin-top: 16px;
    color: #888;
  }
}
.chart-container { height: 400px; background: rgba(255,255,255,0.05); border-radius: 16px; margin-bottom: 32px; }
.indicators {
  h3 { margin-bottom: 16px; }
  .indicator-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;
  }
  .indicator-item {
    background: rgba(255,255,255,0.05);
    padding: 16px;
    border-radius: 8px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    .label { color: #888; font-size: 12px; }
  }
}
</style>
