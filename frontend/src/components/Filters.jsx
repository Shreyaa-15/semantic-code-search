export default function Filters({ language, onLanguage, rerank, onRerank, topK, onTopK }) {
  return (
    <div style={{
      display: 'flex', gap: '1rem', alignItems: 'center',
      flexWrap: 'wrap', marginBottom: '1.5rem'
    }}>
      <div style={groupStyle}>
        <label style={labelStyle}>Language</label>
        <select value={language} onChange={e => onLanguage(e.target.value)} style={selectStyle}>
          <option value="all">All</option>
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
        </select>
      </div>

      <div style={groupStyle}>
        <label style={labelStyle}>Results</label>
        <select value={topK} onChange={e => onTopK(Number(e.target.value))} style={selectStyle}>
          {[5, 10, 20].map(n => (
            <option key={n} value={n}>{n}</option>
          ))}
        </select>
      </div>

      <div style={{ ...groupStyle, flexDirection: 'row', alignItems: 'center', gap: '0.5rem' }}>
        <input
          type="checkbox"
          id="rerank"
          checked={rerank}
          onChange={e => onRerank(e.target.checked)}
          style={{ width: 16, height: 16, cursor: 'pointer' }}
        />
        <label htmlFor="rerank" style={{ ...labelStyle, cursor: 'pointer', marginBottom: 0 }}>
          BM25 re-ranking
        </label>
      </div>
    </div>
  )
}

const groupStyle = { display: 'flex', flexDirection: 'column', gap: '0.3rem' }
const labelStyle = { color: '#a6adc8', fontSize: '0.8rem', marginBottom: '0.2rem' }
const selectStyle = {
  padding: '0.5rem 0.8rem',
  background: '#313244', border: '1px solid #45475a',
  borderRadius: 8, color: '#cdd6f4', fontSize: '0.9rem',
  cursor: 'pointer'
}