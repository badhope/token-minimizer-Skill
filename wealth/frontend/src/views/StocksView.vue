<template>
  <div class="stocks-view">
    <div class="search-bar">
      <input v-model="keyword" placeholder="搜索股票代码或名称" @keyup.enter="search" />
      <button @click="search">搜索</button>
    </div>
    <div class="results" v-if="results.length">
      <div v-for="stock in results" :key="stock.symbol" class="stock-card" @click="goDetail(stock.symbol)">
        <div class="stock-info">
          <span class="symbol">{{ stock.symbol }}</span>
          <span class="name">{{ stock.name }}</span>
        </div>
        <div class="market">{{ stock.market }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { stockApi } from '@/api'

const router = useRouter()
const keyword = ref('')
const results = ref([])

const search = async () => {
  if (!keyword.value) return
  try {
    results.value = await stockApi.search(keyword.value)
  } catch (e) {
    console.error(e)
  }
}

const goDetail = (symbol) => {
  router.push(`/stocks/${symbol}`)
}
</script>

<style lang="scss" scoped>
.stocks-view { padding: 40px; color: #fff; }
.search-bar {
  display: flex;
  gap: 16px;
  margin-bottom: 32px;
  input {
    flex: 1;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.2);
    background: rgba(255,255,255,0.05);
    color: #fff;
    font-size: 16px;
  }
  button {
    padding: 16px 32px;
    border-radius: 12px;
    border: none;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: #fff;
    cursor: pointer;
  }
}
.results { display: flex; flex-direction: column; gap: 12px; }
.stock-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
  &:hover { background: rgba(255,255,255,0.1); }
  .symbol { font-size: 18px; font-weight: bold; margin-right: 12px; }
  .name { color: #888; }
  .market { color: #666; font-size: 14px; }
}
</style>
