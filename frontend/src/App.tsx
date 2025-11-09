import React from 'react'
import { BrowserRouter, Link, Route, Routes } from 'react-router-dom'
import './App.css'
import ModernUI from './pages/ModernUI'

function Home() {
  const [status, setStatus] = React.useState<string>('Checking...')

  React.useEffect(() => {
    // Check backend health
    fetch('http://localhost:8000/health')
      .then((res) => res.json())
      .then((data) => {
        setStatus(`✓ Backend: ${data.status}`)
      })
      .catch(() => {
        setStatus('✗ Backend: not connected')
      })
  }, [])

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="bg-white shadow-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">ReasonOS</h1>
          <p className="text-lg text-slate-600">Enterprise AI Reasoning Operating System</p>
          <div className="mt-4">
            <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
              status.includes('healthy') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
            }`}>
              {status}
            </span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Link to="/graph-demo" className="group">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 hover:border-blue-500 hover:shadow-md transition-all">
              <h3 className="text-xl font-semibold text-slate-900 mb-2 group-hover:text-blue-600">
                Semantic Code Analysis
              </h3>
              <p className="text-slate-600">
                Analyze codebase dependencies, impact assessment, and risk analysis
              </p>
            </div>
          </Link>

          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="group"
          >
            <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 hover:border-blue-500 hover:shadow-md transition-all">
              <h3 className="text-xl font-semibold text-slate-900 mb-2 group-hover:text-blue-600">
                API Documentation
              </h3>
              <p className="text-slate-600">
                Interactive API documentation and testing interface
              </p>
            </div>
          </a>

          <a
            href="https://github.com/Motupallisailohith/ReasonOS"
            target="_blank"
            rel="noopener noreferrer"
            className="group"
          >
            <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 hover:border-blue-500 hover:shadow-md transition-all">
              <h3 className="text-xl font-semibold text-slate-900 mb-2 group-hover:text-blue-600">
                GitHub Repository
              </h3>
              <p className="text-slate-600">
                Source code, documentation, and contribution guidelines
              </p>
            </div>
          </a>
        </div>
      </main>
    </div>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ModernUI />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
