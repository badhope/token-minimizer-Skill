<template>
  <div class="funds-view">
    <h1>基金搜索</h1>
    <div class="search-bar">
      <input v-model="keyword" placeholder="搜索基金代码或名称" @keyup.enter="search" />
      <button @click="search">搜索</button>
    </div>
    <div class="results" v-if="results.length">
      <div v-for="fund in results" :key="fund.symbol" class="fund-card">
        <div class="fund-info">
          <span class="symbol">{{ fund.symbol }}</span>
          <span class="name">{{ fund.name }}</span>
        </div>
        <div class="type">{{ fund.fund_type }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const keyword = ref('')
const results = ref([])

const search = async () => {
  if (!keyword.value) return
  try {
    const res = await axios.post('/api/v1/funds/search', { keyword: keyword.value })
    results.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}
</script>

<style lang="scss" scoped>
.funds-view { padding: 40px; color: #fff; }
.search-bar {
  display: flex;
  gap: 16px;
  margin: 24px 0;
  input {
    flex: 1;
    padding: 16px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.2);
    background: rgba(255,255,255,0.05);
    color: #fff;
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
.fund-card {
  display: flex;
  justify-content: space-between;
  padding: 20px 24px;
  background: rgba(255,255,255,0.05);
  border-radius: 12px;
  .symbol { font-weight: bold; margin-right: 12px; }
  .name { color: #888; }
  .type { color: #666; }
}
</style>
