<template>
  <div class="portfolio-view">
    <h1>我的持仓</h1>
    <div class="portfolio-summary">
      <div class="stat">
        <span class="label">总价值</span>
        <span class="value">{{ portfolio.total_value.toFixed(2) }}</span>
      </div>
      <div class="stat">
        <span class="label">现金</span>
        <span>{{ portfolio.cash.toFixed(2) }}</span>
      </div>
      <div class="stat">
        <span class="label">总盈亏</span>
        <span :class="portfolio.total_pnl >= 0 ? 'up' : 'down'">
          {{ portfolio.total_pnl >= 0 ? '+' : '' }}{{ portfolio.total_pnl.toFixed(2) }} ({{ portfolio.total_pnl_pct.toFixed(2) }}%)
        </span>
      </div>
    </div>
    <div class="positions">
      <div v-for="pos in portfolio.positions" :key="pos.symbol" class="position-card">
        <div class="pos-header">
          <span class="symbol">{{ pos.symbol }}</span>
          <span class="name">{{ pos.name }}</span>
        </div>
        <div class="pos-details">
          <div class="detail">
            <span class="label">持仓</span>
            <span>{{ pos.quantity }}</span>
          </div>
          <div class="detail">
            <span class="label">成本</span>
            <span>{{ pos.avg_cost.toFixed(2) }}</span>
          </div>
          <div class="detail">
            <span class="label">现价</span>
            <span>{{ pos.current_price.toFixed(2) }}</span>
          </div>
          <div class="detail">
            <span class="label">市值</span>
            <span>{{ pos.market_value.toFixed(2) }}</span>
          </div>
          <div class="detail">
            <span class="label">盈亏</span>
            <span :class="pos.unrealized_pnl >= 0 ? 'up' : 'down'">
              {{ pos.unrealized_pnl >= 0 ? '+' : '' }}{{ pos.unrealized_pnl.toFixed(2) }}
            </span>
          </div>
          <div class="detail">
            <span class="label">权重</span>
            <span>{{ pos.weight.toFixed(2) }}%</span>
          </div>
        </div>
      </div>
      <div v-if="!portfolio.positions?.length" class="empty">
        暂无持仓
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { portfolioApi } from '@/api'

const portfolio = ref({
  total_value: 0,
  cash: 0,
  total_pnl: 0,
  total_pnl_pct: 0,
  positions: []
})

const loadPortfolio = async () => {
  try {
    portfolio.value = await portfolioApi.get()
  } catch (e) {
    console.error(e)
  }
}

onMounted(loadPortfolio)
</script>

<style lang="scss" scoped>
.portfolio-view { padding: 40px; color: #fff; }
.portfolio-summary {
  display: flex;
  gap: 24px;
  margin: 24px 0;
  .stat {
    flex: 1;
    background: rgba(255,255,255,0.05);
    padding: 24px;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    .label { color: #888; font-size: 14px; }
    .value { font-size: 28px; font-weight: bold; }
    .up { color: #ef5350; }
    .down { color: #26a69a; }
  }
}
.positions { display: grid; gap: 16px; }
.position-card {
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  padding: 20px 24px;
  .pos-header {
    margin-bottom: 16px;
    .symbol { font-size: 20px; font-weight: bold; margin-right: 12px; }
    .name { color: #888; }
  }
  .pos-details {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 16px;
    .detail {
      display: flex;
      flex-direction: column;
      gap: 4px;
      .label { color: #666; font-size: 12px; }
      .up { color: #ef5350; }
      .down { color: #26a69a; }
    }
  }
}
.empty { text-align: center; color: #666; padding: 60px; }
</style>
