#!/usr/bin/env python3
"""
Vercel 환경에서 API 키 테스트 스크립트
배포된 환경에서 실행하여 API 키가 정상적으로 로딩되는지 확인
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.config import settings

def test_api_keys():
    """API 키 테스트 및 간단한 검증"""
    print("=" * 80)
    print("Vercel API 키 검증")
    print("=" * 80)
    print()
    
    # Vercel 환경 확인
    is_vercel = os.getenv("VERCEL") == "1"
    print(f"환경: {'Vercel (배포)' if is_vercel else '로컬 개발'}")
    print()
    
    # API 키 확인
    openai_key = settings.OPENAI_API_KEY
    gemini_key = settings.GEMINI_API_KEY
    
    print("API 키 상태:")
    print(f"  OPENAI_API_KEY: {'✅ 설정됨' if openai_key else '❌ 미설정'}")
    if openai_key:
        print(f"    - 길이: {len(openai_key)} 문자")
        print(f"    - 유효성: {'✅ 유효 (sk-로 시작)' if openai_key.startswith('sk-') else '⚠️ 형식 확인 필요'}")
    
    print(f"  GEMINI_API_KEY: {'✅ 설정됨' if gemini_key else '❌ 미설정'}")
    if gemini_key:
        print(f"    - 길이: {len(gemini_key)} 문자")
        print(f"    - 유효성: {'✅ 유효 (AIza로 시작)' if gemini_key.startswith('AIza') else '⚠️ 형식 확인 필요'}")
    print()
    
    # 환경 변수 직접 확인
    print("환경 변수 직접 확인:")
    openai_env = os.getenv("OPENAI_API_KEY")
    gemini_env = os.getenv("GEMINI_API_KEY")
    
    print(f"  os.getenv('OPENAI_API_KEY'): {'✅ 있음' if openai_env else '❌ 없음'}")
    print(f"  os.getenv('GEMINI_API_KEY'): {'✅ 있음' if gemini_env else '❌ 없음'}")
    print()
    
    # Settings와 환경 변수 일치 확인
    if openai_key and openai_env:
        match = openai_key == openai_env
        print(f"OPENAI_API_KEY 일치: {'✅ 예' if match else '❌ 아니오'}")
    if gemini_key and gemini_env:
        match = gemini_key == gemini_env
        print(f"GEMINI_API_KEY 일치: {'✅ 예' if match else '❌ 아니오'}")
    print()
    
    # 최종 상태
    if openai_key or gemini_key:
        print("✅ API 키가 설정되어 있습니다.")
        print("   AI 분석 기능을 사용할 수 있습니다.")
        return True
    else:
        print("❌ API 키가 설정되지 않았습니다.")
        print("   기본 분석 모드로만 작동합니다.")
        if is_vercel:
            print("\n해결 방법:")
            print("  1. Vercel Dashboard > Settings > Environment Variables")
            print("  2. OPENAI_API_KEY 및 GEMINI_API_KEY 추가")
            print("  3. 재배포")
        return False

if __name__ == "__main__":
    try:
        success = test_api_keys()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
