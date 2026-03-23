import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000
})

api.interceptors.response.use(
  response => response.data,
  error => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

export const stockApi = {
  search: (keyword, market) => api.post('/stocks/search', { keyword, market }),
  realtime: (symbol) => api.post('/stocks/quote/realtime', null, { params: { symbol } }),
  kline: (params) => api.post('/stocks/kline', params)
}

export const indicatorApi = {
  calculate: (params) => api.post('/indicators/calculate', params)
}

export const backtestApi = {
  run: (params) => api.post('/backtest', params),
  trades: (params) => api.post('/backtest/trades', params),
  equityCurve: (params) => api.post('/backtest/equity-curve', params),
  compare: (params) => api.post('/backtest/compare', params)
}

export const alertApi = {
  create: (params) => api.post('/alerts', params),
  list: () => api.get('/alerts')
}

export const fundApi = {
  info: (symbol) => api.get(`/funds/${symbol}`)
}

export const portfolioApi = {
  get: () => api.get('/portfolio')
}

export const marketApi = {
  overview: () => api.get('/market/overview')
}

export const strategyApi = {
  list: () => api.get('/strategies')
}

export const healthApi = {
  check: () => api.get('/health')
}

export default api
