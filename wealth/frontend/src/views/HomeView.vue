<template>
  <div class="home">
    <div class="hero">
      <h1 class="hero-title">Wealth</h1>
      <p class="hero-subtitle">智能量化分析平台</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon上证">📈</div>
        <div class="stat-content">
          <h3>上证指数</h3>
          <p class="value">{{ marketData.indices?.['000001']?.price || '--' }}</p>
          <p :class="['change', marketData.indices?.['000001']?.change_pct >= 0 ? 'up' : 'down']">
            {{ marketData.indices?.['000001']?.change_pct >= 0 ? '+' : '' }}{{ marketData.indices?.['000001']?.change_pct || 0 }}%
          </p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon涨">🔥</div>
        <div class="stat-content">
          <h3>涨停数量</h3>
          <p class="value up">{{ marketData.limit_up_count || 0 }}</p>
          <p class="stat-label">涨停</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon跌">❄️</div>
        <div class="stat-content">
          <h3>跌停数量</h3>
          <p class="value down">{{ marketData.limit_down_count || 0 }}</p>
          <p class="stat-label">跌停</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon交易">💹</div>
        <div class="stat-content">
          <h3>市场成交额</h3>
          <p class="value">{{ formatAmount(marketData.total_amount) }}</p>
          <p class="stat-label">今日</p>
        </div>
      </div>
    </div>

    <div class="section">
      <h2 class="section-title">快捷操作</h2>
      <div class="actions-grid">
        <router-link to="/stocks" class="action-card">
          <span class="action-icon">🔍</span>
          <span class="action-text">搜索股票</span>
          <span class="action-desc">查找和分析股票</span>
        </router-link>
        <router-link to="/funds" class="action-card">
          <span class="action-icon">📊</span>
          <span class="action-text">基金筛选</span>
          <span class="action-desc">优选潜力基金</span>
        </router-link>
        <router-link to="/backtest" class="action-card">
          <span class="action-icon">📉</span>
          <span class="action-text">回测策略</span>
          <span class="action-desc">验证策略有效性</span>
        </router-link>
        <router-link to="/prediction" class="action-card">
          <span class="action-icon">🤖</span>
          <span class="action-text">价格预测</span>
          <span class="action-desc">AI智能预测</span>
        </router-link>
        <router-link to="/alerts" class="action-card">
          <span class="action-icon">🔔</span>
          <span class="action-text">价格预警</span>
          <span class="action-desc">实时监控提醒</span>
        </router-link>
        <router-link to="/portfolio" class="action-card">
          <span class="action-icon">💼</span>
          <span class="action-text">我的持仓</span>
          <span class="action-desc">管理投资组合</span>
        </router-link>
        <router-link to="/monitoring" class="action-card">
          <span class="action-icon">📊</span>
          <span class="action-text">系统监控</span>
          <span class="action-desc">运行状态监控</span>
        </router-link>
        <router-link to="/indicators" class="action-card">
          <span class="action-icon">📈</span>
          <span class="action-text">技术指标</span>
          <span class="action-desc">多维度分析</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { marketApi } from '@/api'

const marketData = ref({})

function formatAmount(amount) {
  if (!amount) return '--'
  if (amount >= 1e8) return (amount / 1e8).toFixed(2) + '亿'
  if (amount >= 1e4) return (amount / 1e4).toFixed(2) + '万'
  return amount.toFixed(0)
}

onMounted(async () => {
  try {
    marketData.value = await marketApi.overview()
  } catch (e) {
    console.error(e)
  }
})
</script>

<style scoped>
.home {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  animation: page-enter 0.4s ease;
}

@keyframes page-enter {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hero {
  text-align: center;
  margin-bottom: 48px;
  padding: 48px 0;
}

.hero-title {
  font-size: 56px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 12px;
  letter-spacing: -1px;
}

.hero-subtitle {
  font-size: 20px;
  color: #888;
  font-weight: 400;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 48px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: flex-start;
  gap: 16px;
  transition: all 0.3s ease;
}

.stat-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.15);
  transform: translateY(-2px);
}

.stat-icon上证, .stat-icon涨, .stat-icon跌, .stat-icon交易 {
  font-size: 32px;
  line-height: 1;
}

.stat-content {
  flex: 1;
}

.stat-content h3 {
  color: #666;
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 8px;
}

.stat-content .value {
  font-size: 28px;
  font-weight: 700;
  font-family: 'Fira Code', monospace;
  margin-bottom: 4px;
}

.stat-content .change {
  font-size: 14px;
  font-weight: 500;
}

.stat-content .up { color: #ef5350; }
.stat-content .down { color: #26a69a; }
.stat-label {
  font-size: 12px;
  color: #666;
}

.section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #fff;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.action-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  text-decoration: none;
  transition: all 0.3s ease;
}

.action-card:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: rgba(102, 126, 234, 0.3);
  transform: translateY(-4px);
}

.action-icon {
  font-size: 36px;
  margin-bottom: 12px;
}

.action-text {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 6px;
}

.action-desc {
  font-size: 13px;
  color: #666;
}

@media (max-width: 1200px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .actions-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 900px) {
  .stats-grid { grid-template-columns: repeat(2, 1fr); }
  .actions-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 600px) {
  .home { padding: 16px; }
  .hero { padding: 32px 0; }
  .hero-title { font-size: 40px; }
  .hero-subtitle { font-size: 16px; }
  .stats-grid { grid-template-columns: 1fr; }
  .actions-grid { grid-template-columns: 1fr; }
  .stat-card { flex-direction: column; align-items: center; text-align: center; }
}
</style>
