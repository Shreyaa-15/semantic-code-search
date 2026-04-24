import { useState, useEffect } from 'react'
import { search, getStats, runEvaluation } from '../api'
import CodeCard from '../components/CodeCard'
import Filters from '../components/Filters'

export default function Search() {
  const [query, setQuery]       = useState('')
  const [results, setResults]   = useState([])
  const [loading, setLoading]   = useState(false)
  const [stats, setStats]       = useState(null)
  const [language, setLanguage] = useState('all')
  const [rerank, setRerank]     = useState(true)
  const [topK, setTopK]         = useState(10)
  const [evalResult, setEval]   = useState(null)
  const [evalLoading, setEvalLoading] = useState(false)
  const [searched, setSearched] = useState(false)
  const [timing, setTiming]     = useState(null)

  useEffect(() => {
    getStats().then(r => setStats(r.data)).catch(() => {})
  }, [])

  const handleSearch = async () => {
    if (!query.trim()) return
    setLoading(true)
    setSearched(true)
    const t0 = Date.now()
    try {
      const r = await search(query, language, topK, rerank)
      setResults(r.data.results)
      setTiming(Date.now() - t0)
    } catch(e) {
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  const handleEval = async () => {
    setEvalLoading(true)
    try {
      const r = await runEvaluation()
      setEval(r.data)
    } finally {
      setEvalLoading(false)
    }
  }

  const EXAMPLES = [
    "binary search in sorted array",
    "check if string is palindrome",
    "depth first search graph",
    "merge two sorted lists",
    "calculate fibonacci sequence",
  ]

  return (
    <div style={{ minHeight: '100vh', background: '#1e1e2e', color: '#cdd6f4' }}>
      {/* Header */}
      <div style={{ borderBottom: '1px solid #313244', padding: '1rem 2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <span style={{ color: '#cba6f7', fontWeight: 700, fontSize: '1.2rem' }}>CodeSearch</span>
          <span style={{ color: '#6c7086', fontSize: '0.85rem', marginLeft: '0.8rem' }}>semantic search over real GitHub code</span>
        </div>
        {stats && (
          <div style={{ color: '#6c7086', fontSize: '0.85rem', display: 'flex', gap: '1.5rem' }}>
            <span>{stats.total_snippets?.toLocaleString()} functions</span>
            <span>{stats.total_repos} repos</span>
            <span>Python + JavaScript</span>
          </div>
        )}
      </div>

      <div style={{ maxWidth: 900, margin: '0 auto', padding: '2rem 1rem' }}>
        {/* Search box */}
        <div style={{ marginBottom: '1.5rem' }}>
          <div style={{ display: 'flex', gap: '0.8rem', marginBottom: '0.8rem' }}>
            <input
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSearch()}
              placeholder='Search code in natural language — "sort a list of objects by key"'
              style={{
                flex: 1, padding: '0.9rem 1.2rem',
                background: '#313244', border: '1px solid #45475a',
                borderRadius: 10, color: '#cdd6f4', fontSize: '1rem',
                outline: 'none'
              }}
            />
            <button onClick={handleSearch} disabled={loading} style={{
              background: '#cba6f7', color: '#1e1e2e',
              border: 'none', borderRadius: 10,
              padding: '0.9rem 2rem', fontWeight: 700,
              cursor: 'pointer', fontSize: '1rem',
              opacity: loading ? 0.7 : 1
            }}>
              {loading ? 'Searching...' : 'Search'}
            </button>
          </div>

          {/* Example queries */}
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {EXAMPLES.map(ex => (
              <button key={ex} onClick={() => { setQuery(ex); }} style={{
                background: '#313244', border: '1px solid #45475a',
                borderRadius: 20, padding: '0.3rem 0.8rem',
                color: '#a6adc8', fontSize: '0.8rem', cursor: 'pointer'
              }}>
                {ex}
              </button>
            ))}
          </div>
        </div>

        {/* Filters */}
        <Filters
          language={language} onLanguage={setLanguage}
          rerank={rerank}    onRerank={setRerank}
          topK={topK}        onTopK={setTopK}
        />

        {/* Results */}
        {loading && (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#a6adc8' }}>
            Embedding query + searching 1683 functions...
          </div>
        )}

        {!loading && searched && results.length === 0 && (
          <div style={{ textAlign: 'center', padding: '3rem', color: '#6c7086' }}>
            No results found. Try a different query.
          </div>
        )}

        {!loading && results.length > 0 && (
          <div>
            <div style={{ color: '#6c7086', fontSize: '0.85rem', marginBottom: '1rem' }}>
              {results.length} results · {timing}ms
            </div>
            {results.map((r, i) => (
              <CodeCard key={r.id} result={r} rank={i + 1} />
            ))}
          </div>
        )}

        {/* Evaluation panel */}
        <div style={{ marginTop: '3rem', borderTop: '1px solid #313244', paddingTop: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h2 style={{ color: '#cdd6f4', margin: 0 }}>Evaluation</h2>
              <p style={{ color: '#6c7086', fontSize: '0.85rem', margin: '0.3rem 0 0' }}>
                MRR + NDCG — semantic search vs BM25 baseline
              </p>
            </div>
            <button onClick={handleEval} disabled={evalLoading} style={{
              background: '#313244', border: '1px solid #45475a',
              borderRadius: 8, padding: '0.6rem 1.2rem',
              color: '#cba6f7', cursor: 'pointer', fontWeight: 600
            }}>
              {evalLoading ? 'Running...' : 'Run Evaluation'}
            </button>
          </div>

          {evalResult && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem' }}>
              {[
                { label: 'Semantic MRR',  value: evalResult.semantic.mrr,  color: '#a6e3a1' },
                { label: 'BM25 MRR',      value: evalResult.bm25.mrr,      color: '#f9e2af' },
                { label: 'MRR Improvement', value: `${evalResult.improvement_pct}%`, color: '#cba6f7' },
                { label: 'Semantic NDCG', value: evalResult.semantic.ndcg, color: '#a6e3a1' },
                { label: 'BM25 NDCG',     value: evalResult.bm25.ndcg,    color: '#f9e2af' },
              ].map(m => (
                <div key={m.label} style={{
                  background: '#313244', border: '1px solid #45475a',
                  borderRadius: 10, padding: '1rem', textAlign: 'center'
                }}>
                  <div style={{ color: m.color, fontSize: '1.8rem', fontWeight: 700 }}>{m.value}</div>
                  <div style={{ color: '#6c7086', fontSize: '0.8rem', marginTop: '0.3rem' }}>{m.label}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}