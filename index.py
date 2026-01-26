"""
FastAPI 메인 애플리케이션 - Vercel 진입점
Vercel은 루트의 index.py를 자동으로 인식합니다.
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# FastAPI 앱 import
from backend.main import app

# Vercel은 app 인스턴스를 자동으로 인식합니다
# FastAPI 앱은 루트에 있을 때 자동으로 처리됩니다
