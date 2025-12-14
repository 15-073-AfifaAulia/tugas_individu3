import { useState, useEffect } from 'react'
import './App.css'

function App() {
  // --- STATE (Penyimpanan Data Sementara di Browser) ---
  const [reviews, setReviews] = useState([])
  const [inputText, setInputText] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  // --- 1. Load Data saat Aplikasi Dibuka ---
  useEffect(() => {
    fetchReviews()
  }, [])

  const fetchReviews = async () => {
    try {
      const response = await fetch('/api/reviews')
      const data = await response.json()
      // Backend kita mengirim data dalam format { data: [...] }
      setReviews(data.data)
    } catch (err) {
      console.error("Gagal ambil data:", err)
    }
  }

  // --- 2. Fungsi Kirim Review ke AI ---
  const handleSubmit = async (e) => {
    e.preventDefault() // Mencegah halaman refresh
    if (!inputText.trim()) return

    setLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/analyze-review', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ review_text: inputText })
      })

      if (!response.ok) throw new Error('Gagal menganalisis')

      const result = await response.json()
      
      // Tambahkan hasil baru ke daftar review (paling atas)
      setReviews([result.data, ...reviews]) 
      setInputText('') // Kosongkan form
    } catch (err) {
      setError('Terjadi kesalahan saat menghubungi AI. Coba lagi.')
      console.error(err)
    } finally {
      setLoading(false) // Matikan loading state
    }
  }

  // --- 3. TAMPILAN (HTML) ---
  return (
    <div className="container">
      <header>
        <h1>🤖 Product Review Analyzer</h1>
        <p>Powered by Hugging Face & Gemini AI</p>
      </header>

      {/* FORM INPUT */}
      <div className="card input-section">
        <form onSubmit={handleSubmit}>
          <textarea
            placeholder="Tulis ulasan produk di sini... (Contoh: Barangnya bagus tapi pengiriman lama)"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={loading}
            rows="4"
          />
          <button type="submit" disabled={loading || !inputText}>
            {loading ? 'Sedang Menganalisis...' : 'Analyze Review'}
          </button>
        </form>
        {error && <p className="error-msg">{error}</p>}
      </div>

      {/* HASIL REVIEW */}
      <div className="reviews-list">
        <h2>Riwayat Analisis ({reviews.length})</h2>
        
        {reviews.length === 0 && <p className="empty-state">Belum ada review.</p>}

        {reviews.map((review) => (
          <div key={review.id} className="review-card">
            <div className="review-header">
              <span className={`badge ${review.sentiment}`}>
                {review.sentiment || 'Neutral'}
              </span>
            </div>
            
            <p className="review-text">"{review.review_text}"</p>
            
            <div className="review-summary">
              <strong>✨ Key Points (Gemini):</strong>
              <div className="summary-content">
                {review.key_points}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App