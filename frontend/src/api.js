import axios from 'axios'

const api = axios.create({ baseURL: '' })

export const search = (query, language = 'all', top_k = 10, rerank = true) =>
  api.post('/search', { query, language, top_k, rerank })

export const searchBM25 = (query, language = 'all', top_k = 10) =>
  api.post('/search/bm25', { query, language, top_k })

export const getStats = () => api.get('/stats')

export const runEvaluation = () => api.get('/evaluate')