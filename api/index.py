"""
Vercel Serverless Function Entry Point
FastAPI 앱을 Vercel에서 실행하기 위한 진입점

Vercel 함수 설정:
- maxDuration: 60초
- memory: 3008MB
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

# FastAPI 앱 import
try:
    from backend.main import app
    logger.info("FastAPI app imported successfully")
except Exception as e:
    logger.error(f"Failed to import app: {e}", exc_info=True)
    # 에러 발생 시에도 기본 handler 제공
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/")
    async def error_root():
        return {"error": "Application failed to start", "message": str(e)}

# Mangum을 사용하여 ASGI 앱을 AWS Lambda 핸들러로 변환
# Vercel은 Mangum handler를 필요로 합니다 (requirements.txt에 mangum 포함 필수)
try:
    from mangum import Mangum
    # handler를 Mangum 인스턴스로 정의 (Vercel이 기대하는 형식)
    handler = Mangum(app, lifespan="off")
    logger.info("Mangum handler created successfully")
except ImportError as e:
    # 로컬 개발 환경에서는 Mangum이 없을 수 있음
    # 하지만 Vercel 배포 시에는 requirements.txt에 mangum이 포함되어 있어야 함
    logger.error(f"Mangum import failed: {e}")
    logger.error("Vercel 배포 시 requirements.txt에 mangum==0.17.0이 포함되어 있는지 확인하세요")
    # Fallback: app을 직접 사용 (Vercel에서는 작동하지 않을 수 있음)
    handler = app

# Vercel에서 인식할 수 있도록 handler export
# handler는 모듈 레벨 변수로 export됩니다
