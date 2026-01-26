"""
Vercel Serverless Function Entry Point
FastAPI 앱을 Vercel에서 실행하기 위한 진입점
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# FastAPI 앱 import
from backend.main import app

# Vercel은 handler를 export해야 함
# Mangum을 사용하여 ASGI 앱을 AWS Lambda 핸들러로 변환
try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    # Mangum이 없으면 직접 app을 export (Vercel이 자동으로 처리)
    handler = app
