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

import os
IS_VERCEL = os.environ.get("VERCEL") == "1"

handlers = [logging.StreamHandler()]
# Vercel 환경에서는 파일 로깅 비활성화
if settings.LOG_FILE and not IS_VERCEL:
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
    description="""
    AI 기반 뉴스 트렌드 분석 및 마케팅 인사이트 서비스
    
    ## 주요 기능
    
    * **타겟 분석**: 키워드, 오디언스, 종합 분석
    * **감정 분석**: 텍스트 감정 및 톤 분석
    * **키워드 추천**: 연관 키워드 및 SEO 최적화 제안
    * **대시보드**: 실시간 메트릭 및 퍼널 분석
    
    ## AI 모델
    
    * OpenAI GPT-4o-mini
    * Google Gemini 2.0 Flash
    
    ## API 문서
    
    * Swagger UI: `/docs`
    * ReDoc: `/redoc`
    * OpenAPI JSON: `/openapi.json`
    """,
    version="1.0.0",
    contact={
        "name": "News Trend Analyzer",
        "url": "https://news-trend-analyzer.vercel.app",
    },
    license_info={
        "name": "MIT",
    },
    servers=[
        {
            "url": "https://news-trend-analyzer.vercel.app",
            "description": "프로덕션 서버"
        },
        {
            "url": "http://localhost:8000",
            "description": "로컬 개발 서버"
        }
    ]
)

# CORS 설정 (보안 강화)
# 환경 변수 기반 CORS 설정
ALLOWED_ORIGINS_ENV = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
ALLOWED_ORIGINS = [origin.strip() for origin in ALLOWED_ORIGINS_ENV.split(",")]

# Vercel 환경에서는 프로덕션 도메인만 허용
if IS_VERCEL:
    ALLOWED_ORIGINS = ["https://news-trend-analyzer.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# 캐싱 미들웨어 추가 (CORS 이후에 추가)
if settings.CACHE_ENABLED:
    app.add_middleware(CacheMiddleware, duration=settings.CACHE_TTL)

# API 라우터 등록
app.include_router(router, prefix="/api", tags=["analysis"])

# 캐시 통계 라우터 등록
from backend.api.cache_stats import router as cache_router
app.include_router(cache_router, prefix="/api", tags=["cache"])

# 성능 메트릭 라우터 등록
from backend.api.metrics import router as metrics_router
app.include_router(metrics_router, prefix="/api", tags=["metrics"])

# Dashboard API 라우터 등록 (스텁)
from backend.api.dashboard_routes import router as dashboard_router
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["dashboard"])

# 모니터링 라우터 등록
try:
    from backend.api.monitoring import router as monitoring_router
    app.include_router(monitoring_router, tags=["monitoring"])
except ImportError:
    # psutil이 설치되지 않은 경우 기본 헬스 체크만 제공
    logger.warning("psutil이 설치되지 않아 기본 헬스 체크만 제공됩니다.")

# 루트 및 헬스 체크 엔드포인트는 정적 파일 마운트 전에 등록해야 함
@app.get("/", response_class=HTMLResponse)
async def root():
    """루트 엔드포인트 - HTML 랜딩 페이지 및 분석 인터페이스 제공 (블랙/화이트 미니멀 테마)"""
    html_content = r"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        
        <!-- Primary Meta Tags -->
        <title>뉴스 트렌드 분석 서비스 | AI 기반 키워드, 오디언스, 경쟁자 분석</title>
        <meta name="title" content="뉴스 트렌드 분석 서비스 | AI 기반 키워드, 오디언스, 경쟁자 분석">
        <meta name="description" content="AI 기반 키워드 분석, 오디언스 분석, 경쟁자 분석을 제공하는 뉴스 트렌드 분석 플랫폼. OpenAI GPT-4o-mini와 Google Gemini 2.0 Flash를 활용한 전문적인 마케팅 인사이트를 제공합니다.">
        <meta name="keywords" content="뉴스 트렌드 분석, 키워드 분석, 오디언스 분석, 경쟁자 분석, AI 분석, 마케팅 인사이트, 트렌드 분석, 키워드 리서치, SEO 분석, 마케팅 분석 도구">
        <meta name="author" content="News Trend Analyzer">
        <meta name="robots" content="index, follow">
        <meta name="language" content="Korean">
        <meta name="revisit-after" content="7 days">
        
        <!-- Open Graph / Facebook -->
        <meta property="og:type" content="website">
        <meta property="og:url" content="https://news-trend-analyzer.vercel.app/">
        <meta property="og:title" content="뉴스 트렌드 분석 서비스 | AI 기반 키워드, 오디언스, 경쟁자 분석">
        <meta property="og:description" content="AI 기반 키워드 분석, 오디언스 분석, 경쟁자 분석을 제공하는 뉴스 트렌드 분석 플랫폼. OpenAI GPT-4o-mini와 Google Gemini 2.0 Flash를 활용한 전문적인 마케팅 인사이트를 제공합니다.">
        <meta property="og:image" content="https://news-trend-analyzer.vercel.app/og-image.png">
        <meta property="og:locale" content="ko_KR">
        <meta property="og:site_name" content="뉴스 트렌드 분석 서비스">
        
        <!-- Twitter -->
        <meta property="twitter:card" content="summary_large_image">
        <meta property="twitter:url" content="https://news-trend-analyzer.vercel.app/">
        <meta property="twitter:title" content="뉴스 트렌드 분석 서비스 | AI 기반 키워드, 오디언스, 경쟁자 분석">
        <meta property="twitter:description" content="AI 기반 키워드 분석, 오디언스 분석, 경쟁자 분석을 제공하는 뉴스 트렌드 분석 플랫폼. OpenAI GPT-4o-mini와 Google Gemini 2.0 Flash를 활용한 전문적인 마케팅 인사이트를 제공합니다.">
        <meta property="twitter:image" content="https://news-trend-analyzer.vercel.app/og-image.png">
        
        <!-- Canonical URL -->
        <link rel="canonical" href="https://news-trend-analyzer.vercel.app/">
        
        <!-- Favicon -->
        <link rel="icon" type="image/x-icon" href="/favicon.ico">
        
        <!-- Structured Data (JSON-LD) -->
        <script type="application/ld+json">
        {
          "@context": "https://schema.org",
          "@type": "WebApplication",
          "name": "뉴스 트렌드 분석 서비스",
          "alternateName": "News Trend Analyzer",
          "url": "https://news-trend-analyzer.vercel.app/",
          "description": "AI 기반 키워드 분석, 오디언스 분석, 경쟁자 분석을 제공하는 뉴스 트렌드 분석 플랫폼",
          "applicationCategory": "BusinessApplication",
          "operatingSystem": "Web",
          "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "KRW"
          },
          "featureList": [
            "키워드 분석",
            "오디언스 분석",
            "경쟁자 분석",
            "AI 기반 인사이트",
            "트렌드 분석"
          ],
          "provider": {
            "@type": "Organization",
            "name": "News Trend Analyzer"
          }
        }
        </script>
        
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@100;200;300;400;500;600;700&family=IBM+Plex+Sans:ital,wght@0,100..700;1,100..700&family=Nanum+Gothic&family=Noto+Sans+KR:wght@100..900&display=swap" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <style>
            /* ============================================
               Flat Design System - Professional & Minimal
               Based on Stitch-generated design principles
               ============================================ */
            
            /* Flat Design Variables */
            :root {
              --flat-bg-primary: #FFFFFF;
              --flat-bg-secondary: #F9FAFB;
              --flat-border: #E5E7EB;
              --flat-text-primary: #111827;
              --flat-text-secondary: #6B7280;
              --flat-accent-primary: #2563EB;
              --flat-accent-success: #10B981;
              --flat-accent-error: #EF4444;
              --flat-accent-warning: #F59E0B;
              --spacing-xs: 4px;
              --spacing-sm: 8px;
              --spacing-md: 16px;
              --spacing-lg: 24px;
              --spacing-xl: 32px;
              --spacing-2xl: 48px;
              --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
              --font-size-xs: 12px;
              --font-size-sm: 14px;
              --font-size-base: 16px;
              --font-size-lg: 18px;
              --font-size-xl: 20px;
              --font-size-2xl: 24px;
              --font-size-3xl: 30px;
              --border-width: 1px;
              --border-radius-sm: 4px;
              --border-radius-md: 8px;
              --border-radius-lg: 12px;
            }
            
            /* Flat Design 강제 적용 - 모든 그림자와 transform 제거 */
            * {
              box-shadow: none !important;
              text-shadow: none !important;
            }
            
            /* Flat Design 오버라이드 - 모든 카드, 버튼, 입력 필드 */
            .btn,
            .btn:hover,
            .btn:focus,
            .form-group input,
            .form-group input:focus,
            .form-group select,
            .form-group select:focus,
            .form-group textarea,
            .form-group textarea:focus,
            .link-card,
            .link-card:hover,
            .copy-btn,
            .copy-btn:hover,
            .result-section,
            .progress-container,
            .error {
              box-shadow: none !important;
              transform: none !important;
            }
            
            /* Flat Design 애니메이션 - transform 제거 */
            @keyframes fadeIn {
              from { opacity: 0; }
              to { opacity: 1; }
            }
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Inter', 'IBM Plex Sans KR', 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background-color: #FFFFFF;
                color: #111827;
                min-height: 100vh;
                letter-spacing: -0.48px;
                line-height: 1.5;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }
            /* 스크롤바 - 블랙/화이트 테마 */
            ::-webkit-scrollbar {
                width: 6px;
                height: 6px;
            }
            ::-webkit-scrollbar-track {
                background: #ffffff;
            }
            ::-webkit-scrollbar-thumb {
                background: #000000;
                border-radius: 3px;
            }
            ::-webkit-scrollbar-thumb:hover {
                background: #333333;
            }
            .main-container {
                display: flex;
                flex-direction: column;
                min-height: 100vh;
            }
            .header {
                background: white;
                border-bottom: 1px solid #E5E7EB;
                padding: 20px 24px;
                flex-shrink: 0;
                /* Flat Design: No box-shadow */
                box-shadow: none !important;
            }
            .header h1 {
                font-size: 1.5rem;
                font-weight: 600;
                color: #000000;
                letter-spacing: -0.8px;
                margin-bottom: 4px;
            }
            .header .subtitle {
                font-size: 0.875rem;
                color: #000000;
                letter-spacing: -0.42px;
            }
            .status-badge {
                display: inline-block;
                padding: 6px 12px;
                background: black;
                color: white;
                border: 1px solid black;
                border-radius: 6px;
                font-size: 0.75rem;
                font-weight: 500;
                margin-top: 12px;
                letter-spacing: -0.36px;
            }
            .content-wrapper {
                display: flex;
                flex: 1;
                flex-direction: column;
            }
            @media (min-width: 1024px) {
                .content-wrapper {
                    flex-direction: row;
                }
            }
            /* 좌측: 분석 설정 패널 */
            .settings-panel {
                width: 100%;
                background: white;
                border-right: 1px solid #E5E7EB;
                padding: 24px;
                overflow-y: auto;
                /* Flat Design: No box-shadow */
                box-shadow: none !important;
            }
            @media (min-width: 1024px) {
                .settings-panel {
                    width: 384px;
                    flex-shrink: 0;
                }
            }
            .settings-panel h2 {
                font-size: 1.125rem;
                font-weight: 600;
                color: #111827;
                margin-bottom: 8px;
                letter-spacing: -0.72px;
                padding-bottom: 16px;
                border-bottom: 1px solid #E5E7EB;
            }
            .settings-panel .description {
                font-size: 0.75rem;
                color: #000000;
                margin-bottom: 24px;
                letter-spacing: -0.36px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            .form-group label {
                display: block;
                font-size: 0.75rem;
                font-weight: 500;
                color: #000000;
                margin-bottom: 8px;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            .form-group input,
            .form-group select,
            .form-group textarea {
                width: 100%;
                padding: 12px;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                font-size: 0.875rem;
                background: white;
                color: #111827;
                font-family: 'Inter', 'IBM Plex Sans KR', 'Noto Sans KR', sans-serif;
                letter-spacing: -0.42px;
                transition: border-color 0.2s ease, background-color 0.2s ease;
                /* Flat Design: No box-shadow */
                box-shadow: none !important;
            }
            .form-group input:focus,
            .form-group select:focus,
            .form-group textarea:focus {
                outline: none;
                border-color: #2563EB;
                /* Flat Design: No transform, no box-shadow */
                transform: none !important;
                box-shadow: none !important;
            }
            .form-group textarea {
                resize: vertical;
                min-height: 100px;
            }
            .checkbox-group {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .checkbox-group input[type="checkbox"] {
                width: auto;
            }
            .checkbox-group label {
                margin: 0;
                text-transform: none;
                font-weight: 400;
            }
            .btn {
                width: 100%;
                padding: 12px 24px;
                background: #2563EB;
                color: white;
                border: 1px solid #2563EB;
                border-radius: 4px;
                font-size: 0.875rem;
                font-weight: 500;
                cursor: pointer;
                transition: background-color 0.2s ease, border-color 0.2s ease;
                font-family: 'Inter', 'IBM Plex Sans KR', 'Noto Sans KR', sans-serif;
                letter-spacing: -0.42px;
                min-height: 44px;
                /* Flat Design: No box-shadow */
                box-shadow: none !important;
            }
            .btn:hover:not(:disabled) {
                background: #1D4ED8;
                border-color: #1D4ED8;
                /* Flat Design: No transform */
                transform: none !important;
                box-shadow: none !important;
            }
            .btn:disabled {
                background: #666666;
                cursor: not-allowed;
                transform: none;
            }
            /* 우측: 분석 결과 패널 */
            .results-panel {
                flex: 1;
                background: white;
                padding: 24px;
                overflow-y: auto;
            }
            @media (min-width: 1024px) {
                .results-panel {
                    padding: 32px;
                }
            }
            .results-panel h2 {
                font-size: 1.5rem;
                font-weight: 600;
                color: #000000;
                margin-bottom: 8px;
                letter-spacing: -1.04px;
            }
            .results-panel .subtitle {
                font-size: 0.875rem;
                color: #000000;
                margin-bottom: 24px;
                letter-spacing: -0.42px;
            }
            .loading {
                display: none;
                text-align: center;
                padding: 40px;
                color: #000000;
            }
            .loading.show {
                display: block;
            }
            .progress-container {
                margin-top: 24px;
                padding: 20px;
                background: white;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                /* Flat Design: No box-shadow */
                box-shadow: none !important;
            }
            .progress-bar-wrapper {
                width: 100%;
                height: 24px;
                background: #f3f3f3;
                border: 1px solid black;
                border-radius: 12px;
                overflow: hidden;
                margin-bottom: 12px;
            }
            .progress-bar {
                height: 100%;
                background: black;
                transition: width 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-size: 0.75rem;
                font-weight: 600;
                letter-spacing: -0.36px;
            }
            .progress-step {
                font-size: 0.875rem;
                color: #000000;
                letter-spacing: -0.42px;
                margin-top: 8px;
            }
            .progress-percentage {
                font-size: 1.125rem;
                font-weight: 600;
                color: #000000;
                letter-spacing: -0.72px;
                margin-bottom: 8px;
            }
            .error {
                background: white;
                color: #111827;
                padding: 16px;
                border-radius: 4px;
                border: 1px solid #EF4444;
                margin-top: 20px;
                display: none;
                font-size: 0.875rem;
                letter-spacing: -0.42px;
                /* Flat Design: No box-shadow */
                box-shadow: none !important;
            }
            .error.show {
                display: block;
            }
            .result-section {
                margin-top: 24px;
                padding: 24px;
                background: white;
                border-radius: 4px;
                border: 1px solid #E5E7EB;
                display: none;
                /* Flat Design: No box-shadow */
                box-shadow: none !important;
            }
            .result-section.show {
                display: block;
                animation: fadeIn 0.3s ease;
            }
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            .result-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 16px;
                padding-bottom: 16px;
                border-bottom: 1px solid black;
            }
            .result-header h3 {
                font-size: 1.125rem;
                font-weight: 600;
                color: #000000;
                margin: 0;
                letter-spacing: -0.72px;
            }
            .copy-btn {
                background: #2563EB;
                color: white;
                padding: 8px 16px;
                border: 1px solid #2563EB;
                border-radius: 4px;
                font-size: 0.75rem;
                font-weight: 500;
                cursor: pointer;
                transition: background-color 0.2s ease, border-color 0.2s ease;
                font-family: 'Inter', 'IBM Plex Sans KR', 'Noto Sans KR', sans-serif;
                letter-spacing: -0.36px;
                /* Flat Design: No box-shadow */
                box-shadow: none !important;
            }
            .copy-btn:hover {
                background: #1D4ED8;
                border-color: #1D4ED8;
                /* Flat Design: No transform */
                transform: none !important;
                box-shadow: none !important;
            }
            .result-content {
                background: white;
                padding: 24px 20px;
                border-radius: 4px;
                font-family: 'Inter', 'IBM Plex Sans KR', 'Noto Sans KR', sans-serif;
                font-size: 0.875rem;
                line-height: 1.65;
                max-height: 70vh;
                overflow-y: auto;
                border: 1px solid #E5E7EB;
                color: #111827;
                letter-spacing: -0.42px;
                box-shadow: none !important;
            }
            /* 분석 결과 문서 스타일 (UI/UX: 가독성·계층·여백) */
            .result-content {
                background: white;
                padding: 40px; /* A4 여백 시뮬레이션 */
                border-radius: 2px;
                font-family: 'Inter', 'IBM Plex Sans KR', 'Noto Sans KR', sans-serif;
                font-size: 10.5pt; /* 문서 표준 폰트 크기 */
                line-height: 1.6;
                max-height: 70vh;
                overflow-y: auto;
                border: 1px solid #E5E7EB;
                color: #111827;
                letter-spacing: -0.02em;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important; /* 종이 질감용 그림자 복원 */
                max-width: 210mm; /* A4 너비 */
                margin: 0 auto; /* 중앙 정렬 */
            }
            .result-content .report-body { max-width: 100%; margin: 0 auto; }
            .result-content .report-body .report-h1 { font-size: 22pt; font-weight: 700; color: #111827; margin: 0 0 20px; padding-bottom: 12px; border-bottom: 2px solid #111827; letter-spacing: -0.03em; line-height: 1.3; }
            .result-content .report-body .report-h1:first-child { margin-top: 0; }
            .result-content .report-body .report-h2 { font-size: 16pt; font-weight: 700; color: #111827; margin: 28px 0 12px; padding-bottom: 8px; border-bottom: 1px solid #E5E7EB; letter-spacing: -0.025em; line-height: 1.4; break-after: avoid; }
            .result-content .report-body .report-h3 { font-size: 13pt; font-weight: 600; color: #1F2937; margin: 20px 0 10px; letter-spacing: -0.02em; line-height: 1.45; break-after: avoid; }
            .result-content .report-body .report-p { margin: 0 0 12px; color: #374151; line-height: 1.7; text-align: justify; }
            .result-content .report-body .report-ul { margin: 8px 0 16px; padding-left: 20px; list-style-type: disc; }
            .result-content .report-body .report-ol { margin: 8px 0 16px; padding-left: 20px; list-style-type: decimal; }
            .result-content .report-body .report-li { margin-bottom: 6px; line-height: 1.65; color: #374151; padding-left: 4px; }
            .result-content .report-body .report-hr { border: none; border-top: 1px solid #E5E7EB; margin: 24px 0; }
            .result-content .report-body strong { font-weight: 600; color: #111827; }
            .result-content .report-body .report-meta { font-size: 9pt; color: #6B7280; margin-top: 32px; padding-top: 20px; border-top: 1px solid #E5E7EB; text-align: center; }
            
            @media (max-width: 640px) {
                .result-content { padding: 20px; max-width: 100%; box-shadow: none !important; border: none; }
                .result-content .report-body { max-width: 100%; }
            }
            
            @media print {
                body * {
                    visibility: hidden;
                }
                .result-content, .result-content * {
                    visibility: visible;
                }
                .result-content {
                    position: absolute;
                    left: 0;
                    top: 0;
                    width: 100%;
                    max-width: 100%;
                    padding: 0;
                    margin: 0;
                    box-shadow: none !important;
                    border: none;
                    overflow: visible;
                    max-height: none;
                }
                .header, .settings-panel, .result-header, .empty-state, .loading, .error {
                    display: none !important;
                }
            }
            .links {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 16px;
                margin-top: 32px;
                padding-top: 32px;
                border-top: 1px solid black;
            }
            .link-card {
                background: white;
                border: 1px solid #E5E7EB;
                border-radius: 4px;
                padding: 20px;
                text-decoration: none;
                color: #111827;
                transition: background-color 0.2s ease, color 0.2s ease, border-color 0.2s ease;
                display: block;
                text-align: center;
                /* Flat Design: No box-shadow */
                box-shadow: none !important;
            }
            .link-card:hover {
                background: #F9FAFB;
                color: #2563EB;
                border-color: #2563EB;
                /* Flat Design: No transform */
                transform: none !important;
                box-shadow: none !important;
            }
            .link-card h3 {
                font-size: 1rem;
                font-weight: 600;
                margin-bottom: 8px;
                letter-spacing: -0.48px;
            }
            .link-card p {
                font-size: 0.75rem;
                letter-spacing: -0.36px;
            }
            .version {
                text-align: center;
                color: #000000;
                margin-top: 32px;
                padding-top: 24px;
                border-top: 1px solid black;
                font-size: 0.75rem;
                letter-spacing: -0.36px;
            }
            .empty-state {
                text-align: center;
                padding: 60px 20px;
                color: #000000;
            }
            .empty-state p {
                font-size: 0.875rem;
                letter-spacing: -0.42px;
            }
        </style>
    </head>
    <body>
        <div class="main-container">
            <!-- 헤더 -->
            <div class="header">
                <h1>핵심 트렌드 분석 서비스</h1>
                <p class="subtitle">AI 기반 키워드, 오디언스, 종합 분석 플랫폼</p>
                <span class="status-badge">서비스 정상 운영 중</span>
            </div>
            
            <!-- 메인 컨텐츠: 좌우 분할 -->
            <div class="content-wrapper">
                <!-- 좌측: 분석 설정 패널 -->
                <div class="settings-panel">
                    <h2>분석 설정</h2>
                    <p class="description">분석할 키워드와 옵션을 선택하세요</p>
                    
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
                                <option value="comprehensive">종합 분석</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label>분석 기간 설정 *</label>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                                <div>
                                    <label for="start_date" style="font-size: 0.75rem; margin-bottom: 4px; display: block;">시작일</label>
                                    <input type="date" id="start_date" name="start_date" required>
                                </div>
                                <div>
                                    <label for="end_date" style="font-size: 0.75rem; margin-bottom: 4px; display: block;">종료일</label>
                                    <input type="date" id="end_date" name="end_date" required>
                                </div>
                            </div>
                            <p style="font-size: 0.75rem; color: #666; margin-top: 8px; letter-spacing: -0.36px;">
                                분석할 기간을 선택하세요. 이 기간 동안의 트렌드와 변화를 중심으로 분석합니다.
                            </p>
                        </div>
                        
                        <div class="form-group">
                            <label for="additional_context">추가 컨텍스트 (선택사항)</label>
                            <textarea id="additional_context" name="additional_context" 
                                      placeholder="추가로 제공할 컨텍스트 정보를 입력하세요"></textarea>
                        </div>
                        
                        <div class="form-group checkbox-group">
                            <input type="checkbox" id="use_gemini" name="use_gemini">
                            <label for="use_gemini">Gemini API 사용 (OpenAI 대신)</label>
                        </div>
                        
                        <button type="submit" class="btn" id="analyzeBtn">분석 시작</button>
                    </form>
                </div>
                
                <!-- 우측: 분석 결과 패널 -->
                <div class="results-panel">
                    <h2>분석 결과</h2>
                    <p class="subtitle">분석 결과가 여기에 표시됩니다</p>
                    
                    <div class="loading" id="loading">
                        <div class="progress-container" id="progressContainer" style="display: none;">
                            <div class="progress-percentage" id="progressPercentage">0%</div>
                            <div class="progress-bar-wrapper">
                                <div class="progress-bar" id="progressBar" style="width: 0%;">0%</div>
                            </div>
                            <div class="progress-step" id="progressStep">분석 준비 중...</div>
                        </div>
                    </div>
                    
                    <div class="error" id="error"></div>
                    
                    <div class="empty-state" id="emptyState">
                        <p>좌측에서 분석 설정을 입력하고 "분석 시작" 버튼을 클릭하세요.</p>
                    </div>
                    
                    <div class="result-section" id="resultSection">
                        <div class="result-header">
                            <h3>분석 결과</h3>
                            <button class="copy-btn" id="copyBtn" onclick="copyToClipboard()">복사</button>
                        </div>
                        <div class="result-content" id="resultContent"></div>
                    </div>
                    
                    <div class="version">
                        Version 1.0.0 | 뉴스 트렌드 분석 서비스
                    </div>
                </div>
            </div>
        </div>
        
        <script>
            // 브라우저 확장 프로그램 오류 필터링 (앱 기능에 영향 없음)
            window.addEventListener("unhandledrejection", function(event) {
                const error = event.reason;
                const errorMessage = error?.message || error?.toString() || '';
                
                // 무시해도 되는 브라우저 확장 프로그램 오류 패턴
                const ignoredPatterns = [
                    /message channel closed/i,
                    /asynchronous response/i,
                    /Extension context invalidated/i,
                    /Receiving end does not exist/i,
                    /liner-core/i,
                    /Violation/i
                ];
                
                // 무시해도 되는 오류는 기본 동작 방지
                if (ignoredPatterns.some(pattern => pattern.test(errorMessage))) {
                    event.preventDefault();
                    return;
                }
            });
            
            // 일반 오류 핸들러 (브라우저 확장 프로그램 오류 필터링)
            window.addEventListener("error", function(event) {
                const errorMessage = event.message || '';
                
                // 무시해도 되는 브라우저 확장 프로그램 오류 패턴
                const ignoredPatterns = [
                    /message channel closed/i,
                    /asynchronous response/i,
                    /Extension context invalidated/i,
                    /Receiving end does not exist/i,
                    /liner-core/i,
                    /Violation/i
                ];
                
                // 무시해도 되는 오류는 기본 동작 방지
                if (ignoredPatterns.some(pattern => pattern.test(errorMessage))) {
                    event.preventDefault();
                    return true;
                }
            }, true);
            
            // 기본 날짜 설정 (최근 3개월) 및 URL 파라미터 처리
            window.addEventListener("DOMContentLoaded", function() {
                const today = new Date();
                const threeMonthsAgo = new Date();
                threeMonthsAgo.setMonth(today.getMonth() - 3);
                
                // 길이 제한 상수
                const MAX_TARGET_KEYWORD_LENGTH = 200;
                const MAX_ADDITIONAL_CONTEXT_LENGTH = 2000;
                
                // 허용된 target_type 값
                const allowedTypes = ["keyword", "audience", "comprehensive"];
                
                // 날짜 유효성 검사 헬퍼 함수
                function isValidDate(dateString) {
                    if (!dateString) return false;
                    
                    // YYYY-MM-DD 형식 정규식 검사
                    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
                    if (!dateRegex.test(dateString)) {
                        return false;
                    }
                    
                    // Date 객체로 파싱하여 유효성 검사
                    const date = new Date(dateString + "T00:00:00");
                    if (isNaN(date.getTime())) {
                        return false;
                    }
                    
                    // 입력된 문자열과 파싱된 날짜가 일치하는지 확인 (예: 2025-13-01 같은 경우 방지)
                    const [year, month, day] = dateString.split("-").map(Number);
                    return date.getFullYear() === year &&
                           date.getMonth() === month - 1 &&
                           date.getDate() === day;
                }
                
                // URL 파라미터 읽기
                const urlParams = new URLSearchParams(window.location.search);
                
                const targetKeywordInput = document.getElementById("target_keyword");
                const targetTypeSelect = document.getElementById("target_type");
                const startDateInput = document.getElementById("start_date");
                const endDateInput = document.getElementById("end_date");
                const additionalContextInput = document.getElementById("additional_context");
                const useGeminiCheckbox = document.getElementById("use_gemini");
                
                // URL 파라미터로 폼 채우기 (검증 포함)
                
                // target_keyword 처리 (길이 제한 + 디코딩 에러 처리)
                if (urlParams.has("target_keyword") && targetKeywordInput) {
                    const keywordValue = urlParams.get("target_keyword");
                    if (keywordValue) {
                        try {
                            // URLSearchParams는 자동 디코딩하지만, 이중 인코딩된 경우를 대비
                            const decodedValue = decodeURIComponent(keywordValue);
                            if (decodedValue.length <= MAX_TARGET_KEYWORD_LENGTH) {
                                targetKeywordInput.value = decodedValue;
                            }
                        } catch (e) {
                            // 잘못된 인코딩 처리 - 무시
                            console.warn("Invalid URL encoding for target_keyword:", e);
                        }
                    }
                }
                
                // target_type 처리 (허용된 값 검증)
                if (urlParams.has("target_type") && targetTypeSelect) {
                    const targetTypeValue = urlParams.get("target_type");
                    if (targetTypeValue) {
                        // 허용된 타입 배열에서 확인
                        if (allowedTypes.includes(targetTypeValue)) {
                            // select 옵션에서도 확인
                            const optionExists = Array.from(targetTypeSelect.options).some(
                                option => option.value === targetTypeValue
                            );
                            if (optionExists) {
                                targetTypeSelect.value = targetTypeValue;
                            }
                        }
                    }
                }
                
                // start_date 처리 (날짜 유효성 검사 + 폴백)
                if (urlParams.has("start_date") && startDateInput) {
                    const startDateValue = urlParams.get("start_date");
                    if (startDateValue && isValidDate(startDateValue)) {
                        startDateInput.value = startDateValue;
                    } else if (startDateInput) {
                        startDateInput.value = threeMonthsAgo.toISOString().split("T")[0];
                    }
                } else if (startDateInput) {
                    startDateInput.value = threeMonthsAgo.toISOString().split("T")[0];
                }
                
                // end_date 처리 (날짜 유효성 검사 + 폴백)
                if (urlParams.has("end_date") && endDateInput) {
                    const endDateValue = urlParams.get("end_date");
                    if (endDateValue && isValidDate(endDateValue)) {
                        endDateInput.value = endDateValue;
                    } else if (endDateInput) {
                        endDateInput.value = today.toISOString().split("T")[0];
                    }
                } else if (endDateInput) {
                    endDateInput.value = today.toISOString().split("T")[0];
                }
                
                // additional_context 처리 (길이 제한 + 디코딩 에러 처리)
                if (urlParams.has("additional_context") && additionalContextInput) {
                    const contextValue = urlParams.get("additional_context");
                    if (contextValue) {
                        try {
                            const decodedValue = decodeURIComponent(contextValue);
                            if (decodedValue.length <= MAX_ADDITIONAL_CONTEXT_LENGTH) {
                                additionalContextInput.value = decodedValue;
                            }
                        } catch (e) {
                            // 잘못된 인코딩 처리 - 무시
                            console.warn("Invalid URL encoding for additional_context:", e);
                        }
                    }
                }
                
                // use_gemini 처리 (강화된 파싱)
                if (urlParams.has("use_gemini") && useGeminiCheckbox) {
                    const geminiValue = urlParams.get("use_gemini");
                    if (geminiValue) {
                        const normalizedValue = geminiValue.toLowerCase().trim();
                        useGeminiCheckbox.checked = normalizedValue === "true" || 
                                                    normalizedValue === "1" || 
                                                    normalizedValue === "on";
                    }
                }
            });
            
            // 클립보드 복사 함수
            function escapeReportHtml(s) {
                if (!s) return "";
                return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
            }
            function markdownToReportHtml(text) {
                if (!text || typeof text !== "string") return "<div class=\"report-body\"></div>";
                var escaped = escapeReportHtml(text);
                var lines = text.split("\\n");
                var out = [];
                var inList = false;
                var listTag = "ul";
                function flushList() {
                    if (inList) { out.push("</" + listTag + ">"); inList = false; }
                }
                for (var i = 0; i < lines.length; i++) {
                    var line = lines[i];
                    var trimmed = line.trim();
                    if (trimmed === "" || trimmed === "---") {
                        flushList();
                        if (trimmed === "---") out.push("<hr class=\"report-hr\" />");
                        continue;
                    }
                    if (trimmed.indexOf("### ") === 0) {
                        flushList();
                        out.push("<h3 class=\"report-h3\">" + escapeReportHtml(trimmed.slice(4)) + "</h3>");
                    } else if (trimmed.indexOf("## ") === 0) {
                        flushList();
                        out.push("<h2 class=\"report-h2\">" + escapeReportHtml(trimmed.slice(3)) + "</h2>");
                    } else if (trimmed.indexOf("# ") === 0) {
                        flushList();
                        out.push("<h1 class=\"report-h1\">" + escapeReportHtml(trimmed.slice(2)) + "</h1>");
                    } else if (trimmed.indexOf("- ") === 0) {
                        if (!inList) { out.push("<ul class=\"report-ul\">"); inList = true; listTag = "ul"; }
                        var content = escapeReportHtml(trimmed.slice(2));
                        content = content.replace(/\\*\\*([^*]+)\\*\\*/g, "<strong>$1</strong>");
                        out.push("<li class=\"report-li\">" + content + "</li>");
                    } else if (/^\\d+\\.\\s/.test(trimmed)) {
                        if (!inList) { out.push("<ol class=\"report-ol\">"); inList = true; listTag = "ol"; }
                        var content = escapeReportHtml(trimmed.replace(/^\\d+\\.\\s/, ""));
                        content = content.replace(/\\*\\*([^*]+)\\*\\*/g, "<strong>$1</strong>");
                        out.push("<li class=\"report-li\">" + content + "</li>");
                    } else {
                        flushList();
                        var content = escapeReportHtml(trimmed);
                        content = content.replace(/\\*\\*([^*]+)\\*\\*/g, "<strong>$1</strong>");
                        out.push("<p class=\"report-p\">" + content + "</p>");
                    }
                }
                flushList();
                var html = out.join("");
                return "<div class=\"report-body\">" + html + "</div>";
            }
            function copyToClipboard() {
                const resultContent = document.getElementById("resultContent");
                const text = resultContent.innerText || resultContent.textContent || "";
                
                navigator.clipboard.writeText(text).then(function() {
                    const copyBtn = document.getElementById("copyBtn");
                    const originalText = copyBtn.textContent;
                    copyBtn.textContent = "복사됨!";
                    copyBtn.style.background = "#333333";
                    
                    setTimeout(function() {
                        copyBtn.textContent = originalText;
                        copyBtn.style.background = "black";
                    }, 2000);
                }).catch(function(err) {
                    console.error("복사 실패:", err);
                    alert("복사에 실패했습니다. 수동으로 선택하여 복사해주세요.");
                });
            }
            
            document.getElementById("analysisForm").addEventListener("submit", async function(e) {
                e.preventDefault();
                
                const form = e.target;
                const loading = document.getElementById("loading");
                const error = document.getElementById("error");
                const resultSection = document.getElementById("resultSection");
                const resultContent = document.getElementById("resultContent");
                const analyzeBtn = document.getElementById("analyzeBtn");
                const emptyState = document.getElementById("emptyState");
                
                // 초기화
                loading.classList.add("show");
                error.classList.remove("show");
                resultSection.classList.remove("show");
                emptyState.style.display = "none";
                analyzeBtn.disabled = true;
                
                // 진행률 표시 초기화 및 표시
                const progressContainer = document.getElementById("progressContainer");
                const progressBar = document.getElementById("progressBar");
                const progressPercentage = document.getElementById("progressPercentage");
                const progressStep = document.getElementById("progressStep");
                
                if (progressContainer) {
                    progressContainer.style.display = "block";
                }
                if (progressBar) {
                    progressBar.style.width = "0%";
                    progressBar.textContent = "0%";
                }
                if (progressPercentage) {
                    progressPercentage.textContent = "0%";
                }
                if (progressStep) {
                    progressStep.textContent = "분석 준비 중...";
                }
                
                // 폼 데이터 수집
                const startDate = document.getElementById("start_date").value;
                const endDate = document.getElementById("end_date").value;
                
                // 날짜 유효성 검사
                if (!startDate || !endDate) {
                    error.textContent = "시작일과 종료일을 모두 입력해주세요.";
                    error.classList.add("show");
                    loading.classList.remove("show");
                    analyzeBtn.disabled = false;
                    return;
                }
                
                if (new Date(startDate) > new Date(endDate)) {
                    error.textContent = "시작일은 종료일보다 이전이어야 합니다.";
                    error.classList.add("show");
                    loading.classList.remove("show");
                    analyzeBtn.disabled = false;
                    return;
                }
                
                const formData = {
                    target_keyword: document.getElementById("target_keyword").value,
                    target_type: document.getElementById("target_type").value,
                    additional_context: document.getElementById("additional_context").value || null,
                    use_gemini: document.getElementById("use_gemini").checked,
                    start_date: startDate,
                    end_date: endDate,
                    include_sentiment: true,
                    include_recommendations: true
                };
                
                try {
                    // 분석 단계별 진행률 정의
                    const analysisSteps = [
                        { progress: 5, step: "분석 준비 중..." },
                        { progress: 10, step: "프롬프트 생성 중..." },
                        { progress: 15, step: formData.use_gemini ? "Gemini API 호출 중..." : "OpenAI API 호출 중..." },
                        { progress: 30, step: "AI API 요청 전송 중..." },
                        { progress: 50, step: "AI 응답 대기 중..." },
                        { progress: 70, step: "AI 응답 수신 완료, 결과 파싱 중..." },
                        { progress: 80, step: "JSON 파싱 완료, 결과 정리 중..." },
                        { progress: 90, step: formData.include_sentiment ? "정성적 분석 수행 중..." : "결과 정리 중..." },
                        { progress: 95, step: formData.include_recommendations ? "키워드 추천 생성 중..." : "결과 정리 중..." },
                        { progress: 100, step: "분석 완료" }
                    ];
                    
                    let currentStepIndex = 0;
                    let progressInterval = null;
                    
                    // 진행률 인터벌 설정 (나중에 정리할 수 있도록 변수에 저장)
                    progressInterval = setInterval(() => {
                        if (currentStepIndex < analysisSteps.length - 1) {
                            const currentStep = analysisSteps[currentStepIndex];
                            
                            if (progressBar) {
                                progressBar.style.width = currentStep.progress + '%';
                                progressBar.textContent = currentStep.progress + '%';
                            }
                            if (progressPercentage) {
                                progressPercentage.textContent = currentStep.progress + '%';
                            }
                            if (progressStep) {
                                progressStep.textContent = currentStep.step;
                            }
                            
                            // 다음 단계로 진행 (점진적으로)
                            if (currentStepIndex < analysisSteps.length - 1) {
                                currentStepIndex++;
                            }
                        }
                    }, 2000); // 2초마다 다음 단계로
                    
                    // API URL 설정 (스트리밍 엔드포인트 사용)
                    const apiBaseUrl = window.location.origin;
                    const apiUrl = apiBaseUrl + "/api/target/analyze/stream";
                    
                    console.log("API 스트리밍 호출:", apiUrl, formData);
                    
                    // 결과 컨텐츠 초기화 및 표시
                    resultSection.classList.add("show");
                    resultContent.innerHTML = "";
                    resultContent.style.display = "block";
                    
                    let accumulatedResult = null;
                    let currentSection = "executive_summary";
                    const sectionHeaders = {
                        "executive_summary": "## Executive Summary\\\\n\\\\n",
                        "key_findings": "\\\\n## Key Findings\\\\n\\\\n",
                        "detailed_analysis": "\\\\n## Detailed Analysis\\\\n\\\\n",
                        "strategic_recommendations": "\\\\n## Strategic Recommendations\\\\n\\\\n"
                    };
                    
                    // 섹션 헤더 추가 함수
                    function addSectionHeader(section) {
                        if (sectionHeaders[section] && !resultContent.textContent.includes(sectionHeaders[section])) {
                            resultContent.textContent += sectionHeaders[section];
                        }
                    }
                    
                    const response = await fetch(apiUrl, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify(formData)
                    });
                    
                    console.log("API 스트리밍 응답 상태:", response.status, response.statusText);
                    
                    if (!response.ok) {
                        let errorData = {};
                        try {
                            errorData = await response.json();
                        } catch (e) {
                            try {
                                errorData = { detail: await response.text() || "분석 요청 실패" };
                            } catch (textError) {
                                errorData = { detail: `HTTP ${response.status}: ${response.statusText}` };
                            }
                        }
                        console.error("API 오류:", errorData);
                        const errorMessage = errorData.detail || errorData.error || errorData.message || `HTTP ${response.status}: 분석 요청 실패`;
                        throw new Error(errorMessage);
                    }
                    
                    // 스트리밍 응답 읽기 (응답 본문 확인)
                    if (!response.body) {
                        throw new Error("스트리밍 응답 본문을 읽을 수 없습니다.");
                    }
                    
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder();
                    let buffer = "";
                    let hasReceivedData = false;
                    let streamError = null;
                    
                    try {
                        while (true) {
                            const { done, value } = await reader.read();
                            
                            if (done) {
                                console.log("스트리밍 완료");
                                break;
                            }
                            
                            hasReceivedData = true;
                            
                            // 디코딩 및 버퍼에 추가
                            buffer += decoder.decode(value, { stream: true });
                            
                            // 줄 단위로 분리하여 처리 (올바른 줄바꿈 문자 사용)
                            const lines = buffer.split("\n");
                            buffer = lines.pop() || ""; // 마지막 불완전한 줄은 버퍼에 유지
                            
                            for (const line of lines) {
                                if (!line.trim()) {
                                    continue;
                                }
                                
                                try {
                                    const chunk = JSON.parse(line);
                                    console.log("스트리밍 청크:", chunk);
                                    
                                    // 문장 타입 처리
                                    if (chunk.type === "sentence") {
                                        const section = chunk.section || "executive_summary";
                                        
                                        // 섹션이 변경되면 헤더 추가
                                        if (section !== currentSection) {
                                            addSectionHeader(section);
                                            currentSection = section;
                                        }
                                        
                                        // 문장 추가 (실시간 표시)
                                        resultContent.textContent += chunk.content + " ";
                                        
                                        // 스크롤을 맨 아래로
                                        resultContent.scrollTop = resultContent.scrollHeight;
                                    }
                                    // 진행 상황 처리
                                    else if (chunk.type === "progress") {
                                        if (progressBar) {
                                            progressBar.style.width = chunk.progress + "%";
                                            progressBar.textContent = chunk.progress + "%";
                                        }
                                        if (progressPercentage) {
                                            progressPercentage.textContent = chunk.progress + "%";
                                        }
                                        if (progressStep) {
                                            progressStep.textContent = chunk.message || "분석 중...";
                                        }
                                    }
                                    // 완료 처리
                                    else if (chunk.type === "complete") {
                                        accumulatedResult = chunk.data;
                                        
                                        if (progressBar) {
                                            progressBar.style.width = "100%";
                                            progressBar.textContent = "100%";
                                        }
                                        if (progressPercentage) {
                                            progressPercentage.textContent = "100%";
                                        }
                                        if (progressStep) {
                                            progressStep.textContent = "분석 완료";
                                        }
                                        
                                        // 최종 결과가 있으면 추가 정보 표시
                                        if (chunk.data) {
                                            console.log("최종 결과 수신:", chunk.data);
                                        }
                                        
                                        break;
                                    }
                                    // 오류 처리
                                    else if (chunk.type === "error") {
                                        streamError = new Error(chunk.message || "알 수 없는 오류가 발생했습니다.");
                                        throw streamError;
                                    }
                                } catch (parseError) {
                                    // JSON 파싱 오류는 경고만 (스트리밍 중 일부 데이터 손실 가능)
                                    if (parseError instanceof SyntaxError) {
                                        console.warn("JSON 파싱 실패 (무시):", line.substring(0, 100), parseError);
                                    } else {
                                        // 다른 오류는 재발생
                                        throw parseError;
                                    }
                                }
                            }
                        }
                    } catch (streamReadError) {
                        console.error("스트리밍 읽기 오류:", streamReadError);
                        if (!streamError) {
                            streamError = streamReadError;
                        }
                    }
                    
                    // 스트리밍 중 오류가 발생했거나 데이터를 받지 못한 경우
                    if (streamError) {
                        throw streamError;
                    }
                    
                    if (!hasReceivedData) {
                        throw new Error("서버로부터 데이터를 받지 못했습니다. API 서버 상태를 확인해주세요.");
                    }
                    
                    // 버퍼에 남은 데이터 처리
                    if (buffer.trim()) {
                        try {
                            const chunk = JSON.parse(buffer);
                            if (chunk.type === "sentence") {
                                const section = chunk.section || "executive_summary";
                                if (section !== currentSection) {
                                    addSectionHeader(section);
                                    currentSection = section;
                                }
                                resultContent.textContent += chunk.content + " ";
                                resultContent.scrollTop = resultContent.scrollHeight;
                            } else if (chunk.type === "complete") {
                                accumulatedResult = chunk.data;
                            }
                        } catch (parseError) {
                            console.warn("버퍼 파싱 실패:", buffer, parseError);
                        }
                    }
                    
                    // 기존 코드와의 호환성을 위해 data 변수 설정
                        let data = null;
                    
                    if (accumulatedResult) {
                        data = {
                            success: true,
                            data: accumulatedResult
                        };
                        console.log("최종 분석 결과 수신:", Object.keys(accumulatedResult));
                    } else {
                        // accumulatedResult가 없지만 resultContent에 텍스트가 있는 경우
                        const displayedText = resultContent.textContent || "";
                        if (displayedText.trim().length > 0) {
                            // 표시된 텍스트가 있으면 최소한의 결과 구조 생성
                            data = {
                                success: true,
                                data: {
                                    executive_summary: displayedText,
                                    target_keyword: formData.target_keyword,
                                    target_type: formData.target_type,
                                    note: "스트리밍 결과가 완전히 수신되지 않았지만 일부 내용은 표시되었습니다."
                                }
                            };
                            console.log("부분 결과 사용 (텍스트만 수신)");
                        } else {
                            // 아무것도 받지 못한 경우
                            data = {
                                success: false,
                                error: "분석 결과를 받지 못했습니다. 서버 로그를 확인하거나 잠시 후 다시 시도해주세요."
                            };
                            console.error("분석 결과 없음 - accumulatedResult와 displayedText 모두 비어있음");
                        }
                    }
                    
                    console.log("최종 분석 결과:", data);
                    
                    // 최종 진행률 업데이트 (이미 선언된 변수 사용)
                    if (progressBar) {
                        progressBar.style.width = "100%";
                        progressBar.textContent = "100%";
                    }
                    if (progressPercentage) {
                        progressPercentage.textContent = "100%";
                    }
                    if (progressStep) {
                        progressStep.textContent = "분석 완료";
                    }
                    
                    // 진행률 정보가 있으면 표시
                    if (data.data && data.data.progress_info) {
                        const progressInfo = data.data.progress_info;
                        if (progressStep) {
                            progressStep.textContent = progressInfo.current_step || "분석 완료";
                        }
                    }
                    
                    if (data && data.success && data.data) {
                        // 결과를 Markdown 형식으로 포맷팅
                        let resultText = "";
                        let analysisData = null;
                        
                        // 디버깅: 받은 데이터 로깅
                        console.log("API 응답 받음:", {
                            success: data.success,
                            hasData: !!data.data,
                            dataType: typeof data.data,
                            dataKeys: data.data ? Object.keys(data.data) : []
                        });
                        
                        // JSON 데이터 파싱 - 여러 구조 지원
                        console.log("받은 데이터 구조:", Object.keys(data.data || {}));
                        
                        // data.data를 기본으로 사용하고, analysis 필드가 있으면 병합
                        if (data.data && typeof data.data === "object" && !Array.isArray(data.data)) {
                            // data.data를 기본으로 사용 (한글 키도 포함)
                            analysisData = { ...data.data };
                            
                            // data.data.report가 있으면 그것을 최우선으로 사용 (오디언스 분석 등)
                            if (data.data.report && typeof data.data.report === "object") {
                                console.log("data.data.report 감지됨, analysisData로 사용");
                                analysisData = { ...data.data.report };
                            }
                            
                            // 한글 키가 있는지 확인
                            const hasKoreanKeys = Object.keys(analysisData).some(key => 
                                key === "Executive Summary" || 
                                key === "분석 개요" || 
                                key === "Key Insights" || 
                                key === "오디언스 상세 분석" ||
                                key === "전략 제안" ||
                                key === "실행 로드맵" ||
                                key === "리스크 & 거버넌스" ||
                                key === "부록"
                            );
                            
                            if (hasKoreanKeys) {
                                console.log("한글 키 감지됨:", Object.keys(analysisData).filter(key => 
                                    key === "Executive Summary" || 
                                    key === "분석 개요" || 
                                    key === "Key Insights" || 
                                    key === "오디언스 상세 분석" ||
                                    key === "전략 제안" ||
                                    key === "실행 로드맵" ||
                                    key === "리스크 & 거버넌스" ||
                                    key === "부록"
                                ));
                            }
                            
                            // analysis 필드가 있고 그것이 객체인 경우 병합
                            if (data.data.analysis && typeof data.data.analysis === "object") {
                                analysisData = { ...analysisData, ...data.data.analysis };
                                console.log("analysis 필드 병합:", Object.keys(analysisData));
                            }
                            // analysis 필드가 문자열인 경우 (JSON 파싱 후 병합)
                            else if (data.data.analysis && typeof data.data.analysis === "string") {
                                try {
                                    let cleanAnalysis = data.data.analysis;
                                    // 마크다운 코드 블록 제거
                                    const codeBlockStart = "```json";
                                    const codeBlockEnd = "```";
                                    if (cleanAnalysis.includes(codeBlockStart)) {
                                        const startIdx = cleanAnalysis.indexOf(codeBlockStart);
                                        const endIdx = cleanAnalysis.lastIndexOf(codeBlockEnd);
                                        if (endIdx > startIdx) {
                                            cleanAnalysis = cleanAnalysis.substring(0, startIdx) + 
                                                          cleanAnalysis.substring(startIdx + codeBlockStart.length, endIdx) + 
                                                          cleanAnalysis.substring(endIdx + codeBlockEnd.length);
                                        }
                                    }
                                    cleanAnalysis = cleanAnalysis.replace(/```/g, "").trim();
                                    const parsedAnalysis = JSON.parse(cleanAnalysis);
                                    // 파싱된 analysis와 병합 (analysis 필드 내용이 우선)
                                    analysisData = { ...analysisData, ...parsedAnalysis };
                                    console.log("JSON 파싱 후 병합:", Object.keys(analysisData));
                                } catch (parseError) {
                                    console.warn("JSON 파싱 실패, analysis 필드 무시:", parseError);
                                    // 파싱 실패 시 analysis 필드는 무시하고 data.data만 사용
                                }
                            }
                            
                            console.log("최종 analysisData 구조:", Object.keys(analysisData));
                        }
                        // data가 직접 분석 결과인 경우
                        else if (data.executive_summary || data.key_findings || data.detailed_analysis) {
                            analysisData = data;
                            console.log("data 직접 사용:", Object.keys(analysisData));
                        }
                        // 그 외의 경우
                        else {
                            console.warn("알 수 없는 데이터 구조:", data);
                            analysisData = data.data || data || {};
                        }
                        
                        console.log("파싱된 analysisData 최종 구조:", Object.keys(analysisData || {}));
                        console.log("analysisData 상세 (일부):", JSON.stringify({
                            executive_summary: analysisData?.executive_summary?.substring(0, 100),
                            has_key_findings: !!analysisData?.key_findings,
                            has_detailed_analysis: !!analysisData?.detailed_analysis,
                            has_sentiment: !!analysisData?.sentiment,
                            has_context: !!analysisData?.context,
                            has_tone: !!analysisData?.tone,
                            has_recommendations: !!analysisData?.recommendations
                        }, null, 2));
                        
                        // Markdown 형식으로 변환
                        const targetKeyword = formData.target_keyword;
                        const targetType = formData.target_type;
                        const typeNames = {
                            "keyword": "키워드",
                            "audience": "오디언스",
                            "comprehensive": "종합"
                        };
                        
                        resultText = "# 타겟 분석 보고서\\n\\n";
                        resultText += "**분석 대상**: " + targetKeyword + "\\n";
                        resultText += "**분석 유형**: " + (typeNames[targetType] || targetType) + " 분석\\n";
                        resultText += "**분석 기간**: " + formData.start_date + " ~ " + formData.end_date + "\\n";
                        resultText += "**분석 일시**: " + new Date().toLocaleString("ko-KR") + "\\n\\n";
                        resultText += "---\\n\\n";
                        
                        // 키 매핑 함수 (한글/영문 키 모두 지원) - 모든 분석 유형에 적용
                        function mapKeys(data) {
                            if (!data || typeof data !== "object") return data;
                            
                            const mapped = { ...data };
                            
                            // 영문 키 -> snake_case 키 매핑 (키워드/오디언스/종합 공통)
                            const englishKeyMapping = {
                                "Executive Summary": "executive_summary",
                                "Analysis Overview": "analysis_overview",
                                "Key Insights": "key_insights",
                                "Key Findings": "key_findings",
                                "Audience Detailed Analysis": "detailed_audience_analysis",
                                "Strategic Recommendations": "strategic_recommendations",
                                "Execution Roadmap": "execution_roadmap",
                                "Risks & Governance": "risk_governance",
                                "Appendix": "appendix"
                            };
                            
                            // 한글 키 -> snake_case/영문 키 매핑
                            const koreanKeyMapping = {
                                "분석 개요": "analysis_overview",
                                "오디언스 상세 분석": "detailed_audience_analysis",
                                "상세 분석": "detailed_analysis",
                                "전략 제안": "strategic_recommendations",
                                "전략적 시사점": "strategic_recommendations",
                                "실행 로드맵": "execution_roadmap",
                                "리스크 & 거버넌스": "risk_governance",
                                "리스크 & 대응": "risk_governance",
                                "부록": "appendix"
                            };
                            
                            // 영문 키를 snake_case로 매핑
                            Object.keys(englishKeyMapping).forEach(englishKey => {
                                if (mapped[englishKey] !== undefined) {
                                    const snakeKey = englishKeyMapping[englishKey];
                                    if (!mapped[snakeKey]) {
                                        mapped[snakeKey] = mapped[englishKey];
                                    }
                                }
                            });
                            
                            // 한글 키를 영문 키로 매핑
                            Object.keys(koreanKeyMapping).forEach(koreanKey => {
                                if (mapped[koreanKey] !== undefined) {
                                    const englishKey = koreanKeyMapping[koreanKey];
                                    if (!mapped[englishKey]) {
                                        mapped[englishKey] = mapped[koreanKey];
                                    }
                                }
                            });
                            
                            return mapped;
                        }
                        
                        // 객체/배열을 읽기 쉬운 문서 형식으로 변환 (JSON 대신)
                        function formatValueForReport(val, depth) {
                            depth = depth || 0;
                            if (val == null) return "";
                            
                            // 기본 타입 처리
                            if (typeof val === "string") return val;
                            if (typeof val === "number" || typeof val === "boolean") return String(val);
                            
                            // 들여쓰기 생성 (깊이 * 2 spaces - Markdown list indentation)
                            /* 
                               마크다운 중첩 리스트 규칙:
                               Level 1: - Item
                               Level 2:   - Sub Item (2 spaces)
                               Level 3:     - Sub Sub Item (4 spaces)
                            */
                            // 여기서는 재귀 호출 시 depth를 증가시키고, 호출하는 쪽에서 적절한 들여쓰기를 추가하도록 설계
                            
                            // 배열 처리
                            if (Array.isArray(val)) {
                                if (val.length === 0) return "(내용 없음)";
                                
                                // 단순 문자열 배열인 경우
                                if (val.every(item => typeof item === "string" || typeof item === "number")) {
                                    return val.join(", ");
                                }
                                
                                // 객체나 복잡한 배열인 경우
                                return val.map(function(item, i) {
                                    if (typeof item === "object" && item !== null) {
                                        // 객체 항목은 하위 항목으로 표시
                                        var subContent = formatValueForReport(item, depth + 1);
                                        // 하위 컨텐츠가 여러 줄이면 들여쓰기 적용
                                        if (subContent.includes("\\n")) {
                                            return "- " + subContent.replace(/\\n/g, "\\n  ");
                                        }
                                        return "- " + subContent;
                                    }
                                    return "- " + item;
                                }).join("\\n");
                            }
                            
                            // 객체 처리
                            if (typeof val === "object") {
                                var lines = [];
                                Object.keys(val).forEach(function(k) {
                                    var v = val[k];
                                    if (v == null) return;
                                    
                                    // 키 이름 포맷팅 (예: "market_size" -> "Market Size")
                                    var label = k;
                                    // 숫자_패턴 제거 (예: "1_executive_summary" -> "executive_summary")
                                    label = label.replace(/^\\d+_/, '');
                                    // 언더바를 공백으로 변환 및 첫 글자 대문자화
                                    label = label.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ');
                                    
                                    // 특수 키 이름 한국어 매핑
                                    if (k === "Evidence" || k === "근거") label = "근거";
                                    else if (k === "Interpretation" || k === "해석") label = "해석";
                                    else if (k === "Implication" || k === "시사점") label = "시사점";
                                    else if (k === "Insight" || k === "insight") label = "인사이트";
                                    
                                    // 값 포맷팅 - 재귀 호출
                                    var sub = formatValueForReport(v, depth + 1);
                                    
                                    // 값이 빈 문자열이면 스킵
                                    if (sub === "") return;
                                    
                                    // 하위 컨텐츠가 멀티라인이거나 리스트인 경우
                                    if (sub.includes("\\n") || sub.startsWith("- ")) {
                                        lines.push("**" + label + "**:\\n" + sub); // 줄바꿈 후 출력
                                    } else {
                                        lines.push("**" + label + "**: " + sub); // 같은 줄 출력
                                    }
                                });
                                return lines.join("\\n");
                            }
                            
                            return String(val);
                        }
                        
                        // 보고서에서 제외할 메타데이터/중복 키 (섹션으로 출력하지 않음)
                        var skipSectionKeys = ["target_keyword", "target_type", "executive_summary", "analysis_overview", "key_findings", "execution_roadmap", "appendix", "Executive Summary", "분석 개요", "Key Findings", "상세 분석", "전략적 시사점", "Strategic Implications", "실행 로드맵", "Execution Roadmap", "리스크 & 대응", "Risks & Responses", "Risks & Governance", "부록", "Appendix", "Detailed Analysis", "primary_insights", "quantitative_metrics", "key_insights", "Key Insights", "detailed_audience_analysis", "Audience Detailed Analysis", "오디언스 상세 분석", "insights", "forward_looking_recommendations", "integrated_analysis", "target_audience", "recommendations", "metrics"];
                        
                        // 모든 분석 유형에 키 매핑 적용 (키워드/오디언스/종합 공통)
                        analysisData = mapKeys(analysisData || {});
                        
                        // 오디언스 분석인 경우 특별한 포맷팅 (MECE 구조 지원)
                        if (targetType === "audience" && analysisData) {
                            
                            // Executive Summary (중복 제거) - 영문/한글 키 모두 지원
                            let executiveSummary = null;
                            if (analysisData.executive_summary) {
                                executiveSummary = analysisData.executive_summary;
                            } else if (analysisData.summary) {
                                executiveSummary = analysisData.summary;
                            } else if (analysisData["Executive Summary"]) {
                                executiveSummary = analysisData["Executive Summary"];
                            }
                            
                            // 객체인 경우 문자열로 변환 (.split 호출 전 필수)
                            if (executiveSummary != null && typeof executiveSummary !== "string") {
                                if (typeof executiveSummary === "object") {
                                    const t = executiveSummary.text || executiveSummary.content;
                                    executiveSummary = (t && typeof t === "string") ? t : JSON.stringify(executiveSummary, null, 2);
                                } else {
                                    executiveSummary = String(executiveSummary);
                                }
                            }
                            
                            // 중복된 내용 제거 (API 키 경고 메시지 등)
                            if (executiveSummary && typeof executiveSummary === "string") {
                                // 중복된 문장 제거
                                const lines = executiveSummary.split('\\n');
                                const uniqueLines = [];
                                const seen = new Set();
                                
                                lines.forEach(line => {
                                    const trimmed = line.trim();
                                    // API 키 경고 메시지 제거
                                    if (trimmed.includes('⚠️ AI API 키가 설정되지 않아') || 
                                        trimmed.includes('기본 분석 모드로 실행되었습니다') ||
                                        trimmed.includes('AI API를 설정하면')) {
                                        return; // 이 줄은 건너뛰기
                                    }
                                    // 중복 제거
                                    if (trimmed && !seen.has(trimmed)) {
                                        seen.add(trimmed);
                                        uniqueLines.push(line);
                                    }
                                });
                                
                                const cleanedSummary = uniqueLines.join('\\n').trim();
                                if (cleanedSummary) {
                                    resultText += "## Executive Summary\\n\\n" + (cleanedSummary) + "\\n\\n" ;
                                }
                            }
                            
                            // Key Findings 또는 Key Insights 처리 (영문/한글 키 모두 지원)
                            const keyFindings = analysisData.key_findings || 
                                               analysisData.key_insights || 
                                               analysisData["Key Insights"];
                            if (keyFindings) {
                                resultText += "## 주요 발견사항 (Key Findings)\\n\\n" ;
                                
                                // Key Insights가 배열인 경우 직접 처리
                                if (Array.isArray(keyFindings)) {
                                    keyFindings.forEach((insight, idx) => {
                                        if (typeof insight === "object") {
                                            resultText += "### " + (insight.insight || "인사이트 " + (idx + 1)) + "\\n\\n";
                                            if (insight.evidence) resultText += "- **근거**: " + insight.evidence + "\\n";
                                            if (insight.interpretation) resultText += "- **해석**: " + insight.interpretation + "\\n";
                                            if (insight.implication) resultText += "- **시사점**: " + insight.implication + "\\n";
                                            resultText += "\\n";
                                        } else {
                                            resultText += (idx + 1) + ". " + insight + "\\n";
                                        }
                                    });
                                    resultText += "\\n";
                                } else if (typeof keyFindings === "object") {
                                    // primary_insights가 배열인 경우
                                if (keyFindings.primary_insights && Array.isArray(keyFindings.primary_insights) && keyFindings.primary_insights.length > 0) {
                                    resultText += "### 핵심 인사이트\\n\\n" ;
                                    keyFindings.primary_insights.forEach((point, idx) => {
                                        // API 키 경고 메시지 제거
                                        if (!point.includes("⚠️ AI API 키가 설정되지 않아") && 
                                            !point.includes("기본 분석 모드") &&
                                            !point.includes("AI API를 설정하면")) {
                                            resultText += (idx + 1) + ". " + point + "\\n";
                                        }
                                    });
                                    resultText += "\\n" ;
                                }
                                // primary_insights가 문자열인 경우
                                else if (keyFindings.primary_insights && typeof keyFindings.primary_insights === "string") {
                                    resultText += "### 핵심 인사이트\\n\\n" + (keyFindings.primary_insights) + "\\n\\n" ;
                                }
                                
                                // quantitative_metrics
                                if (keyFindings.quantitative_metrics && typeof keyFindings.quantitative_metrics === "object") {
                                    resultText += "### 정량적 지표\\n\\n" ;
                                    const metrics = keyFindings.quantitative_metrics;
                                    // 모든 메트릭 필드를 동적으로 표시
                                    Object.keys(metrics).forEach(key => {
                                        const value = metrics[key];
                                        if (value && !value.toString().includes('AI API 필요')) {
                                            const labelMap = {
                                                'estimated_volume': '예상 규모',
                                                'engagement_level': '참여 수준',
                                                'growth_potential': '성장 잠재력',
                                                'market_value': '시장 가치',
                                                'accessibility': '접근 난이도'
                                            };
                                            const label = labelMap[key] || key;
                                            resultText += "- **" + (label) + "**: " + (value) + "\\n" ;
                                        }
                                    });
                                    resultText += "\\n" ;
                                }
                                
                                // keyFindings의 다른 필드들도 표시 (skipSectionKeys 제외, 객체는 formatValueForReport)
                                Object.keys(keyFindings).forEach(key => {
                                    if (skipSectionKeys.indexOf(key) >= 0 || !keyFindings[key]) return;
                                    resultText += "### " + (key) + "\\n\\n" ;
                                    if (Array.isArray(keyFindings[key])) {
                                        keyFindings[key].forEach((item, idx) => {
                                            resultText += (idx + 1) + ". " + (typeof item === "object" && item !== null ? formatValueForReport(item) : item) + "\\n" ;
                                        });
                                    } else if (typeof keyFindings[key] === "object") {
                                        resultText += formatValueForReport(keyFindings[key]) + "\\n" ;
                                    } else {
                                        resultText += (keyFindings[key]) + "\\n" ;
                                    }
                                    resultText += "\\n" ;
                                });
                                }
                            } else if (analysisData.key_points && Array.isArray(analysisData.key_points) && analysisData.key_points.length > 0) {
                                resultText += "## 주요 포인트\\n\\n" ;
                                analysisData.key_points.forEach((point, idx) => {
                                    // API 키 경고 메시지 제거
                                    if (!point.includes("⚠️ AI API 키가 설정되지 않아") && 
                                        !point.includes("기본 분석 모드") &&
                                        !point.includes("AI API를 설정하면")) {
                                        resultText += (idx + 1) + ". " + point + "\\n";
                                    }
                                });
                                resultText += "\\n" ;
                            }
                            
                            // Detailed Analysis (영문/한글 키 모두 지원)
                            const detailedAnalysis = analysisData.detailed_analysis || 
                                                     analysisData.detailed_audience_analysis || 
                                                     analysisData["Audience Detailed Analysis"] ||
                                                     analysisData["오디언스 상세 분석"];
                            const insights = detailedAnalysis?.insights || analysisData.insights;
                            
                            // detailed_analysis가 직접 객체인 경우
                            if (detailedAnalysis && typeof detailedAnalysis === "object") {
                                resultText += "## 상세 분석 (Detailed Analysis)\\n\\n" ;
                                
                                // insights가 있는 경우
                                if (insights) {
                                    if (insights.demographics) {
                                        resultText += "### 인구통계학적 특성\\n\\n" ;
                                        const demo = insights.demographics;
                                        if (typeof demo === "object") {
                                            if (demo.age_range) resultText += "- **연령대**: " + (demo.age_range) + "\\n" ;
                                            if (demo.gender) resultText += "- **성별**: " + (demo.gender) + "\\n" ;
                                            if (demo.location) resultText += "- **지역**: " + (demo.location) + "\\n" ;
                                            if (demo.income_level) resultText += "- **소득 수준**: " + (demo.income_level) + "\\n" ;
                                            if (demo.education_level) resultText += "- **교육 수준**: " + (demo.education_level) + "\\n" ;
                                            if (demo.family_status) resultText += "- **가족 구성**: " + (demo.family_status) + "\\n" ;
                                            if (demo.expected_occupations && Array.isArray(demo.expected_occupations) && demo.expected_occupations.length > 0) {
                                                resultText += "- **예상 직업**:\\n" ;
                                                demo.expected_occupations.forEach(occupation => {
                                                    resultText += "  - " + (occupation) + "\\n" ;
                                                });
                                            }
                                        } else {
                                            resultText += (demo) + "\\n" ;
                                        }
                                        resultText += "\\n" ;
                                    }
                                    
                                    if (insights.psychographics) {
                                        resultText += "### 심리적 특성\\n\\n" ;
                                        const psycho = insights.psychographics;
                                        if (typeof psycho === "object") {
                                            if (psycho.lifestyle) resultText += "- **라이프스타일**: " + (psycho.lifestyle) + "\\n" ;
                                            if (psycho.values) resultText += "- **가치관**: " + (psycho.values) + "\\n" ;
                                            if (psycho.interests) resultText += "- **관심사**: " + (psycho.interests) + "\\n" ;
                                            if (psycho.personality_traits) resultText += "- **성격 특성**: " + (psycho.personality_traits) + "\\n" ;
                                            if (psycho.aspirations) resultText += "- **열망 및 목표**: " + (psycho.aspirations) + "\\n" ;
                                            if (psycho.fears_concerns) resultText += "- **우려사항**: " + (psycho.fears_concerns) + "\\n" ;
                                        } else {
                                            resultText += (psycho) + "\\n" ;
                                        }
                                        resultText += "\\n" ;
                                    }
                                    
                                    if (insights.behavior) {
                                        resultText += "### 행동 패턴\\n\\n" ;
                                        const behavior = insights.behavior;
                                        if (typeof behavior === "object") {
                                            if (behavior.purchase_behavior) resultText += "- **구매 행동**: " + (behavior.purchase_behavior) + "\\n" ;
                                            if (behavior.media_consumption) resultText += "- **미디어 소비**: " + (behavior.media_consumption) + "\\n" ;
                                            if (behavior.online_activity) resultText += "- **온라인 활동**: " + (behavior.online_activity) + "\\n" ;
                                            if (behavior.brand_loyalty) resultText += "- **브랜드 충성도**: " + (behavior.brand_loyalty) + "\\n" ;
                                            if (behavior.decision_making) resultText += "- **의사결정 프로세스**: " + (behavior.decision_making) + "\\n" ;
                                        } else {
                                            resultText += (behavior) + "\\n" ;
                                        }
                                        resultText += "\\n" ;
                                    }
                                    
                                    if (insights.trends && Array.isArray(insights.trends) && insights.trends.length > 0) {
                                        resultText += "### 트렌드\\n\\n" ;
                                        insights.trends.forEach((trend, idx) => {
                                            resultText += (idx + 1) + ". " + (trend) + "\\n" ;
                                        });
                                        resultText += "\\n" ;
                                    }
                                    
                                    if (insights.opportunities && Array.isArray(insights.opportunities) && insights.opportunities.length > 0) {
                                        resultText += "### 기회\\n\\n" ;
                                        insights.opportunities.forEach((opp, idx) => {
                                            resultText += (idx + 1) + ". " + (opp) + "\\n" ;
                                        });
                                        resultText += "\\n" ;
                                    }
                                    
                                    if (insights.challenges && Array.isArray(insights.challenges) && insights.challenges.length > 0) {
                                        resultText += "### 도전 과제\\n\\n" ;
                                        insights.challenges.forEach((challenge, idx) => {
                                            resultText += (idx + 1) + ". " + (challenge) + "\\n" ;
                                        });
                                        resultText += "\\n" ;
                                    }
                                }
                                // insights가 없지만 detailed_analysis가 문자열인 경우
                                else if (typeof detailedAnalysis === "string") {
                                    resultText += detailedAnalysis + "\\n\\n" ;
                                }
                                // detailed_analysis가 객체이지만 insights가 없는 경우 (skipSectionKeys, formatValueForReport)
                                else if (typeof detailedAnalysis === "object") {
                                    Object.keys(detailedAnalysis).forEach(key => {
                                        if (skipSectionKeys.indexOf(key) >= 0 || !detailedAnalysis[key]) return;
                                        resultText += "### " + (key) + "\\n\\n" ;
                                        resultText += formatValueForReport(detailedAnalysis[key]) + "\\n\\n" ;
                                    });
                                }
                            }
                            // detailed_analysis가 없지만 insights가 직접 있는 경우
                            else if (insights && typeof insights === "object") {
                                resultText += "## 상세 분석 (Detailed Analysis)\\n\\n" ;
                                
                                if (insights.demographics) {
                                    resultText += "### 인구통계학적 특성\\n\\n" ;
                                    const demo = insights.demographics;
                                    if (typeof demo === "object") {
                                        Object.keys(demo).forEach(key => {
                                            if (demo[key]) {
                                                if (Array.isArray(demo[key])) {
                                                    resultText += "- **" + (key) + "**: " + (demo[key].join(', ')) + "\\n" ;
                                                } else {
                                                    resultText += "- **" + (key) + "**: " + (demo[key]) + "\\n" ;
                                                }
                                            }
                                        });
                                    } else {
                                        resultText += (demo) + "\\n" ;
                                    }
                                    resultText += "\\n" ;
                                }
                                
                                if (insights.psychographics) {
                                    resultText += "### 심리적 특성\\n\\n" ;
                                    const psycho = insights.psychographics;
                                    if (typeof psycho === "object") {
                                        Object.keys(psycho).forEach(key => {
                                            if (psycho[key]) {
                                                if (Array.isArray(psycho[key])) {
                                                    resultText += "- **" + (key) + "**: " + (psycho[key].join(', ')) + "\\n" ;
                                                } else {
                                                    resultText += "- **" + (key) + "**: " + (psycho[key]) + "\\n" ;
                                                }
                                            }
                                        });
                                    } else {
                                        resultText += (psycho) + "\\n" ;
                                    }
                                    resultText += "\\n" ;
                                }
                                
                                if (insights.behavior) {
                                    resultText += "### 행동 패턴\\n\\n" ;
                                    const behavior = insights.behavior;
                                    if (typeof behavior === "object") {
                                        Object.keys(behavior).forEach(key => {
                                            if (behavior[key]) {
                                                if (Array.isArray(behavior[key])) {
                                                    resultText += "- **" + (key) + "**: " + (behavior[key].join(', ')) + "\\n" ;
                                                } else {
                                                    resultText += "- **" + (key) + "**: " + (behavior[key]) + "\\n" ;
                                                }
                                            }
                                        });
                                    } else {
                                        resultText += (behavior) + "\\n" ;
                                    }
                                    resultText += "\\n" ;
                                }
                            }
                            
                            // Strategic Recommendations (영문/한글 키 모두 지원)
                            const strategicRecs = analysisData.strategic_recommendations || 
                                                  analysisData["Strategic Recommendations"] ||
                                                  analysisData["전략 제안"];
                            if (strategicRecs) {
                                resultText += "## 전략적 권장사항 (Strategic Recommendations)\\n\\n" ;
                                
                                const recs = strategicRecs;
                                
                                if (recs.immediate_actions && recs.immediate_actions.length > 0) {
                                    resultText += "### 즉시 실행 가능한 전략\\n\\n" ;
                                    recs.immediate_actions.forEach((action, idx) => {
                                        resultText += (idx + 1) + ". " + (action) + "\\n" ;
                                    });
                                    resultText += "\\n" ;
                                }
                                
                                if (recs.short_term_strategies && recs.short_term_strategies.length > 0) {
                                    resultText += "### 단기 전략 (3-6개월)\\n\\n" ;
                                    recs.short_term_strategies.forEach((strategy, idx) => {
                                        resultText += (idx + 1) + ". " + (strategy) + "\\n" ;
                                    });
                                    resultText += "\\n" ;
                                }
                                
                                if (recs.long_term_strategies && recs.long_term_strategies.length > 0) {
                                    resultText += "### 장기 전략 (6개월 이상)\\n\\n" ;
                                    recs.long_term_strategies.forEach((strategy, idx) => {
                                        resultText += (idx + 1) + ". " + (strategy) + "\\n" ;
                                    });
                                    resultText += "\\n" ;
                                }
                                
                                if (recs.success_metrics) {
                                    resultText += "### 성공 지표\\n\\n" + (recs.success_metrics) + "\\n\\n" ;
                                }
                                if (typeof recs === "object" && !Array.isArray(recs) && !recs.immediate_actions && !recs.short_term_strategies && !recs.long_term_strategies && !recs.success_metrics) {
                                    Object.keys(recs).forEach(function(k) {
                                        if (skipSectionKeys.indexOf(k) >= 0) return;
                                        var v = recs[k];
                                        if (v == null) return;
                                        resultText += "### " + k + "\\n\\n";
                                        resultText += formatValueForReport(v) + "\\n\\n";
                                    });
                                } else if (typeof recs === "object" && !Array.isArray(recs)) {
                                    Object.keys(recs).forEach(function(k) {
                                        if (["immediate_actions", "short_term_strategies", "long_term_strategies", "success_metrics"].indexOf(k) >= 0 || skipSectionKeys.indexOf(k) >= 0) return;
                                        var v = recs[k];
                                        if (v == null) return;
                                        resultText += "### " + k + "\\n\\n";
                                        resultText += formatValueForReport(v) + "\\n\\n";
                                    });
                                }
                            } else if (analysisData.recommendations && analysisData.recommendations.length > 0) {
                                resultText += "## 권장사항\\n\\n" ;
                                analysisData.recommendations.forEach((rec, idx) => {
                                    resultText += (idx + 1) + ". " + (rec) + "\\n" ;
                                });
                                resultText += "\\n" ;
                            }
                            
                            // Metrics (하위 호환성)
                            if (analysisData.metrics && !analysisData.key_findings) {
                                resultText += "## 지표\\n\\n" ;
                                const metrics = analysisData.metrics;
                                if (metrics.estimated_volume) resultText += "- **예상 규모**: " + (metrics.estimated_volume) + "\\n" ;
                                if (metrics.engagement_level) resultText += "- **참여 수준**: " + (metrics.engagement_level) + "\\n" ;
                                if (metrics.growth_potential) resultText += "- **성장 잠재력**: " + (metrics.growth_potential) + "\\n" ;
                                if (metrics.market_value) resultText += "- **시장 가치**: " + (metrics.market_value) + "\\n" ;
                                if (metrics.accessibility) resultText += "- **접근 난이도**: " + (metrics.accessibility) + "\\n" ;
                                resultText += "\\n" ;
                            }
                        } else if (targetType === "keyword" && analysisData) {
                            // 키워드 분석 상세 포맷팅 (MECE 구조 지원)
                            
                            // Executive Summary (문자열이 아닌 경우 변환)
                            let execSummary = analysisData.executive_summary || analysisData["Executive Summary"] || analysisData.summary;
                            if (execSummary != null && typeof execSummary !== "string") {
                                execSummary = (execSummary.text || execSummary.content) && typeof (execSummary.text || execSummary.content) === "string" 
                                    ? (execSummary.text || execSummary.content) : JSON.stringify(execSummary, null, 2);
                            }
                            if (execSummary && typeof execSummary === "string") {
                                resultText += "## Executive Summary\\n\\n" + (execSummary) + "\\n\\n" ;
                            }
                            
                            // Key Findings (배열 또는 객체 모두 지원)
                            const keyFindingsKw = analysisData.key_findings || analysisData["Key Findings"];
                            if (keyFindingsKw) {
                                resultText += "## 주요 발견사항 (Key Findings)\\n\\n" ;
                                
                                if (Array.isArray(keyFindingsKw) && keyFindingsKw.length > 0) {
                                    keyFindingsKw.forEach((item, idx) => {
                                        if (typeof item === "object") {
                                            const evidence = item.evidence || item["근거"];
                                            const interpretation = item.interpretation || item["해석"];
                                            const implication = item.implication || item["시사점"];
                                            const insight = item.insight || item["인사이트"];
                                            if (insight) resultText += "### " + (insight) + "\\n\\n" ;
                                            if (evidence) resultText += "- **근거**: " + (typeof evidence === "string" ? evidence : formatValueForReport(evidence)) + "\\n" ;
                                            if (interpretation) resultText += "- **해석**: " + (typeof interpretation === "string" ? interpretation : formatValueForReport(interpretation)) + "\\n" ;
                                            if (implication) resultText += "- **시사점**: " + (typeof implication === "string" ? implication : formatValueForReport(implication)) + "\\n" ;
                                            resultText += "\\n" ;
                                        } else {
                                            resultText += (idx + 1) + ". " + (item) + "\\n" ;
                                        }
                                    });
                                } else if (keyFindingsKw.primary_insights && Array.isArray(keyFindingsKw.primary_insights) && keyFindingsKw.primary_insights.length > 0) {
                                    resultText += "### 핵심 인사이트\\n\\n" ;
                                    keyFindingsKw.primary_insights.forEach((point, idx) => {
                                        resultText += (idx + 1) + ". " + (point) + "\\n" ;
                                    });
                                    resultText += "\\n" ;
                                }
                                
                                if (keyFindingsKw.quantitative_metrics && typeof keyFindingsKw.quantitative_metrics === "object") {
                                    resultText += "### 정량적 지표\\n\\n" ;
                                    const metrics = keyFindingsKw.quantitative_metrics;
                                    if (metrics.estimated_volume) resultText += "- **예상 검색량**: " + (metrics.estimated_volume) + "\\n" ;
                                    if (metrics.competition_level) resultText += "- **경쟁 수준**: " + (metrics.competition_level) + "\\n" ;
                                    if (metrics.growth_potential) resultText += "- **성장 잠재력**: " + (metrics.growth_potential) + "\\n" ;
                                    if (metrics.difficulty_score) resultText += "- **난이도 점수**: " + (metrics.difficulty_score) + "\\n" ;
                                    if (metrics.opportunity_score) resultText += "- **기회 점수**: " + (metrics.opportunity_score) + "\\n" ;
                                    resultText += "\\n" ;
                                }
                            } else if (analysisData.key_points && Array.isArray(analysisData.key_points) && analysisData.key_points.length > 0) {
                                resultText += "## 주요 포인트\\n\\n" ;
                                analysisData.key_points.forEach((point, idx) => {
                                    resultText += (idx + 1) + ". " + (point) + "\\n" ;
                                });
                                resultText += "\\n" ;
                            }
                            
                            // Detailed Analysis (상세 분석 객체 또는 insights)
                            const detailedAnalysisKw = analysisData.detailed_analysis || analysisData["상세 분석"] || analysisData;
                            const insights = detailedAnalysisKw.insights || analysisData.insights;
                            
                            if (insights) {
                                resultText += "## 상세 분석 (Detailed Analysis)\\n\\n" ;
                                
                                if (insights.search_intent) {
                                    resultText += "### 검색 의도 분석\\n\\n" ;
                                    const intent = insights.search_intent;
                                    if (intent.primary_intent) resultText += "- **주요 검색 의도**: " + (intent.primary_intent) + "\\n" ;
                                    if (intent.intent_breakdown) resultText += "- **의도별 분포**: " + (intent.intent_breakdown) + "\\n" ;
                                    if (intent.user_journey_stage) resultText += "- **사용자 여정 단계**: " + (intent.user_journey_stage) + "\\n" ;
                                    if (intent.search_context) resultText += "- **검색 맥락**: " + (intent.search_context) + "\\n" ;
                                    resultText += "\\n" ;
                                }
                                
                                if (insights.competition) {
                                    resultText += "### 경쟁 환경\\n\\n" ;
                                    const comp = insights.competition;
                                    if (comp.competition_level) resultText += "- **경쟁 수준**: " + (comp.competition_level) + "\\n" ;
                                    if (comp.top_competitors && comp.top_competitors.length > 0) {
                                        resultText += "- **주요 경쟁 페이지**:\\n" ;
                                        comp.top_competitors.forEach((competitor, idx) => {
                                            resultText += "  " + (idx + 1) + ". " + (competitor) + "\\n" ;
                                        });
                                    }
                                    if (comp.competitor_analysis) resultText += "- **경쟁자 분석**: " + (comp.competitor_analysis) + "\\n" ;
                                    if (comp.market_gap) resultText += "- **시장 공백**: " + (comp.market_gap) + "\\n" ;
                                    resultText += "\\n" ;
                                }
                                
                                if (insights.trends) {
                                    resultText += "### 검색 트렌드\\n\\n" ;
                                    const trends = insights.trends;
                                    if (trends.search_volume_trend) resultText += "- **검색량 트렌드**: " + (trends.search_volume_trend) + "\\n" ;
                                    if (trends.seasonal_patterns) resultText += "- **계절성 패턴**: " + (trends.seasonal_patterns) + "\\n" ;
                                    if (trends.trending_topics && Array.isArray(trends.trending_topics) && trends.trending_topics.length > 0) {
                                        resultText += "- **관련 트렌딩 토픽**:\\n" ;
                                        trends.trending_topics.forEach((topic, idx) => {
                                            resultText += "  " + (idx + 1) + ". " + (topic) + "\\n" ;
                                        });
                                    }
                                    if (trends.period_analysis) resultText += "- **기간별 분석**: " + (trends.period_analysis) + "\\n" ;
                                    if (trends.future_outlook) resultText += "- **향후 전망**: " + (trends.future_outlook) + "\\n" ;
                                    resultText += "\\n" ;
                                }
                                
                                if (insights.related_keywords) {
                                    resultText += "### 관련 키워드\\n\\n" ;
                                    const related = insights.related_keywords;
                                    if (related.semantic_keywords && Array.isArray(related.semantic_keywords) && related.semantic_keywords.length > 0) {
                                        resultText += "#### 의미적 관련 키워드\\n\\n" ;
                                        related.semantic_keywords.forEach((kw, idx) => {
                                            resultText += (idx + 1) + ". " + (kw) + "\\n" ;
                                        });
                                        resultText += "\\n" ;
                                    }
                                    if (related.long_tail_keywords && Array.isArray(related.long_tail_keywords) && related.long_tail_keywords.length > 0) {
                                        resultText += "#### 롱테일 키워드\\n\\n" ;
                                        related.long_tail_keywords.forEach((kw, idx) => {
                                            resultText += (idx + 1) + ". " + (kw) + "\\n" ;
                                        });
                                        resultText += "\\n" ;
                                    }
                                    if (related.question_keywords && Array.isArray(related.question_keywords) && related.question_keywords.length > 0) {
                                        resultText += "#### 질문형 키워드\\n\\n" ;
                                        related.question_keywords.forEach((kw, idx) => {
                                            resultText += (idx + 1) + ". " + (kw) + "\\n" ;
                                        });
                                        resultText += "\\n" ;
                                    }
                                    if (related.comparison_keywords && Array.isArray(related.comparison_keywords) && related.comparison_keywords.length > 0) {
                                        resultText += "#### 비교형 키워드\\n\\n" ;
                                        related.comparison_keywords.forEach((kw, idx) => {
                                            resultText += (idx + 1) + ". " + (kw) + "\\n" ;
                                        });
                                        resultText += "\\n" ;
                                    }
                                }
                                
                                if (insights.opportunities && Array.isArray(insights.opportunities) && insights.opportunities.length > 0) {
                                    resultText += "### SEO 기회\\n\\n" ;
                                    insights.opportunities.forEach((opp, idx) => {
                                        resultText += (idx + 1) + ". " + (opp) + "\\n" ;
                                    });
                                    resultText += "\\n" ;
                                }
                                
                                if (insights.challenges && Array.isArray(insights.challenges) && insights.challenges.length > 0) {
                                    resultText += "### SEO 도전 과제\\n\\n" ;
                                    insights.challenges.forEach((challenge, idx) => {
                                        resultText += (idx + 1) + ". " + (challenge) + "\\n" ;
                                    });
                                    resultText += "\\n" ;
                                }
                            } else if (detailedAnalysisKw && typeof detailedAnalysisKw === "object" && !Array.isArray(detailedAnalysisKw)) {
                                resultText += "## 상세 분석 (Detailed Analysis)\\n\\n" ;
                                Object.keys(detailedAnalysisKw).forEach(function(key) {
                                    if (key === "insights") return;
                                    if (skipSectionKeys.indexOf(key) >= 0) return;
                                    var val = detailedAnalysisKw[key];
                                    if (val == null) return;
                                    resultText += "### " + key + "\\n\\n";
                                    resultText += formatValueForReport(val) + "\\n\\n";
                                });
                            }
                            
                            // Strategic Recommendations (영문/한글 키 모두 지원)
                            const strategicRecsKw = analysisData.strategic_recommendations || 
                                                    analysisData["Strategic Recommendations"] ||
                                                    analysisData["전략 제안"] ||
                                                    analysisData["전략적 시사점"];
                            if (strategicRecsKw) {
                                resultText += "## 전략적 권장사항 (Strategic Recommendations)\\n\\n" ;
                                
                                const recsKw = strategicRecsKw;
                                
                                if (recsKw.immediate_actions && recsKw.immediate_actions.length > 0) {
                                    resultText += "### 즉시 실행 가능한 전략\\n\\n" ;
                                    recsKw.immediate_actions.forEach((action, idx) => {
                                        resultText += (idx + 1) + ". " + (action) + "\\n" ;
                                    });
                                    resultText += "\\n" ;
                                }
                                
                                if (recsKw.short_term_strategies && recsKw.short_term_strategies.length > 0) {
                                    resultText += "### 단기 전략 (3-6개월)\\n\\n" ;
                                    recsKw.short_term_strategies.forEach((strategy, idx) => {
                                        resultText += (idx + 1) + ". " + (strategy) + "\\n" ;
                                    });
                                    resultText += "\\n" ;
                                }
                                
                                if (recsKw.long_term_strategies && recsKw.long_term_strategies.length > 0) {
                                    resultText += "### 장기 전략 (6개월 이상)\\n\\n" ;
                                    recsKw.long_term_strategies.forEach((strategy, idx) => {
                                        resultText += (idx + 1) + ". " + (strategy) + "\\n" ;
                                    });
                                    resultText += "\\n" ;
                                }
                                
                                if (recsKw.success_metrics) {
                                    resultText += "### 성공 지표\\n\\n" + (recsKw.success_metrics) + "\\n\\n" ;
                                }
                                
                                if (typeof recsKw === "object" && !Array.isArray(recsKw) && !recsKw.immediate_actions && !recsKw.short_term_strategies && !recsKw.long_term_strategies && !recsKw.success_metrics) {
                                    Object.keys(recsKw).forEach(function(k) {
                                        if (skipSectionKeys.indexOf(k) >= 0) return;
                                        var v = recsKw[k];
                                        if (v == null) return;
                                        resultText += "### " + k + "\\n\\n";
                                        resultText += formatValueForReport(v) + "\\n\\n";
                                    });
                                }
                            } else if (analysisData.recommendations && analysisData.recommendations.length > 0) {
                                resultText += "## 키워드 최적화 전략\\n\\n" ;
                                analysisData.recommendations.forEach((rec, idx) => {
                                    resultText += (idx + 1) + ". " + (rec) + "\\n" ;
                                });
                                resultText += "\\n" ;
                            }
                            
                            // Metrics (하위 호환성)
                            if (analysisData.metrics && !analysisData.key_findings) {
                                resultText += "## 지표\\n\\n" ;
                                const metrics = analysisData.metrics;
                                if (metrics.estimated_volume) resultText += "- **예상 검색량**: " + (metrics.estimated_volume) + "\\n" ;
                                if (metrics.competition_level) resultText += "- **경쟁 수준**: " + (metrics.competition_level) + "\\n" ;
                                if (metrics.growth_potential) resultText += "- **성장 잠재력**: " + (metrics.growth_potential) + "\\n" ;
                                if (metrics.difficulty_score) resultText += "- **난이도 점수**: " + (metrics.difficulty_score) + "\\n" ;
                                if (metrics.opportunity_score) resultText += "- **기회 점수**: " + (metrics.opportunity_score) + "\\n" ;
                                resultText += "\\n" ;
                            }
                            
                            // 타겟 오디언스 정보 (키워드 분석의 경우)
                            if (analysisData.target_audience && analysisData.target_audience.expected_occupations) {
                                resultText += "## 예상 직업\\n\\n" ;
                                analysisData.target_audience.expected_occupations.forEach((occupation, idx) => {
                                    resultText += (idx + 1) + ". " + (occupation) + "\\n" ;
                                });
                                resultText += "\\n" ;
                            }
                            
                            // 실행 로드맵 (키워드 분석)
                            const roadmapKw = analysisData.execution_roadmap || analysisData["Execution Roadmap"] || analysisData["실행 로드맵"];
                            if (roadmapKw && typeof roadmapKw === "object") {
                                resultText += "## 실행 로드맵\\n\\n" ;
                                Object.keys(roadmapKw).forEach(function(k) {
                                    var v = roadmapKw[k];
                                    if (v == null) return;
                                    resultText += "### " + k + "\\n\\n";
                                    resultText += formatValueForReport(v) + "\\n\\n";
                                });
                            }
                            
                            // 리스크 & 대응 (키워드 분석)
                            const riskKw = analysisData.risk_governance || analysisData["Risks & Governance"] || analysisData["리스크 & 대응"];
                            if (riskKw && typeof riskKw === "object") {
                                resultText += "## 리스크 & 대응\\n\\n" ;
                                Object.keys(riskKw).forEach(function(k) {
                                    var v = riskKw[k];
                                    if (v == null) return;
                                    resultText += "### " + k + "\\n\\n";
                                    resultText += formatValueForReport(v) + "\\n\\n";
                                });
                            }
                            
                            // 부록 (키워드 분석)
                            const appendixKw = analysisData.appendix || analysisData["Appendix"] || analysisData["부록"];
                            if (appendixKw && typeof appendixKw === "object") {
                                resultText += "## 부록\\n\\n" ;
                                Object.keys(appendixKw).forEach(function(k) {
                                    var v = appendixKw[k];
                                    if (v == null) return;
                                    resultText += "### " + k + "\\n\\n";
                                    resultText += formatValueForReport(v) + "\\n\\n";
                                });
                            }
                        } else if (targetType === "comprehensive" && analysisData) {
                            // 종합 분석 상세 포맷팅 (키워드 + 오디언스 통합, 동일 문서 스타일)
                            
                            // Executive Summary (문자열 정규화·중복/API 메시지 제거)
                            let execSummaryComp = analysisData.executive_summary || analysisData["Executive Summary"] || analysisData.summary;
                            if (execSummaryComp != null && typeof execSummaryComp !== "string") {
                                if (typeof execSummaryComp === "object") {
                                    const t = execSummaryComp.text || execSummaryComp.content;
                                    execSummaryComp = (t && typeof t === "string") ? t : JSON.stringify(execSummaryComp, null, 2);
                                } else {
                                    execSummaryComp = String(execSummaryComp);
                                }
                            }
                            if (execSummaryComp && typeof execSummaryComp === "string") {
                                const lines = execSummaryComp.split("\\n");
                                const uniqueLines = [];
                                const seen = new Set();
                                lines.forEach(line => {
                                    const trimmed = line.trim();
                                    if (trimmed.includes("⚠️ AI API 키가 설정되지 않아") || trimmed.includes("기본 분석 모드") || trimmed.includes("AI API를 설정하면")) return;
                                    if (trimmed && !seen.has(trimmed)) { seen.add(trimmed); uniqueLines.push(line); }
                                });
                                const cleaned = uniqueLines.join("\\n").trim();
                                if (cleaned) resultText += "## Executive Summary\\n\\n" + cleaned + "\\n\\n";
                            }
                            
                            // Key Findings (배열·객체·primary_insights/quantitative_metrics 동일 스타일)
                            const keyFindingsComp = analysisData.key_findings || analysisData["Key Findings"];
                            if (keyFindingsComp) {
                                resultText += "## 주요 발견사항 (Key Findings)\\n\\n" ;
                                if (Array.isArray(keyFindingsComp) && keyFindingsComp.length > 0) {
                                    keyFindingsComp.forEach((item, idx) => {
                                        if (typeof item === "object" && item !== null) {
                                            const evidence = item.evidence || item["근거"];
                                            const interpretation = item.interpretation || item["해석"];
                                            const implication = item.implication || item["시사점"];
                                            const insight = item.insight || item["인사이트"];
                                            if (insight) resultText += "### " + (insight) + "\\n\\n" ;
                                            if (evidence) resultText += "- **근거**: " + (typeof evidence === "string" ? evidence : formatValueForReport(evidence)) + "\\n" ;
                                            if (interpretation) resultText += "- **해석**: " + (typeof interpretation === "string" ? interpretation : formatValueForReport(interpretation)) + "\\n" ;
                                            if (implication) resultText += "- **시사점**: " + (typeof implication === "string" ? implication : formatValueForReport(implication)) + "\\n" ;
                                            resultText += "\\n" ;
                                        } else {
                                            resultText += (idx + 1) + ". " + (item) + "\\n" ;
                                        }
                                    });
                                } else if (keyFindingsComp.primary_insights && Array.isArray(keyFindingsComp.primary_insights) && keyFindingsComp.primary_insights.length > 0) {
                                    resultText += "### 핵심 인사이트\\n\\n" ;
                                    keyFindingsComp.primary_insights.forEach((point, idx) => {
                                        resultText += (idx + 1) + ". " + (point) + "\\n" ;
                                    });
                                    resultText += "\\n" ;
                                }
                                if (keyFindingsComp.quantitative_metrics && typeof keyFindingsComp.quantitative_metrics === "object") {
                                    resultText += "### 정량적 지표\\n\\n" ;
                                    resultText += formatValueForReport(keyFindingsComp.quantitative_metrics) + "\\n\\n" ;
                                }
                                if (typeof keyFindingsComp === "object" && !Array.isArray(keyFindingsComp)) {
                                    Object.keys(keyFindingsComp).forEach(key => {
                                        if (skipSectionKeys.indexOf(key) >= 0 || !keyFindingsComp[key]) return;
                                        resultText += "### " + (key) + "\\n\\n" ;
                                        resultText += formatValueForReport(keyFindingsComp[key]) + "\\n\\n" ;
                                    });
                                }
                            } else if (analysisData.key_points && analysisData.key_points.length > 0) {
                                resultText += "## 주요 포인트\\n\\n" ;
                                analysisData.key_points.forEach((point, idx) => {
                                    resultText += (idx + 1) + ". " + (point) + "\\n" ;
                                });
                                resultText += "\\n" ;
                            }
                            
                            // Integrated Analysis (키워드 + 오디언스 통합)
                            const integrated = analysisData.integrated_analysis || analysisData.detailed_analysis || analysisData;
                            
                            if (integrated) {
                                resultText += "## 통합 분석 (Integrated Analysis)\\n\\n" ;
                                
                                // Keyword-Audience Alignment
                                if (integrated.keyword_audience_alignment) {
                                    resultText += "### 키워드-오디언스 정렬 분석\\n\\n" ;
                                    const align = integrated.keyword_audience_alignment;
                                    if (align.search_intent_match) resultText += "- **검색 의도-오디언스 매칭**: " + (align.search_intent_match) + "\\n" ;
                                    if (align.keyword_opportunity_for_audience) resultText += "- **오디언스 타겟팅 키워드 기회**: " + (align.keyword_opportunity_for_audience) + "\\n" ;
                                    if (align.audience_preferred_keywords) resultText += "- **오디언스 선호 키워드**: " + (align.audience_preferred_keywords) + "\\n" ;
                                    if (align.content_gap_analysis) resultText += "- **콘텐츠 공백 분석**: " + (align.content_gap_analysis) + "\\n" ;
                                    resultText += "\\n" ;
                                }
                                
                                // Core Keyword Insights
                                if (integrated.core_keyword_insights) {
                                    resultText += "### 핵심 키워드 인사이트\\n\\n" ;
                                    const kw = integrated.core_keyword_insights;
                                    if (kw.primary_search_intent) resultText += "- **주요 검색 의도**: " + (kw.primary_search_intent) + "\\n" ;
                                    if (kw.key_opportunity_keywords && Array.isArray(kw.key_opportunity_keywords)) {
                                        resultText += "#### 주요 기회 키워드\\n\\n" ;
                                        kw.key_opportunity_keywords.forEach((k, idx) => {
                                            resultText += (idx + 1) + ". " + (k) + "\\n" ;
                                        });
                                        resultText += "\\n" ;
                                    }
                                    if (kw.trending_keywords && Array.isArray(kw.trending_keywords)) {
                                        resultText += "#### 트렌딩 키워드\\n\\n" ;
                                        kw.trending_keywords.forEach((k, idx) => {
                                            resultText += (idx + 1) + ". " + (k) + "\\n" ;
                                        });
                                        resultText += "\\n" ;
                                    }
                                    if (kw.search_volume_trend) resultText += "- **검색량 트렌드**: " + (kw.search_volume_trend) + "\\n\\n" ;
                                }
                                
                                // Core Audience Insights
                                if (integrated.core_audience_insights) {
                                    resultText += "### 핵심 오디언스 인사이트\\n\\n" ;
                                    const aud = integrated.core_audience_insights;
                                    
                                    if (aud.target_demographics) {
                                        resultText += "#### 타겟 인구통계\\n\\n" ;
                                        const demo = aud.target_demographics;
                                        if (demo.age_range) resultText += "- **연령대**: " + (demo.age_range) + "\\n" ;
                                        if (demo.gender) resultText += "- **성별**: " + (demo.gender) + "\\n" ;
                                        if (demo.location) resultText += "- **지역**: " + (demo.location) + "\\n" ;
                                        if (demo.income_level) resultText += "- **소득 수준**: " + (demo.income_level) + "\\n" ;
                                        if (demo.expected_occupations && Array.isArray(demo.expected_occupations)) {
                                            resultText += "- **예상 직업군**: " + (demo.expected_occupations.join(', ')) + "\\n" ;
                                        }
                                        resultText += "\\n" ;
                                    }
                                    
                                    if (aud.key_behavior_patterns) {
                                        resultText += "#### 주요 행동 패턴\\n\\n" ;
                                        const beh = aud.key_behavior_patterns;
                                        if (beh.purchase_behavior) resultText += "- **구매 행동**: " + (beh.purchase_behavior) + "\\n" ;
                                        if (beh.media_consumption) resultText += "- **미디어 소비**: " + (beh.media_consumption) + "\\n" ;
                                        if (beh.online_activity) resultText += "- **온라인 활동**: " + (beh.online_activity) + "\\n" ;
                                        resultText += "\\n" ;
                                    }
                                    
                                    if (aud.core_values_and_needs) {
                                        resultText += "#### 핵심 가치 및 니즈\\n\\n" ;
                                        const val = aud.core_values_and_needs;
                                        if (val.primary_values && Array.isArray(val.primary_values)) {
                                            resultText += "- **주요 가치**: " + (val.primary_values.join(', ')) + "\\n" ;
                                        }
                                        if (val.main_pain_points && Array.isArray(val.main_pain_points)) {
                                            resultText += "- **주요 페인 포인트**: " + (val.main_pain_points.join(', ')) + "\\n" ;
                                        }
                                        if (val.key_aspirations && Array.isArray(val.key_aspirations)) {
                                            resultText += "- **핵심 열망**: " + (val.key_aspirations.join(', ')) + "\\n" ;
                                        }
                                        resultText += "\\n" ;
                                    }
                                }
                                
                                // Trends and Patterns
                                if (integrated.trends_and_patterns) {
                                    resultText += "### 트렌드 및 패턴\\n\\n" ;
                                    const trends = integrated.trends_and_patterns;
                                    if (trends.converging_trends && Array.isArray(trends.converging_trends)) {
                                        trends.converging_trends.forEach((trend, idx) => {
                                            resultText += (idx + 1) + ". " + (trend) + "\\n" ;
                                        });
                                        resultText += "\\n" ;
                                    }
                                    if (trends.period_analysis) resultText += "- **기간별 분석**: " + (trends.period_analysis) + "\\n" ;
                                    if (trends.future_outlook) resultText += "- **향후 전망**: " + (trends.future_outlook) + "\\n" ;
                                    resultText += "\\n" ;
                                }
                            }
                            
                            // Forward-Looking Recommendations
                            if (analysisData.forward_looking_recommendations) {
                                resultText += "## 앞으로의 제안 방향 (Forward-Looking Recommendations)\\n\\n" ;
                                const rec = analysisData.forward_looking_recommendations;
                                
                                if (rec.immediate_actions && Array.isArray(rec.immediate_actions)) {
                                    resultText += "### 즉시 실행 가능한 액션\\n\\n" ;
                                    rec.immediate_actions.forEach((action, idx) => {
                                        resultText += (idx + 1) + ". " + (action) + "\\n" ;
                                    });
                                    resultText += "\\n" ;
                                }
                                
                                if (rec.content_strategy) {
                                    resultText += "### 콘텐츠 전략\\n\\n" ;
                                    const cs = rec.content_strategy;
                                    if (cs.recommended_topics && Array.isArray(cs.recommended_topics)) {
                                        resultText += "#### 추천 주제\\n\\n" ;
                                        cs.recommended_topics.forEach((topic, idx) => {
                                            resultText += (idx + 1) + ". " + (topic) + "\\n" ;
                                        });
                                        resultText += "\\n" ;
                                    }
                                    if (cs.content_format) resultText += "- **콘텐츠 형식**: " + (cs.content_format) + "\\n" ;
                                    if (cs.distribution_channels && Array.isArray(cs.distribution_channels)) {
                                        resultText += "- **배포 채널**: " + (cs.distribution_channels.join(', ')) + "\\n" ;
                                    }
                                    resultText += "\\n" ;
                                }
                                
                                if (rec.marketing_strategy) {
                                    resultText += "### 마케팅 전략\\n\\n" ;
                                    const ms = rec.marketing_strategy;
                                    if (ms.keyword_targeting) resultText += "- **키워드 타겟팅**: " + (ms.keyword_targeting) + "\\n" ;
                                    if (ms.messaging_framework) resultText += "- **메시징 프레임워크**: " + (ms.messaging_framework) + "\\n" ;
                                    if (ms.channel_strategy) resultText += "- **채널 전략**: " + (ms.channel_strategy) + "\\n" ;
                                    resultText += "\\n" ;
                                }
                                
                                if (rec.short_term_goals && Array.isArray(rec.short_term_goals)) {
                                    resultText += "### 단기 목표 (3-6개월)\\n\\n" ;
                                    rec.short_term_goals.forEach((goal, idx) => {
                                        resultText += (idx + 1) + ". " + (goal) + "\\n" ;
                                    });
                                    resultText += "\\n" ;
                                }
                                
                                if (rec.long_term_vision && Array.isArray(rec.long_term_vision)) {
                                    resultText += "### 장기 비전 (6개월 이상)\\n\\n" ;
                                    rec.long_term_vision.forEach((vision, idx) => {
                                        resultText += (idx + 1) + ". " + (vision) + "\\n" ;
                                    });
                                    resultText += "\\n" ;
                                }
                                
                                if (rec.success_metrics) {
                                    resultText += "### 성공 지표\\n\\n" ;
                                    const sm = rec.success_metrics;
                                    if (sm.keyword_metrics) resultText += "- **키워드 지표**: " + (sm.keyword_metrics) + "\\n" ;
                                    if (sm.audience_metrics) resultText += "- **오디언스 지표**: " + (sm.audience_metrics) + "\\n" ;
                                    if (sm.integrated_kpis) resultText += "- **통합 KPI**: " + (sm.integrated_kpis) + "\\n" ;
                                    resultText += "\\n" ;
                                }
                            } else if (analysisData.strategic_recommendations) {
                                resultText += "## 전략적 제안\\n\\n" ;
                                const strat = analysisData.strategic_recommendations;
                                if (strat.content_differentiation && strat.content_differentiation.length > 0) {
                                    resultText += "### 콘텐츠 차별화 전략\\n\\n" ;
                                    strat.content_differentiation.forEach((strategy, idx) => {
                                        resultText += (idx + 1) + ". " + (strategy) + "\\n" ;
                                    });
                                    resultText += "\\n" ;
                                }
                                if (strat.pricing_strategy) {
                                    resultText += "### 가격 전략\\n\\n" + (strat.pricing_strategy) + "\\n\\n" ;
                                }
                                if (strat.partnership_opportunities) {
                                    resultText += "### 파트너십 기회\\n\\n" + (strat.partnership_opportunities) + "\\n\\n" ;
                                }
                            }
                            
                            if (analysisData.recommendations && analysisData.recommendations.length > 0) {
                                resultText += "## 경쟁 전략\\n\\n" ;
                                analysisData.recommendations.forEach((rec, idx) => {
                                    resultText += (idx + 1) + ". " + (rec) + "\\n" ;
                                });
                                resultText += "\\n" ;
                            }
                            
                            // Metrics (하위 호환성 - key_findings가 없을 때만)
                            if (analysisData.metrics && !analysisData.key_findings) {
                                resultText += "## 지표\\n\\n" ;
                                const metrics = analysisData.metrics;
                                if (metrics.competition_level) resultText += "- **경쟁 수준**: " + (metrics.competition_level) + "\\n" ;
                                if (metrics.market_opportunity) resultText += "- **시장 기회 크기**: " + (metrics.market_opportunity) + "\\n" ;
                                if (metrics.differentiation_potential) resultText += "- **차별화 가능성**: " + (metrics.differentiation_potential) + "\\n" ;
                                if (metrics.risk_level) resultText += "- **위험 수준**: " + (metrics.risk_level) + "\\n" ;
                                if (metrics.success_probability) resultText += "- **성공 확률**: " + (metrics.success_probability) + "\\n" ;
                                resultText += "\\n" ;
                            }
                        }
                        
                        // 추가 분석 데이터 표시 (sentiment, context, tone, recommendations, analysis_sources)
                        // analysisData와 data.data 모두에서 확인
                        const sentimentData = analysisData?.sentiment || data.data?.sentiment;
                        const contextData = analysisData?.context || data.data?.context;
                        const toneData = analysisData?.tone || data.data?.tone;
                        const recommendationsData = analysisData?.recommendations || data.data?.recommendations;
                        const analysisSources = analysisData?.analysis_sources || data.data?.analysis_sources;
                        
                        // Sentiment 분석
                        if (sentimentData && typeof sentimentData === "object") {
                            resultText += "## 감정 분석 (Sentiment Analysis)\\n\\n" ;
                            const sentiment = sentimentData;
                            if (sentiment.overall_sentiment) resultText += "- **전체 감정**: " + (sentiment.overall_sentiment) + "\\n" ;
                            if (sentiment.sentiment_score !== undefined && sentiment.sentiment_score !== null) {
                                resultText += "- **감정 점수**: " + (sentiment.sentiment_score) + "\\n" ;
                            }
                            if (sentiment.positive_aspects && Array.isArray(sentiment.positive_aspects) && sentiment.positive_aspects.length > 0) {
                                resultText += "- **긍정적 측면**:\\n" ;
                                sentiment.positive_aspects.forEach((aspect, idx) => {
                                    resultText += "  " + (idx + 1) + ". " + (aspect) + "\\n" ;
                                });
                            }
                            if (sentiment.negative_aspects && Array.isArray(sentiment.negative_aspects) && sentiment.negative_aspects.length > 0) {
                                resultText += "- **부정적 측면**:\\n" ;
                                sentiment.negative_aspects.forEach((aspect, idx) => {
                                    resultText += "  " + (idx + 1) + ". " + (aspect) + "\\n" ;
                                });
                            }
                            if (sentiment.emotional_tone) resultText += "- **감정적 톤**: " + (sentiment.emotional_tone) + "\\n" ;
                            // sentiment 객체의 다른 필드들도 동적으로 표시
                            Object.keys(sentiment).forEach(key => {
                                if (!['overall_sentiment', 'sentiment_score', 'positive_aspects', 'negative_aspects', 'emotional_tone'].includes(key) && sentiment[key]) {
                                    if (Array.isArray(sentiment[key])) {
                                        resultText += "- **" + (key) + "**: " + (sentiment[key].join(', ')) + "\\n" ;
                                    } else {
                                        resultText += "- **" + (key) + "**: " + (sentiment[key]) + "\\n" ;
                                    }
                                }
                            });
                            resultText += "\\n" ;
                        }
                        
                        // Context 분석
                        if (contextData && typeof contextData === "object") {
                            resultText += "## 맥락 분석 (Context Analysis)\\n\\n" ;
                            const context = contextData;
                            if (context.industry_context) resultText += "- **산업 맥락**: " + (context.industry_context) + "\\n" ;
                            if (context.market_context) resultText += "- **시장 맥락**: " + (context.market_context) + "\\n" ;
                            if (context.social_context) resultText += "- **사회적 맥락**: " + (context.social_context) + "\\n" ;
                            if (context.cultural_context) resultText += "- **문화적 맥락**: " + (context.cultural_context) + "\\n" ;
                            if (context.temporal_context) resultText += "- **시대적 맥락**: " + (context.temporal_context) + "\\n" ;
                            if (context.related_events && Array.isArray(context.related_events) && context.related_events.length > 0) {
                                resultText += "- **관련 이벤트**:\\n" ;
                                context.related_events.forEach((event, idx) => {
                                    resultText += "  " + (idx + 1) + ". " + (event) + "\\n" ;
                                });
                            }
                            // context 객체의 다른 필드들도 동적으로 표시 (동일 문서 스타일)
                            Object.keys(context).forEach(key => {
                                if (!['industry_context', 'market_context', 'social_context', 'cultural_context', 'temporal_context', 'related_events'].includes(key) && context[key]) {
                                    resultText += "- **" + (key) + "**: " + (typeof context[key] === "object" ? formatValueForReport(context[key]) : context[key]) + "\\n" ;
                                }
                            });
                            resultText += "\\n" ;
                        }
                        
                        // Tone 분석
                        if (toneData && typeof toneData === "object") {
                            resultText += "## 톤 분석 (Tone Analysis)\\n\\n" ;
                            const tone = toneData;
                            if (tone.overall_tone) resultText += "- **전체 톤**: " + (tone.overall_tone) + "\\n" ;
                            if (tone.communication_style) resultText += "- **커뮤니케이션 스타일**: " + (tone.communication_style) + "\\n" ;
                            if (tone.formality_level) resultText += "- **격식 수준**: " + (tone.formality_level) + "\\n" ;
                            if (tone.energy_level) resultText += "- **에너지 수준**: " + (tone.energy_level) + "\\n" ;
                            if (tone.recommended_tone && Array.isArray(tone.recommended_tone) && tone.recommended_tone.length > 0) {
                                resultText += "- **권장 톤**:\\n" ;
                                tone.recommended_tone.forEach((rec, idx) => {
                                    resultText += "  " + (idx + 1) + ". " + (rec) + "\\n" ;
                                });
                            }
                            // tone 객체의 다른 필드들도 동적으로 표시
                            Object.keys(tone).forEach(key => {
                                if (!['overall_tone', 'communication_style', 'formality_level', 'energy_level', 'recommended_tone'].includes(key) && tone[key]) {
                                    if (Array.isArray(tone[key])) {
                                        resultText += "- **" + (key) + "**: " + (tone[key].join(', ')) + "\\n" ;
                                    } else {
                                        resultText += "- **" + (key) + "**: " + (tone[key]) + "\\n" ;
                                    }
                                }
                            });
                            resultText += "\\n" ;
                        }
                        
                        // Recommendations (키워드 추천 등) - strategic_recommendations와 중복되지 않도록 확인
                        if (recommendationsData && !analysisData?.strategic_recommendations) {
                            if (typeof recommendationsData === "object" && !Array.isArray(recommendationsData)) {
                                resultText += "## 키워드 추천 (Keyword Recommendations)\\n\\n" ;
                                const recs = recommendationsData;
                                
                                if (recs.semantic_keywords && Array.isArray(recs.semantic_keywords) && recs.semantic_keywords.length > 0) {
                                    resultText += "### 의미적 관련 키워드\\n\\n" ;
                                    recs.semantic_keywords.forEach((kw, idx) => {
                                        const keyword = typeof kw === "string" ? kw : (kw.keyword || kw);
                                        const score = kw.score ? ' (점수: ' + kw.score + ')' : '';
                                        resultText += (idx + 1) + '. ' + keyword + score + '\\n';
                                    });
                                    resultText += "\\n";
                                }
                                
                                if (recs.co_occurring_keywords && Array.isArray(recs.co_occurring_keywords) && recs.co_occurring_keywords.length > 0) {
                                    resultText += "### 공기 키워드\\n\\n";
                                    recs.co_occurring_keywords.forEach((kw, idx) => {
                                        const keyword = typeof kw === "string" ? kw : (kw.keyword || kw);
                                        resultText += (idx + 1) + '. ' + keyword + '\\n';
                                    });
                                    resultText += "\\n";
                                }
                                
                                if (recs.long_tail_keywords && Array.isArray(recs.long_tail_keywords) && recs.long_tail_keywords.length > 0) {
                                    resultText += "### 롱테일 키워드\\n\\n";
                                    recs.long_tail_keywords.forEach((kw, idx) => {
                                        const keyword = typeof kw === "string" ? kw : (kw.keyword || kw);
                                        resultText += (idx + 1) + '. ' + keyword + '\\n';
                                    });
                                    resultText += "\\n";
                                }
                                
                                if (recs.trending_keywords && Array.isArray(recs.trending_keywords) && recs.trending_keywords.length > 0) {
                                    resultText += "### 트렌딩 키워드\\n\\n";
                                    recs.trending_keywords.forEach((kw, idx) => {
                                        const keyword = typeof kw === "string" ? kw : (kw.keyword || kw);
                                        resultText += (idx + 1) + '. ' + keyword + '\\n';
                                    });
                                    resultText += "\\n";
                                }
                                
                                // recommendations 객체의 다른 필드들도 동적으로 표시
                                Object.keys(recs).forEach(key => {
                                    if (!['semantic_keywords', 'co_occurring_keywords', 'long_tail_keywords', 'trending_keywords'].includes(key) && recs[key]) {
                                        if (Array.isArray(recs[key]) && recs[key].length > 0) {
                                            resultText += "### " + key + "\\n\\n";
                                            recs[key].forEach((item, idx) => {
                                                const keyword = typeof item === "string" ? item : (item.keyword || item);
                                                resultText += (idx + 1) + '. ' + keyword + '\\n';
                                            });
                                            resultText += "\\n";
                                        }
                                    }
                                });
                            } else if (Array.isArray(recommendationsData) && recommendationsData.length > 0) {
                                resultText += "## 키워드 추천\\n\\n" ;
                                recommendationsData.forEach((rec, idx) => {
                                    const keyword = typeof rec === "string" ? rec : (rec.keyword || rec);
                                    resultText += (idx + 1) + ". " + (keyword) + "\\n" ;
                                });
                                resultText += "\\n" ;
                            }
                        }
                        
                        // Analysis Sources
                        if (analysisSources && Array.isArray(analysisSources) && analysisSources.length > 0) {
                            resultText += "## 📚 분석 출처 (Analysis Sources)\\n\\n" ;
                            analysisSources.forEach((source, idx) => {
                                resultText += (idx + 1) + ". " + (source) + "\\n" ;
                            });
                            resultText += "\\n" ;
                        }
                        
                        // 영문/한글 키가 있는 경우 직접 처리 (오디언스 분석)
                        if (targetType === "audience" && analysisData && !resultText.includes("Executive Summary") && !resultText.includes("주요 발견사항")) {
                            // 영문/한글 키로 직접 데이터 표시
                            if (analysisData["Executive Summary"]) {
                                resultText += "## Executive Summary\\n\\n" + (analysisData["Executive Summary"]) + "\\n\\n";
                            }
                            if (analysisData["Analysis Overview"]) {
                                resultText += "## Analysis Overview\\n\\n";
                                const overview = analysisData["Analysis Overview"];
                                if (typeof overview === "object") {
                                    Object.keys(overview).forEach(key => {
                                        if (skipSectionKeys.indexOf(key) >= 0 || !overview[key]) return;
                                        resultText += "### " + key + "\\n\\n";
                                        resultText += formatValueForReport(overview[key]) + "\\n\\n";
                                    });
                                } else {
                                    resultText += overview + "\\n\\n";
                                }
                            }
                            if (analysisData["분석 개요"]) {
                                resultText += "## 분석 개요\\n\\n";
                                const overview = analysisData["분석 개요"];
                                if (typeof overview === "object") {
                                    Object.keys(overview).forEach(key => {
                                        if (skipSectionKeys.indexOf(key) >= 0 || !overview[key]) return;
                                        resultText += "### " + key + "\\n\\n";
                                        resultText += formatValueForReport(overview[key]) + "\\n\\n";
                                    });
                                } else {
                                    resultText += overview + "\\n\\n";
                                }
                            }
                            if (analysisData["Key Insights"]) {
                                resultText += "## Key Insights\\n\\n";
                                const insights = analysisData["Key Insights"];
                                if (Array.isArray(insights)) {
                                    insights.forEach((insight, idx) => {
                                        if (typeof insight === "object") {
                                            resultText += "### " + (insight.insight || "인사이트 " + (idx + 1)) + "\\n\\n";
                                            if (insight.evidence) resultText += "- **근거**: " + insight.evidence + "\\n";
                                            if (insight.interpretation) resultText += "- **해석**: " + insight.interpretation + "\\n";
                                            if (insight.implication) resultText += "- **시사점**: " + insight.implication + "\\n";
                                            resultText += "\\n";
                                        } else {
                                            resultText += (idx + 1) + ". " + insight + "\\n";
                                        }
                                    });
                                    resultText += "\\n";
                                } else if (typeof insights === "object") {
                                    Object.keys(insights).forEach(key => {
                                        if (skipSectionKeys.indexOf(key) >= 0 || insights[key] == null) return;
                                        resultText += "### " + key + "\\n\\n";
                                        resultText += formatValueForReport(insights[key]) + "\\n\\n";
                                    });
                                } else {
                                    resultText += insights + "\\n\\n";
                                }
                            }
                            if (analysisData["Audience Detailed Analysis"]) {
                                resultText += "## Audience Detailed Analysis\\n\\n";
                                const detailed = analysisData["Audience Detailed Analysis"];
                                if (typeof detailed === "object" && !Array.isArray(detailed)) {
                                    Object.keys(detailed).forEach(key => {
                                        if (skipSectionKeys.indexOf(key) >= 0 || !detailed[key]) return;
                                        resultText += "### " + key + "\\n\\n";
                                        resultText += formatValueForReport(detailed[key]) + "\\n\\n";
                                    });
                                } else {
                                    resultText += (typeof detailed === "string" ? detailed : formatValueForReport(detailed)) + "\\n\\n";
                                }
                            }
                            if (analysisData["오디언스 상세 분석"]) {
                                resultText += "## 오디언스 상세 분석\\n\\n";
                                const detailed = analysisData["오디언스 상세 분석"];
                                if (typeof detailed === "object" && !Array.isArray(detailed)) {
                                    Object.keys(detailed).forEach(key => {
                                        if (skipSectionKeys.indexOf(key) >= 0 || !detailed[key]) return;
                                        resultText += "### " + key + "\\n\\n";
                                        resultText += formatValueForReport(detailed[key]) + "\\n\\n";
                                    });
                                } else {
                                    resultText += (typeof detailed === "string" ? detailed : formatValueForReport(detailed)) + "\\n\\n";
                                }
                            }
                            if (analysisData["Strategic Recommendations"]) {
                                resultText += "## Strategic Recommendations\\n\\n";
                                const strategy = analysisData["Strategic Recommendations"];
                                if (typeof strategy === "object" && !Array.isArray(strategy)) {
                                    Object.keys(strategy).forEach(key => {
                                        if (skipSectionKeys.indexOf(key) >= 0 || strategy[key] == null) return;
                                        resultText += "### " + key + "\\n\\n";
                                        resultText += formatValueForReport(strategy[key]) + "\\n\\n";
                                    });
                                } else {
                                    resultText += (typeof strategy === "string" ? strategy : formatValueForReport(strategy)) + "\\n\\n";
                                }
                            }
                            if (analysisData["전략 제안"]) {
                                resultText += "## 전략 제안\\n\\n";
                                const strategy = analysisData["전략 제안"];
                                if (typeof strategy === "object" && !Array.isArray(strategy)) {
                                    Object.keys(strategy).forEach(key => {
                                        if (skipSectionKeys.indexOf(key) >= 0 || strategy[key] == null) return;
                                        resultText += "### " + key + "\\n\\n";
                                        resultText += formatValueForReport(strategy[key]) + "\\n\\n";
                                    });
                                } else {
                                    resultText += (typeof strategy === "string" ? strategy : formatValueForReport(strategy)) + "\\n\\n";
                                }
                            }
                            if (analysisData["Execution Roadmap"]) {
                                resultText += "## Execution Roadmap\\n\\n";
                                const roadmap = analysisData["Execution Roadmap"];
                                if (typeof roadmap === "object" && !Array.isArray(roadmap)) {
                                    Object.keys(roadmap).forEach(key => {
                                        if (skipSectionKeys.indexOf(key) >= 0 || roadmap[key] == null) return;
                                        resultText += "### " + key + "\\n\\n";
                                        resultText += formatValueForReport(roadmap[key]) + "\\n\\n";
                                    });
                                } else {
                                    resultText += (typeof roadmap === "string" ? roadmap : formatValueForReport(roadmap)) + "\\n\\n";
                                }
                            }
                            if (analysisData["실행 로드맵"]) {
                                resultText += "## 실행 로드맵\\n\\n";
                                const roadmap = analysisData["실행 로드맵"];
                                if (typeof roadmap === "object" && !Array.isArray(roadmap)) {
                                    Object.keys(roadmap).forEach(key => {
                                        if (skipSectionKeys.indexOf(key) >= 0 || roadmap[key] == null) return;
                                        resultText += "### " + key + "\\n\\n";
                                        resultText += formatValueForReport(roadmap[key]) + "\\n\\n";
                                    });
                                } else {
                                    resultText += (typeof roadmap === "string" ? roadmap : formatValueForReport(roadmap)) + "\\n\\n";
                                }
                            }
                            if (analysisData["Risks & Governance"]) {
                                resultText += "## Risks & Governance\\n\\n";
                                const risk = analysisData["Risks & Governance"];
                                if (typeof risk === "object" && !Array.isArray(risk)) {
                                    Object.keys(risk).forEach(key => {
                                        if (skipSectionKeys.indexOf(key) >= 0 || risk[key] == null) return;
                                        resultText += "### " + key + "\\n\\n";
                                        resultText += formatValueForReport(risk[key]) + "\\n\\n";
                                    });
                                } else {
                                    resultText += (typeof risk === "string" ? risk : formatValueForReport(risk)) + "\\n\\n";
                                }
                            }
                            if (analysisData["리스크 & 거버넌스"]) {
                                resultText += "## 리스크 & 거버넌스\\n\\n";
                                const risk = analysisData["리스크 & 거버넌스"];
                                if (typeof risk === "object" && !Array.isArray(risk)) {
                                    Object.keys(risk).forEach(key => {
                                        if (skipSectionKeys.indexOf(key) >= 0 || risk[key] == null) return;
                                        resultText += "### " + key + "\\n\\n";
                                        resultText += formatValueForReport(risk[key]) + "\\n\\n";
                                    });
                                } else {
                                    resultText += (typeof risk === "string" ? risk : formatValueForReport(risk)) + "\\n\\n";
                                }
                            }
                            if (analysisData["Appendix"]) {
                                resultText += "## Appendix\\n\\n";
                                const appendix = analysisData["Appendix"];
                                if (typeof appendix === "object" && !Array.isArray(appendix)) {
                                    Object.keys(appendix).forEach(key => {
                                        if (skipSectionKeys.indexOf(key) >= 0 || appendix[key] == null) return;
                                        resultText += "### " + key + "\\n\\n";
                                        resultText += formatValueForReport(appendix[key]) + "\\n\\n";
                                    });
                                } else {
                                    resultText += (typeof appendix === "string" ? appendix : formatValueForReport(appendix)) + "\\n\\n";
                                }
                            }
                            if (analysisData["부록"]) {
                                resultText += "## 부록\\n\\n";
                                const appendix = analysisData["부록"];
                                if (typeof appendix === "object" && !Array.isArray(appendix)) {
                                    Object.keys(appendix).forEach(key => {
                                        if (skipSectionKeys.indexOf(key) >= 0 || appendix[key] == null) return;
                                        resultText += "### " + key + "\\n\\n";
                                        resultText += formatValueForReport(appendix[key]) + "\\n\\n";
                                    });
                                } else {
                                    resultText += (typeof appendix === "string" ? appendix : formatValueForReport(appendix)) + "\\n\\n";
                                }
                            }
                        }
                        
                        // 결과가 비어있는 경우 처리
                        const baseReportText = "# 타겟 분석 보고서\\n\\n**분석 대상**: " + targetKeyword + "\\n**분석 유형**: " + (typeNames[targetType] || targetType) + " 분석\\n**분석 기간**: " + formData.start_date + " ~ " + formData.end_date + "\\n**분석 일시**: " + new Date().toLocaleString("ko-KR") + "\\n\\n---\\n\\n";
                        const currentText = resultText.trim();
                        const baseText = baseReportText.trim();
                        
                        // 결과가 기본 헤더만 있는지 확인 (영문/한글 키 처리 후에는 더 이상 체크하지 않음)
                        const hasEnglishKeys = analysisData["Executive Summary"] || 
                                              analysisData["Analysis Overview"] || 
                                              analysisData["Key Insights"] ||
                                              analysisData["Audience Detailed Analysis"] ||
                                              analysisData["Strategic Recommendations"] ||
                                              analysisData["Execution Roadmap"] ||
                                              analysisData["Risks & Governance"] ||
                                              analysisData["Appendix"];
                        const hasKoreanKeys = analysisData["분석 개요"] || 
                                             analysisData["오디언스 상세 분석"] ||
                                             analysisData["전략 제안"] ||
                                             analysisData["실행 로드맵"] ||
                                             analysisData["리스크 & 거버넌스"] ||
                                             analysisData["부록"];
                        if (!resultText || ((currentText === baseText || currentText.length <= baseText.length + 50) && !hasEnglishKeys && !hasKoreanKeys)) {
                            resultText += "## ⚠️ 분석 결과 없음\\n\\n" ;
                            resultText += "분석 데이터를 받지 못했습니다.\\n\\n" ;
                            resultText += "**디버깅 정보**:\\n" ;
                            resultText += "- 받은 데이터 타입: " + (typeof data.data) + "\\n" ;
                            resultText += "- analysisData 타입: " + (typeof analysisData) + "\\n" ;
                            resultText += "- analysisData 키: " + Object.keys(analysisData || {}).join(', ') + "\\n" ;
                            resultText += "- data.data 키: " + Object.keys(data.data || {}).join(', ') + "\\n\\n" ;
                            resultText += "**전체 응답 구조**:\\n" ;
                            resultText += "```json\\n" + JSON.stringify({success: data.success, dataKeys: Object.keys(data.data || {}), analysisDataKeys: Object.keys(analysisData || {})}, null, 2) + "\\n```\\n\\n";
                            resultText += "**해결 방법**:\\n" ;
                            resultText += "1. AI API 키가 설정되어 있는지 확인하세요 (OpenAI 또는 Gemini)\\n" ;
                            resultText += "2. 서버 로그를 확인하세요\\n" ;
                            resultText += "3. 브라우저 콘솔에서 상세한 오류 메시지를 확인하세요\\n\\n" ;
                        }
                        
                        resultText += "---\\n\\n" ;
                        resultText += "*본 보고서는 AI 기반 분석 결과입니다.*\\n" ;
                        
                        resultContent.innerHTML = markdownToReportHtml(resultText);
                        resultSection.classList.add("show");
                        emptyState.style.display = "none";
                    } else if (data && !data.success) {
                        // 에러가 있는 경우 에러 메시지 표시
                        throw new Error(data.error || "분석 결과를 받지 못했습니다.");
                    } else if (!data) {
                        // data가 null인 경우
                        throw new Error("분석 결과를 받지 못했습니다. 서버 상태를 확인해주세요.");
                    }
                } catch (err) {
                    console.error("분석 요청 오류:", err);
                    error.textContent = "오류: " + (err.message || "알 수 없는 오류가 발생했습니다.");
                    error.classList.add("show");
                    emptyState.style.display = "none";
                    resultSection.classList.remove("show");
                    
                    // 진행률 표시 숨기기
                    if (progressContainer) {
                        progressContainer.style.display = "none";
                    }
                } finally {
                    loading.classList.remove("show");
                    analyzeBtn.disabled = false;
                    
                    // 진행률 인터벌 정리 (혹시 남아있을 수 있음)
                    if (typeof progressInterval !== 'undefined' && progressInterval !== null) {
                        clearInterval(progressInterval);
                        progressInterval = null;
                    }
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# 헬스 체크는 monitoring 라우터로 이동 (더 상세한 정보 제공)

@app.get("/robots.txt", response_class=HTMLResponse)
async def robots_txt():
    """robots.txt 파일 제공"""
    robots_content = """# robots.txt for News Trend Analyzer
User-agent: *
Allow: /
Disallow: /api/
Disallow: /docs
Disallow: /openapi.json

# Sitemap
Sitemap: https://news-trend-analyzer.vercel.app/sitemap.xml
"""
    from fastapi.responses import PlainTextResponse
    return PlainTextResponse(content=robots_content, media_type="text/plain")

@app.get("/sitemap.xml", response_class=HTMLResponse)
async def sitemap_xml():
    """sitemap.xml 파일 제공"""
    from datetime import datetime
    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9
        http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd">
  
  <!-- Homepage -->
  <url>
    <loc>https://news-trend-analyzer.vercel.app/</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>
  
  <!-- Dashboard (if accessible) -->
  <url>
    <loc>https://news-trend-analyzer.vercel.app/app</loc>
    <lastmod>{datetime.now().strftime('%Y-%m-%d')}</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
  
</urlset>
"""
    from fastapi.responses import Response
    return Response(content=sitemap_content, media_type="application/xml")

# 정적 파일 서빙 (Vercel 환경에서는 건너뛰기)
if not IS_VERCEL:
    try:
        # 정적 파일 서빙 (워드 클라우드 이미지)
        if ASSETS_DIR.exists():
            app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")
    except Exception as e:
        logger.warning(f"정적 파일 마운트 실패: {e}")
    
    # 프론트엔드 정적 파일 서빙 (빌드된 파일이 있는 경우에만)
    # 프론트엔드는 /app 경로로 마운트하여 루트 경로와 충돌 방지
    try:
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
    except Exception as e:
        logger.warning(f"프론트엔드 마운트 실패: {e}")
else:
    logger.info("Vercel 환경: 정적 파일 마운트를 건너뜁니다.")


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    try:
        logger.info("뉴스 트렌드 분석 서비스 시작")
        logger.info(f"서버 설정: {settings.HOST}:{settings.PORT}")
        logger.info(f"디버그 모드: {settings.DEBUG}")
        
        # API 키 상태 로깅 (Vercel 배포 시 확인용)
        import os
        is_vercel = os.getenv("VERCEL") == "1"
        logger.info("=" * 60)
        logger.info("환경 변수 로딩 상태 확인")
        logger.info(f"환경: {'Vercel (배포)' if is_vercel else '로컬 개발'}")
        logger.info(f"OPENAI_API_KEY: {'✅ 설정됨' if settings.OPENAI_API_KEY else '❌ 미설정'}")
        if settings.OPENAI_API_KEY:
            logger.info(f"  - 길이: {len(settings.OPENAI_API_KEY)} 문자")
            logger.info(f"  - 시작: {settings.OPENAI_API_KEY[:10]}...")
        logger.info(f"GEMINI_API_KEY: {'✅ 설정됨' if settings.GEMINI_API_KEY else '❌ 미설정'}")
        if settings.GEMINI_API_KEY:
            logger.info(f"  - 길이: {len(settings.GEMINI_API_KEY)} 문자")
            logger.info(f"  - 시작: {settings.GEMINI_API_KEY[:10]}...")
        logger.info(f"OPENAI_MODEL: {settings.OPENAI_MODEL}")
        logger.info(f"GEMINI_MODEL: {settings.GEMINI_MODEL}")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"Startup event error: {e}", exc_info=True)
        # 에러가 발생해도 앱은 계속 실행되도록 함


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
