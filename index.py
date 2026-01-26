"""
FastAPI 메인 애플리케이션 - Vercel 진입점
Vercel은 루트의 index.py를 자동으로 인식합니다.
"""
import os
import sys
from pathlib import Path

# Vercel 환경 확인
IS_VERCEL = os.environ.get("VERCEL") == "1"

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# FastAPI 앱 import
from backend.main import app

# Vercel은 FastAPI 앱을 자동으로 인식하므로 app을 직접 export
# Mangum은 필요시 Vercel이 자동으로 처리합니다
