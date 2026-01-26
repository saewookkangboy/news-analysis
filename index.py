"""
Vercel 루트 진입점 (선택사항)
주로 api/index.py를 사용하지만, 일부 Vercel 설정에서는 루트의 index.py도 인식할 수 있습니다.
"""
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# FastAPI 앱 import
from backend.main import app

# Vercel은 FastAPI 앱을 자동으로 인식
# 주 진입점은 api/index.py를 사용하는 것을 권장합니다
