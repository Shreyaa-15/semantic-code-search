import { useState } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'

export default function CodeCard({ result, rank }) {
  const [expanded, setExpanded] = useState(false)

  const lang = result.language === 'python' ? 'python' : 'javascript'
  const preview = result.code.split('\n').slice(0, 6).join('\n')
  const hasMore = result.code.split('\n').length > 6

  return (
    <div style={cardStyle}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.8rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem' }}>
          <span style={rankBadge}>#{rank}</span>
          <div>
            <span style={{ color: '#cba6f7', fontWeight: 700, fontSize: '1rem' }}>
              {result.function_name}
            </span>
            <span style={{ color: '#6c7086', fontSize: '0.8rem', marginLeft: '0.5rem' }}>
              {result.filepath}
            </span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <span style={langBadge(result.language)}>{result.language}</span>
          <span style={scoreBadge}>{result.score?.toFixed(3)}</span>
        </div>
      </div>

      {/* Repo + stars */}
      <div style={{ marginBottom: '0.8rem', display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <a href={result.url} target="_blank" rel="noreferrer" style={{ color: '#89dceb', fontSize: '0.85rem', textDecoration: 'none' }}>
          {result.repo}
        </a>
        <span style={{ color: '#6c7086', fontSize: '0.8rem' }}>⭐ {result.stars?.toLocaleString()}</span>
        {result.semantic_score && (
          <span style={{ color: '#6c7086', fontSize: '0.75rem' }}>
            sem: {result.semantic_score} · bm25: {result.bm25_score}
          </span>
        )}
      </div>

      {/* Docstring */}
      {result.docstring && (
        <p style={{ color: '#a6adc8', fontSize: '0.85rem', marginBottom: '0.8rem', fontStyle: 'italic' }}>
          {result.docstring.slice(0, 150)}{result.docstring.length > 150 ? '...' : ''}
        </p>
      )}

      {/* Code */}
      <div style={{ borderRadius: 8, overflow: 'hidden', fontSize: '0.85rem' }}>
        <SyntaxHighlighter
          language={lang}
          style={vscDarkPlus}
          customStyle={{ margin: 0, borderRadius: 8, fontSize: '0.82rem' }}
        >
          {expanded ? result.code : preview}
        </SyntaxHighlighter>
      </div>

      {hasMore && (
        <button onClick={() => setExpanded(!expanded)} style={expandBtn}>
          {expanded ? 'Show less ↑' : `Show more ↓ (${result.code.split('\n').length} lines)`}
        </button>
      )}
    </div>
  )
}

const cardStyle = {
  background: '#313244', border: '1px solid #45475a',
  borderRadius: 12, padding: '1.2rem',
  marginBottom: '1rem'
}
const rankBadge = {
  background: '#1e1e2e', color: '#6c7086',
  borderRadius: 6, padding: '0.2rem 0.5rem',
  fontSize: '0.8rem', fontWeight: 700, minWidth: 28,
  textAlign: 'center'
}
const scoreBadge = {
  background: '#cba6f722', color: '#cba6f7',
  border: '1px solid #cba6f744',
  borderRadius: 6, padding: '0.2rem 0.6rem',
  fontSize: '0.8rem', fontWeight: 700
}
const langBadge = (lang) => ({
  background: lang === 'python' ? '#3b8bd422' : '#f9e2af22',
  color: lang === 'python' ? '#89dceb' : '#f9e2af',
  border: `1px solid ${lang === 'python' ? '#89dceb44' : '#f9e2af44'}`,
  borderRadius: 6, padding: '0.2rem 0.6rem', fontSize: '0.75rem'
})
const expandBtn = {
  background: 'transparent', border: 'none',
  color: '#cba6f7', cursor: 'pointer',
  fontSize: '0.85rem', marginTop: '0.6rem', padding: 0
}