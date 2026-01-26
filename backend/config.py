"""
설정 관리 모듈
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """애플리케이션 설정"""
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # 뉴스 API 설정 (선택사항)
    NEWS_API_KEY: Optional[str] = None
    NAVER_CLIENT_ID: Optional[str] = None
    NAVER_CLIENT_SECRET: Optional[str] = None
    
    # AI API 설정 (타겟 분석용)
    # Vercel 환경에서는 os.getenv()로 직접 읽도록 fallback 처리
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"  # 최신 모델 사용
    
    def __init__(self, **kwargs):
        """환경 변수를 직접 읽어서 설정 (Vercel 호환성)"""
        super().__init__(**kwargs)
        
        # Vercel 환경에서는 os.getenv()로 직접 읽기 (우선순위 높음)
        # 환경 변수가 설정되어 있으면 그것을 사용
        if os.getenv("OPENAI_API_KEY"):
            self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        if os.getenv("GEMINI_API_KEY"):
            self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        if os.getenv("OPENAI_MODEL"):
            self.OPENAI_MODEL = os.getenv("OPENAI_MODEL")
        if os.getenv("GEMINI_MODEL"):
            self.GEMINI_MODEL = os.getenv("GEMINI_MODEL")
    
    # 크롤링 설정
    CRAWL_DELAY: float = 1.0  # 초 단위
    MAX_ARTICLES_PER_KEYWORD: int = 100
    MAX_ARTICLES_TOTAL: int = 500
    
    # NLP 설정
    NLP_MODEL: str = "jhgan/ko-sroberta-multitask"
    STOPWORDS_PATH: str = "./data/stopwords.txt"
    USE_EMBEDDING: bool = True
    
    # 워드 클라우드 설정
    WORDCLOUD_WIDTH: int = 800
    WORDCLOUD_HEIGHT: int = 600
    WORDCLOUD_BACKGROUND_COLOR: str = "white"
    WORDCLOUD_MAX_WORDS: int = 100
    
    # 데이터 저장 설정
    DATA_DIR: str = "./data"
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # 초 단위
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None  # None이면 파일 로깅 비활성화
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        # Vercel 환경에서는 환경 변수를 자동으로 로딩
        # .env 파일은 로컬 개발 환경에서만 사용


# 전역 설정 인스턴스
settings = Settings()

# Vercel 환경에서 환경 변수를 다시 확인하고 업데이트 (이중 체크)
IS_VERCEL = os.environ.get("VERCEL") == "1"
if IS_VERCEL:
    # Vercel 환경에서는 환경 변수를 직접 확인
    if os.getenv("OPENAI_API_KEY") and not settings.OPENAI_API_KEY:
        settings.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if os.getenv("GEMINI_API_KEY") and not settings.GEMINI_API_KEY:
        settings.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if os.getenv("OPENAI_MODEL"):
        settings.OPENAI_MODEL = os.getenv("OPENAI_MODEL")
    if os.getenv("GEMINI_MODEL"):
        settings.GEMINI_MODEL = os.getenv("GEMINI_MODEL")

# 설정 로딩 확인 및 로깅 (디버그용)
import logging
config_logger = logging.getLogger(__name__)

# 환경 변수 직접 확인 (디버깅용)
openai_env = os.getenv("OPENAI_API_KEY")
gemini_env = os.getenv("GEMINI_API_KEY")

config_logger.info("=" * 60)
config_logger.info("환경 변수 로딩 상태 확인")
config_logger.info(f"환경: {'Vercel (배포)' if IS_VERCEL else '로컬 개발'}")
config_logger.info(f"os.getenv('OPENAI_API_KEY'): {'✅ 설정됨' if openai_env else '❌ 미설정'}")
config_logger.info(f"os.getenv('GEMINI_API_KEY'): {'✅ 설정됨' if gemini_env else '❌ 미설정'}")
config_logger.info(f"settings.OPENAI_API_KEY: {'✅ 설정됨' if settings.OPENAI_API_KEY else '❌ 미설정'}")
if settings.OPENAI_API_KEY:
    config_logger.info(f"  - 길이: {len(settings.OPENAI_API_KEY)} 문자")
    config_logger.info(f"  - 시작: {settings.OPENAI_API_KEY[:10]}...")
    if openai_env:
        config_logger.info(f"  - 환경 변수와 일치: {settings.OPENAI_API_KEY == openai_env}")
config_logger.info(f"settings.GEMINI_API_KEY: {'✅ 설정됨' if settings.GEMINI_API_KEY else '❌ 미설정'}")
if settings.GEMINI_API_KEY:
    config_logger.info(f"  - 길이: {len(settings.GEMINI_API_KEY)} 문자")
    config_logger.info(f"  - 시작: {settings.GEMINI_API_KEY[:10]}...")
    if gemini_env:
        config_logger.info(f"  - 환경 변수와 일치: {settings.GEMINI_API_KEY == gemini_env}")
config_logger.info(f"OPENAI_MODEL: {settings.OPENAI_MODEL}")
config_logger.info(f"GEMINI_MODEL: {settings.GEMINI_MODEL}")
config_logger.info("=" * 60)

# 디렉토리 구조 정의
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / settings.DATA_DIR
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
CACHE_DIR = DATA_DIR / "cache"
ASSETS_DIR = BASE_DIR / "frontend" / "public" / "assets"
LOGS_DIR = BASE_DIR / "logs"
EXPORTS_DIR = BASE_DIR / "exports"  # 분석 결과 내보내기용

# 필요한 디렉토리 생성 (Vercel 환경에서는 건너뛰기)
if not IS_VERCEL:
    for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, CACHE_DIR, ASSETS_DIR, LOGS_DIR, EXPORTS_DIR]:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            # 디렉토리 생성 실패해도 계속 진행
            pass

# 로그 파일 경로 설정 (디렉토리 생성 후)
if not settings.LOG_FILE:
    settings.LOG_FILE = str(LOGS_DIR / "app.log")
