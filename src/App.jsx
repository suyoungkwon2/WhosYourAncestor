import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
      <div className="text-center text-white">
        <div className="text-6xl mb-4">🧬</div>
        <h1 className="text-4xl font-bold mb-2">Who's Your Ancestor</h1>
        <h2 className="text-2xl mb-6">조상탐지기</h2>
        <p className="text-lg mb-8 opacity-90">
          당신의 얼굴에서 찾는 전 세계 혈통 분석
        </p>
        
        <div className="bg-white/20 backdrop-blur-sm rounded-lg p-6 mb-6">
          <h3 className="text-xl font-semibold mb-4">🚀 개발 진행 상황</h3>
          <p className="text-sm space-y-2">
            ✅ GitHub 저장소 연결 완료<br/>
            ✅ Vercel 자동 배포 설정 중<br/>
            🔄 TensorFlow.js 개발 예정<br/>
            📅 3일 내 완성 예정
          </p>
        </div>
        
        <button 
          onClick={() => setCount((count) => count + 1)}
          className="bg-white/20 hover:bg-white/30 backdrop-blur-sm px-6 py-3 rounded-lg transition-all"
        >
          테스트 버튼: {count}
        </button>
        
        <p className="mt-8 text-sm opacity-70">
          jamyeah.com • Powered by Vercel
        </p>
      </div>
    </div>
  )
}

export default App
