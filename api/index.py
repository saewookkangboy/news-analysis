"""
Vercel Serverless Function Entry Point
FastAPI 앱을 Vercel에서 실행하기 위한 진입점
"""
import sys
import os
import logging
from pathlib import Path

# Vercel 환경 설정
os.environ.setdefault("VERCEL", "1")

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    # FastAPI 앱 import
    from backend.main import app
    logger.info("FastAPI app imported successfully")
    
    # Vercel은 handler를 export해야 함
    # Mangum을 사용하여 ASGI 앱을 AWS Lambda 핸들러로 변환
    try:
        from mangum import Mangum
        handler = Mangum(app, lifespan="off")
        logger.info("Mangum handler created")
    except ImportError:
        # Mangum이 없으면 직접 app을 export (Vercel이 자동으로 처리)
        handler = app
        logger.info("Using FastAPI app directly (Mangum not available)")
    
except Exception as e:
    logger.error(f"Failed to import app: {e}", exc_info=True)
    # 에러 발생 시에도 기본 handler 제공
    from fastapi import FastAPI
    error_app = FastAPI()
    
    @error_app.get("/")
    async def error_root():
        return {"error": "Application failed to start", "message": str(e)}
    
    handler = error_app

# Vercel에서 인식할 수 있도록 handler export
# handler 변수는 Vercel이 자동으로 찾습니다
