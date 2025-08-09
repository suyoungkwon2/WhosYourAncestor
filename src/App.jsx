import { useState, useRef, useEffect } from 'react'
import ancestorAI from './ai_model.js'

function App() {
  const [isModelLoaded, setIsModelLoaded] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [results, setResults] = useState(null)
  const [selectedGender, setSelectedGender] = useState('')
  const [uploadedImage, setUploadedImage] = useState(null)
  const [error, setError] = useState(null)
  const fileInputRef = useRef(null)
  const imageRef = useRef(null)

  // AI 모델 로드
  useEffect(() => {
    const loadModel = async () => {
      try {
        await ancestorAI.loadModel()
        setIsModelLoaded(true)
      } catch (error) {
        console.error('모델 로드 실패:', error)
        setError('AI 모델 로드에 실패했습니다.')
      }
    }

    loadModel()
  }, [])

  // 이미지 업로드 처리
  const handleImageUpload = (event) => {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        setUploadedImage(e.target.result)
        setResults(null)
        setError(null)
      }
      reader.readAsDataURL(file)
    }
  }

  // 분석 실행
  const handleAnalyze = async () => {
    if (!uploadedImage || !selectedGender) {
      setError('이미지와 성별을 모두 선택해주세요.')
      return
    }

    setIsAnalyzing(true)
    setError(null)

    try {
      // 이미지 요소 생성
      const img = new Image()
      img.onload = async () => {
        try {
          // 얼굴 감지
          const hasFace = await ancestorAI.detectFace(img)
          if (!hasFace) {
            setError('얼굴이 감지되지 않습니다. 더 명확한 얼굴 사진을 업로드해주세요.')
            setIsAnalyzing(false)
            return
          }

          // AI 분석 실행
          const analysisResults = await ancestorAI.predict(img)
          setResults(analysisResults)
        } catch (error) {
          console.error('분석 실패:', error)
          setError('이미지 분석에 실패했습니다.')
        } finally {
          setIsAnalyzing(false)
        }
      }
      img.src = uploadedImage
    } catch (error) {
      console.error('분석 실패:', error)
      setError('이미지 분석에 실패했습니다.')
      setIsAnalyzing(false)
    }
  }

  // 새 분석 시작
  const handleNewAnalysis = () => {
    setUploadedImage(null)
    setSelectedGender('')
    setResults(null)
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600">
      <div className="container mx-auto px-4 py-8">
        {/* 헤더 */}
        <div className="text-center text-white mb-8">
          <div className="text-6xl mb-4">🧬</div>
          <h1 className="text-4xl font-bold mb-2">Who's Your Ancestor</h1>
          <h2 className="text-2xl mb-6">조상탐지기</h2>
          <p className="text-lg opacity-90">
            당신의 얼굴에서 찾는 전 세계 혈통 분석
          </p>
        </div>

        {/* AI 모델 상태 */}
        {!isModelLoaded && (
          <div className="bg-white/20 backdrop-blur-sm rounded-lg p-6 mb-6 text-center text-white">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
            <p>AI 모델 로드 중...</p>
          </div>
        )}

        {/* 메인 컨텐츠 */}
        {isModelLoaded && (
          <div className="max-w-4xl mx-auto">
            {/* 성별 선택 */}
            {!selectedGender && (
              <div className="bg-white/20 backdrop-blur-sm rounded-lg p-6 mb-6">
                <h3 className="text-xl font-semibold text-white mb-4">성별을 선택해주세요</h3>
                <div className="flex gap-4 justify-center">
                  <button
                    onClick={() => setSelectedGender('female')}
                    className="bg-pink-500 hover:bg-pink-600 text-white px-6 py-3 rounded-lg transition-all"
                  >
                    👩 여성
                  </button>
                  <button
                    onClick={() => setSelectedGender('male')}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg transition-all"
                  >
                    👨 남성
                  </button>
                </div>
              </div>
            )}

            {/* 이미지 업로드 */}
            {selectedGender && !uploadedImage && (
              <div className="bg-white/20 backdrop-blur-sm rounded-lg p-6 mb-6">
                <h3 className="text-xl font-semibold text-white mb-4">
                  얼굴 사진을 업로드해주세요 ({selectedGender === 'female' ? '여성' : '남성'})
                </h3>
                <div className="border-2 border-dashed border-white/50 rounded-lg p-8 text-center">
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="bg-white/20 hover:bg-white/30 text-white px-6 py-3 rounded-lg transition-all"
                  >
                    📸 사진 선택하기
                  </button>
                  <p className="text-white/70 mt-2 text-sm">
                    JPG, PNG 파일을 지원합니다
                  </p>
                </div>
              </div>
            )}

            {/* 업로드된 이미지 */}
            {uploadedImage && (
              <div className="bg-white/20 backdrop-blur-sm rounded-lg p-6 mb-6">
                <h3 className="text-xl font-semibold text-white mb-4">업로드된 이미지</h3>
                <div className="flex justify-center mb-4">
                  <img
                    ref={imageRef}
                    src={uploadedImage}
                    alt="업로드된 이미지"
                    className="max-w-md max-h-64 object-contain rounded-lg"
                  />
                </div>
                <div className="flex gap-4 justify-center">
                  <button
                    onClick={handleAnalyze}
                    disabled={isAnalyzing}
                    className="bg-green-500 hover:bg-green-600 disabled:bg-gray-500 text-white px-6 py-3 rounded-lg transition-all"
                  >
                    {isAnalyzing ? '🔍 분석 중...' : '🔍 분석 시작'}
                  </button>
                  <button
                    onClick={handleNewAnalysis}
                    className="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-lg transition-all"
                  >
                    🔄 새로 시작
                  </button>
                </div>
              </div>
            )}

            {/* 에러 메시지 */}
            {error && (
              <div className="bg-red-500/20 backdrop-blur-sm rounded-lg p-4 mb-6 text-white">
                <p className="text-center">❌ {error}</p>
              </div>
            )}

            {/* 분석 결과 */}
            {results && (
              <div className="bg-white/20 backdrop-blur-sm rounded-lg p-6 mb-6">
                <h3 className="text-xl font-semibold text-white mb-4">분석 결과</h3>
                <div className="space-y-3">
                  {results.map((result, index) => (
                    <div key={index} className="bg-white/10 rounded-lg p-4">
                      <div className="flex justify-between items-center">
                        <div>
                          <span className="text-white font-semibold">
                            {result.country} {result.gender}
                          </span>
                          <span className="text-white/70 ml-2">
                            ({result.confidence})
                          </span>
                        </div>
                        <div className="text-white font-bold">
                          {result.probability}%
                        </div>
                      </div>
                      <div className="w-full bg-white/20 rounded-full h-2 mt-2">
                        <div
                          className="bg-gradient-to-r from-blue-400 to-purple-400 h-2 rounded-full transition-all"
                          style={{ width: `${result.probability}%` }}
                        ></div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-6 text-center">
                  <button
                    onClick={handleNewAnalysis}
                    className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg transition-all"
                  >
                    🔄 새 분석 시작
                  </button>
                </div>
              </div>
            )}

            {/* 모델 정보 */}
            <div className="bg-white/10 backdrop-blur-sm rounded-lg p-6">
              <h3 className="text-lg font-semibold text-white mb-4">AI 모델 정보</h3>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-white/80 text-sm">
                <div>정확도: 40.32%</div>
                <div>학습 데이터: 1,263개</div>
                <div>지원 국가: 8개</div>
                <div>모델: MobileNetV2</div>
                <div>입력 크기: 224x224</div>
                <div>업데이트: 2025-08-08</div>
              </div>
            </div>
          </div>
        )}

        {/* 푸터 */}
        <div className="text-center text-white/70 mt-8">
          <p>jamyeah.com • Powered by Vercel</p>
        </div>
      </div>
    </div>
  )
}

export default App
