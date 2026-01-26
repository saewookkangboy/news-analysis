"""
FastAPI 메인 애플리케이션
"""
import sys
import logging
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가 (로컬 실행 시)
# backend 디렉토리에서 직접 실행하는 경우를 대비
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse

from backend.config import settings, ASSETS_DIR, BASE_DIR
from backend.api.routes import router
from backend.middleware.cache_middleware import CacheMiddleware


# 로깅 설정
logger = logging.getLogger(__name__)

handlers = [logging.StreamHandler()]
if settings.LOG_FILE:
    try:
        # 로그 디렉토리 생성
        log_path = Path(settings.LOG_FILE)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(settings.LOG_FILE))
    except Exception as e:
        logger.warning(f"로그 파일 생성 실패: {e}")

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)

# FastAPI 앱 생성
app = FastAPI(
    title="뉴스 트렌드 분석 서비스",
    description="일정 기간과 키워드를 기반으로 뉴스를 크롤링하고 트렌드 분석 및 워드 클라우드를 제공하는 서비스",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 캐싱 미들웨어 추가 (CORS 이후에 추가)
if settings.CACHE_ENABLED:
    app.add_middleware(CacheMiddleware, duration=settings.CACHE_TTL)

# API 라우터 등록
app.include_router(router, prefix="/api", tags=["analysis"])

# 캐시 통계 라우터 등록
from backend.api.cache_stats import router as cache_router
app.include_router(cache_router, prefix="/api", tags=["cache"])

# 루트 및 헬스 체크 엔드포인트는 정적 파일 마운트 전에 등록해야 함
@app.get("/", response_class=HTMLResponse)
async def root():
    """루트 엔드포인트 - HTML 랜딩 페이지 및 분석 인터페이스 제공"""
    html_content = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>뉴스 트렌드 분석 서비스</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                padding: 40px;
                max-width: 1200px;
                width: 100%;
                margin: 0 auto;
            }
            h1 {
                color: #333;
                font-size: 2.5em;
                margin-bottom: 10px;
                text-align: center;
            }
            .subtitle {
                color: #666;
                text-align: center;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            .status {
                background: #10b981;
                color: white;
                padding: 10px 20px;
                border-radius: 25px;
                display: inline-block;
                margin-bottom: 30px;
                font-weight: 600;
            }
            .analysis-section {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 30px;
                margin: 30px 0;
            }
            .analysis-section h2 {
                color: #333;
                margin-bottom: 20px;
                font-size: 1.8em;
            }
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 600;
            }
            .form-group input,
            .form-group select,
            .form-group textarea {
                width: 100%;
                padding: 12px;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                font-size: 1em;
                transition: border-color 0.3s;
            }
            .form-group input:focus,
            .form-group select:focus,
            .form-group textarea:focus {
                outline: none;
                border-color: #667eea;
            }
            .form-group textarea {
                resize: vertical;
                min-height: 100px;
            }
            .btn {
                background: #667eea;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 8px;
                font-size: 1em;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s;
                width: 100%;
            }
            .btn:hover {
                background: #5568d3;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
            }
            .btn:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
            }
            .loading {
                display: none;
                text-align: center;
                padding: 20px;
                color: #667eea;
            }
            .loading.show {
                display: block;
            }
            .result-section {
                margin-top: 30px;
                padding: 20px;
                background: white;
                border-radius: 10px;
                border: 2px solid #e9ecef;
                display: none;
            }
            .result-section.show {
                display: block;
            }
            .result-section h3 {
                color: #333;
                margin-bottom: 15px;
            }
            .result-content {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                white-space: pre-wrap;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                font-size: 0.95em;
                line-height: 1.6;
                max-height: 600px;
                overflow-y: auto;
                border: 1px solid #e9ecef;
            }
            .copy-btn {
                background: #10b981;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 6px;
                font-size: 0.9em;
                cursor: pointer;
                margin-top: 10px;
                transition: all 0.3s;
            }
            .copy-btn:hover {
                background: #059669;
            }
            .copy-btn:active {
                transform: scale(0.95);
            }
            .error {
                background: #fee;
                color: #c33;
                padding: 15px;
                border-radius: 8px;
                margin-top: 20px;
                display: none;
            }
            .error.show {
                display: block;
            }
            .links {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 30px;
            }
            .link-card {
                background: #f8f9fa;
                border: 2px solid #e9ecef;
                border-radius: 10px;
                padding: 20px;
                text-decoration: none;
                color: #333;
                transition: all 0.3s ease;
                display: block;
                text-align: center;
            }
            .link-card:hover {
                border-color: #667eea;
                transform: translateY(-5px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.2);
            }
            .link-card h3 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 1.2em;
            }
            .link-card p {
                color: #666;
                font-size: 0.9em;
            }
            .version {
                text-align: center;
                color: #999;
                margin-top: 30px;
                font-size: 0.9em;
            }
            .checkbox-group {
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .checkbox-group input[type="checkbox"] {
                width: auto;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 뉴스 트렌드 분석 서비스</h1>
            <p class="subtitle">AI 기반 키워드, 오디언스, 경쟁자 분석 플랫폼</p>
            
            <div style="text-align: center;">
                <span class="status">✅ 서비스 정상 운영 중</span>
            </div>
            
            <!-- 분석 섹션 -->
            <div class="analysis-section">
                <h2>🔍 타겟 분석</h2>
                <form id="analysisForm">
                    <div class="form-group">
                        <label for="target_keyword">분석할 키워드 또는 주제 *</label>
                        <input type="text" id="target_keyword" name="target_keyword" 
                               placeholder="예: 인공지능, 스마트폰, 삼성전자" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="target_type">분석 유형 *</label>
                        <select id="target_type" name="target_type" required>
                            <option value="keyword">키워드 분석</option>
                            <option value="audience">오디언스 분석</option>
                            <option value="competitor">경쟁자 분석</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="additional_context">추가 컨텍스트 (선택사항)</label>
                        <textarea id="additional_context" name="additional_context" 
                                  placeholder="추가로 제공할 컨텍스트 정보를 입력하세요"></textarea>
                    </div>
                    
                    <div class="form-group checkbox-group">
                        <input type="checkbox" id="use_gemini" name="use_gemini">
                        <label for="use_gemini" style="margin: 0;">Gemini API 사용 (OpenAI 대신)</label>
                    </div>
                    
                    <button type="submit" class="btn" id="analyzeBtn">분석 시작</button>
                </form>
                
                <div class="loading" id="loading">
                    <p>⏳ 분석 중입니다. 잠시만 기다려주세요...</p>
                </div>
                
                <div class="error" id="error"></div>
                
                <div class="result-section" id="resultSection">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                        <h3 style="margin: 0;">📊 분석 결과</h3>
                        <button class="copy-btn" id="copyBtn" onclick="copyToClipboard()">📋 복사</button>
                    </div>
                    <div class="result-content" id="resultContent"></div>
                </div>
            </div>
            
            <div class="links">
                <a href="/docs" class="link-card">
                    <h3>📚 API 문서</h3>
                    <p>Swagger UI를 통한 API 테스트 및 문서 확인</p>
                </a>
                <a href="/health" class="link-card">
                    <h3>💚 헬스 체크</h3>
                    <p>서비스 상태 확인</p>
                </a>
                <a href="/openapi.json" class="link-card">
                    <h3>📋 OpenAPI 스펙</h3>
                    <p>API 스펙 JSON 다운로드</p>
                </a>
            </div>
            
            <div class="version">
                Version 1.0.0 | 뉴스 트렌드 분석 서비스
            </div>
        </div>
        
        <script>
            // 클립보드 복사 함수
            function copyToClipboard() {
                const resultContent = document.getElementById('resultContent');
                const text = resultContent.textContent;
                
                navigator.clipboard.writeText(text).then(function() {
                    const copyBtn = document.getElementById('copyBtn');
                    const originalText = copyBtn.textContent;
                    copyBtn.textContent = '✅ 복사됨!';
                    copyBtn.style.background = '#10b981';
                    
                    setTimeout(function() {
                        copyBtn.textContent = originalText;
                        copyBtn.style.background = '#10b981';
                    }, 2000);
                }).catch(function(err) {
                    console.error('복사 실패:', err);
                    alert('복사에 실패했습니다. 수동으로 선택하여 복사해주세요.');
                });
            }
            
            document.getElementById('analysisForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const form = e.target;
                const loading = document.getElementById('loading');
                const error = document.getElementById('error');
                const resultSection = document.getElementById('resultSection');
                const resultContent = document.getElementById('resultContent');
                const analyzeBtn = document.getElementById('analyzeBtn');
                
                // 초기화
                loading.classList.add('show');
                error.classList.remove('show');
                resultSection.classList.remove('show');
                analyzeBtn.disabled = true;
                
                // 폼 데이터 수집
                const formData = {
                    target_keyword: document.getElementById('target_keyword').value,
                    target_type: document.getElementById('target_type').value,
                    additional_context: document.getElementById('additional_context').value || null,
                    use_gemini: document.getElementById('use_gemini').checked
                };
                
                try {
                    const response = await fetch('/api/target/analyze', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(formData)
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.detail || '분석 요청 실패');
                    }
                    
                    const data = await response.json();
                    
                    if (data.success && data.data) {
                        // 결과를 Markdown 형식으로 포맷팅
                        let resultText = '';
                        let analysisData = null;
                        
                        // JSON 데이터 파싱
                        if (data.data.analysis) {
                            if (typeof data.data.analysis === 'string') {
                                try {
                                    let cleanAnalysis = data.data.analysis;
                                    // 마크다운 코드 블록 제거
                                    const codeBlockStart = '```json';
                                    const codeBlockEnd = '```';
                                    if (cleanAnalysis.includes(codeBlockStart)) {
                                        const startIdx = cleanAnalysis.indexOf(codeBlockStart);
                                        const endIdx = cleanAnalysis.lastIndexOf(codeBlockEnd);
                                        if (endIdx > startIdx) {
                                            cleanAnalysis = cleanAnalysis.substring(0, startIdx) + 
                                                          cleanAnalysis.substring(startIdx + codeBlockStart.length, endIdx) + 
                                                          cleanAnalysis.substring(endIdx + codeBlockEnd.length);
                                        }
                                    }
                                    cleanAnalysis = cleanAnalysis.replace(/```/g, '').trim();
                                    analysisData = JSON.parse(cleanAnalysis);
                                } catch (parseError) {
                                    console.warn('JSON 파싱 실패:', parseError);
                                    analysisData = { analysis: data.data.analysis };
                                }
                            } else {
                                analysisData = data.data.analysis;
                            }
                        } else {
                            analysisData = data.data;
                        }
                        
                        // Markdown 형식으로 변환
                        const targetKeyword = formData.target_keyword;
                        const targetType = formData.target_type;
                        const typeNames = {
                            'keyword': '키워드',
                            'audience': '오디언스',
                            'competitor': '경쟁자'
                        };
                        
                        resultText = `# 타겟 분석 보고서\\n\\n`;
                        resultText += `**분석 대상**: ${targetKeyword}\\n`;
                        resultText += `**분석 유형**: ${typeNames[targetType] || targetType} 분석\\n`;
                        resultText += `**분석 일시**: ${new Date().toLocaleString('ko-KR')}\\n\\n`;
                        resultText += `---\\n\\n`;
                        
                        // 오디언스 분석인 경우 특별한 포맷팅
                        if (targetType === 'audience' && analysisData) {
                            if (analysisData.summary) {
                                resultText += `## 📋 요약\\n\\n${analysisData.summary}\\n\\n`;
                            }
                            
                            if (analysisData.key_points && analysisData.key_points.length > 0) {
                                resultText += `## 🔑 주요 포인트\\n\\n`;
                                analysisData.key_points.forEach((point, idx) => {
                                    resultText += `${idx + 1}. ${point}\\n`;
                                });
                                resultText += `\\n`;
                            }
                            
                            if (analysisData.insights) {
                                resultText += `## 💡 인사이트\\n\\n`;
                                
                                if (analysisData.insights.demographics) {
                                    resultText += `### 인구통계학적 특성\\n\\n`;
                                    const demo = analysisData.insights.demographics;
                                    if (demo.age_range) resultText += `- **연령대**: ${demo.age_range}\\n`;
                                    if (demo.gender) resultText += `- **성별**: ${demo.gender}\\n`;
                                    if (demo.location) resultText += `- **지역**: ${demo.location}\\n`;
                                    if (demo.income_level) resultText += `- **소득 수준**: ${demo.income_level}\\n`;
                                    if (demo.expected_occupations && demo.expected_occupations.length > 0) {
                                        resultText += `- **예상 직업**:\\n`;
                                        demo.expected_occupations.forEach(occupation => {
                                            resultText += `  - ${occupation}\\n`;
                                        });
                                    }
                                    resultText += `\\n`;
                                }
                                
                                if (analysisData.insights.psychographics) {
                                    resultText += `### 심리적 특성\\n\\n`;
                                    const psycho = analysisData.insights.psychographics;
                                    if (psycho.lifestyle) resultText += `- **라이프스타일**: ${psycho.lifestyle}\\n`;
                                    if (psycho.values) resultText += `- **가치관**: ${psycho.values}\\n`;
                                    if (psycho.interests) resultText += `- **관심사**: ${psycho.interests}\\n`;
                                    resultText += `\\n`;
                                }
                                
                                if (analysisData.insights.behavior) {
                                    resultText += `### 행동 패턴\\n\\n`;
                                    const behavior = analysisData.insights.behavior;
                                    if (behavior.purchase_behavior) resultText += `- **구매 행동**: ${behavior.purchase_behavior}\\n`;
                                    if (behavior.media_consumption) resultText += `- **미디어 소비**: ${behavior.media_consumption}\\n`;
                                    if (behavior.online_activity) resultText += `- **온라인 활동**: ${behavior.online_activity}\\n`;
                                    resultText += `\\n`;
                                }
                                
                                if (analysisData.insights.trends && analysisData.insights.trends.length > 0) {
                                    resultText += `### 트렌드\\n\\n`;
                                    analysisData.insights.trends.forEach((trend, idx) => {
                                        resultText += `${idx + 1}. ${trend}\\n`;
                                    });
                                    resultText += `\\n`;
                                }
                                
                                if (analysisData.insights.opportunities && analysisData.insights.opportunities.length > 0) {
                                    resultText += `### 기회\\n\\n`;
                                    analysisData.insights.opportunities.forEach((opp, idx) => {
                                        resultText += `${idx + 1}. ${opp}\\n`;
                                    });
                                    resultText += `\\n`;
                                }
                                
                                if (analysisData.insights.challenges && analysisData.insights.challenges.length > 0) {
                                    resultText += `### 도전 과제\\n\\n`;
                                    analysisData.insights.challenges.forEach((challenge, idx) => {
                                        resultText += `${idx + 1}. ${challenge}\\n`;
                                    });
                                    resultText += `\\n`;
                                }
                            }
                            
                            if (analysisData.recommendations && analysisData.recommendations.length > 0) {
                                resultText += `## 💼 권장사항\\n\\n`;
                                analysisData.recommendations.forEach((rec, idx) => {
                                    resultText += `${idx + 1}. ${rec}\\n`;
                                });
                                resultText += `\\n`;
                            }
                            
                            if (analysisData.metrics) {
                                resultText += `## 📊 지표\\n\\n`;
                                const metrics = analysisData.metrics;
                                if (metrics.estimated_volume) resultText += `- **예상 규모**: ${metrics.estimated_volume}\\n`;
                                if (metrics.engagement_level) resultText += `- **참여 수준**: ${metrics.engagement_level}\\n`;
                                if (metrics.growth_potential) resultText += `- **성장 잠재력**: ${metrics.growth_potential}\\n`;
                                resultText += `\\n`;
                            }
                        } else {
                            // 키워드 및 경쟁자 분석
                            if (analysisData.summary) {
                                resultText += `## 📋 요약\\n\\n${analysisData.summary}\\n\\n`;
                            }
                            
                            if (analysisData.key_points && analysisData.key_points.length > 0) {
                                resultText += `## 🔑 주요 포인트\\n\\n`;
                                analysisData.key_points.forEach((point, idx) => {
                                    resultText += `${idx + 1}. ${point}\\n`;
                                });
                                resultText += `\\n`;
                            }
                            
                            if (analysisData.insights) {
                                resultText += `## 💡 인사이트\\n\\n`;
                                
                                if (analysisData.insights.trends && analysisData.insights.trends.length > 0) {
                                    resultText += `### 트렌드\\n\\n`;
                                    analysisData.insights.trends.forEach((trend, idx) => {
                                        resultText += `${idx + 1}. ${trend}\\n`;
                                    });
                                    resultText += `\\n`;
                                }
                                
                                if (analysisData.insights.opportunities && analysisData.insights.opportunities.length > 0) {
                                    resultText += `### 기회\\n\\n`;
                                    analysisData.insights.opportunities.forEach((opp, idx) => {
                                        resultText += `${idx + 1}. ${opp}\\n`;
                                    });
                                    resultText += `\\n`;
                                }
                                
                                if (analysisData.insights.challenges && analysisData.insights.challenges.length > 0) {
                                    resultText += `### 도전 과제\\n\\n`;
                                    analysisData.insights.challenges.forEach((challenge, idx) => {
                                        resultText += `${idx + 1}. ${challenge}\\n`;
                                    });
                                    resultText += `\\n`;
                                }
                            }
                            
                            if (analysisData.recommendations && analysisData.recommendations.length > 0) {
                                resultText += `## 💼 권장사항\\n\\n`;
                                analysisData.recommendations.forEach((rec, idx) => {
                                    resultText += `${idx + 1}. ${rec}\\n`;
                                });
                                resultText += `\\n`;
                            }
                            
                            if (analysisData.metrics) {
                                resultText += `## 📊 지표\\n\\n`;
                                const metrics = analysisData.metrics;
                                if (metrics.estimated_volume) resultText += `- **예상 검색량/시장 규모**: ${metrics.estimated_volume}\\n`;
                                if (metrics.competition_level) resultText += `- **경쟁 수준**: ${metrics.competition_level}\\n`;
                                if (metrics.growth_potential) resultText += `- **성장 잠재력**: ${metrics.growth_potential}\\n`;
                                resultText += `\\n`;
                            }
                            
                            // 타겟 오디언스 정보 (키워드 분석의 경우)
                            if (analysisData.target_audience && analysisData.target_audience.expected_occupations) {
                                resultText += `## 👔 예상 직업\\n\\n`;
                                analysisData.target_audience.expected_occupations.forEach((occupation, idx) => {
                                    resultText += `${idx + 1}. ${occupation}\\n`;
                                });
                                resultText += `\\n`;
                            }
                        }
                        
                        resultText += `---\\n\\n`;
                        resultText += `*본 보고서는 AI 기반 분석 결과입니다.*\\n`;
                        
                        resultContent.textContent = resultText;
                        resultSection.classList.add('show');
                    } else {
                        throw new Error('분석 결과를 받지 못했습니다.');
                    }
                } catch (err) {
                    error.textContent = '오류: ' + err.message;
                    error.classList.add('show');
                } finally {
                    loading.classList.remove('show');
                    analyzeBtn.disabled = false;
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {
        "status": "healthy",
        "service": "news-trend-analyzer"
    }

# 정적 파일 서빙 (워드 클라우드 이미지)
app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

# 프론트엔드 정적 파일 서빙 (빌드된 파일이 있는 경우에만)
# 프론트엔드는 /app 경로로 마운트하여 루트 경로와 충돌 방지
frontend_dir = BASE_DIR / "frontend"
frontend_build_dir = frontend_dir / "build"  # React 빌드 디렉토리
frontend_dist_dir = frontend_dir / "dist"  # Vite/기타 빌드 디렉토리

# 빌드된 정적 파일이 있는 경우에만 마운트
if frontend_build_dir.exists() and any(frontend_build_dir.iterdir()):
    app.mount("/app", StaticFiles(directory=str(frontend_build_dir), html=True), name="frontend")
elif frontend_dist_dir.exists() and any(frontend_dist_dir.iterdir()):
    app.mount("/app", StaticFiles(directory=str(frontend_dist_dir), html=True), name="frontend")
elif frontend_dir.exists():
    # 빌드 디렉토리가 없지만 frontend 디렉토리가 있으면 src를 서빙 (개발용)
    logger.info("프론트엔드 빌드 파일이 없습니다. 빌드 후 /app 경로에서 접근 가능합니다.")


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    logger.info("뉴스 트렌드 분석 서비스 시작")
    logger.info(f"서버 설정: {settings.HOST}:{settings.PORT}")
    logger.info(f"디버그 모드: {settings.DEBUG}")


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    logger.info("뉴스 트렌드 분석 서비스 종료")


if __name__ == "__main__":
    import uvicorn
    # 프로젝트 루트에서 실행하도록 수정
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
