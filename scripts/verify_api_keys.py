#!/usr/bin/env python3
"""
API 키 검증 스크립트
Vercel 환경 변수와 .env 파일의 API 키가 정상적으로 로딩되는지 확인
"""
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.config import settings

def verify_api_keys():
    """API 키 검증"""
    print("=" * 80)
    print("API 키 검증 리포트")
    print("=" * 80)
    print()
    
    # 1. 환경 변수 직접 확인
    print("1. 환경 변수 직접 확인 (os.getenv)")
    print("-" * 80)
    openai_env = os.getenv("OPENAI_API_KEY")
    gemini_env = os.getenv("GEMINI_API_KEY")
    
    print(f"OPENAI_API_KEY (환경 변수): {'설정됨' if openai_env else '❌ 미설정'}")
    if openai_env:
        print(f"  - 길이: {len(openai_env)} 문자")
        print(f"  - 시작: {openai_env[:10]}...")
    
    print(f"GEMINI_API_KEY (환경 변수): {'설정됨' if gemini_env else '❌ 미설정'}")
    if gemini_env:
        print(f"  - 길이: {len(gemini_env)} 문자")
        print(f"  - 시작: {gemini_env[:10]}...")
    print()
    
    # 2. Settings 인스턴스 확인
    print("2. Settings 인스턴스 확인 (backend.config.settings)")
    print("-" * 80)
    print(f"OPENAI_API_KEY (Settings): {'설정됨' if settings.OPENAI_API_KEY else '❌ 미설정'}")
    if settings.OPENAI_API_KEY:
        print(f"  - 길이: {len(settings.OPENAI_API_KEY)} 문자")
        print(f"  - 시작: {settings.OPENAI_API_KEY[:10]}...")
        print(f"  - 환경 변수와 일치: {settings.OPENAI_API_KEY == openai_env}")
    
    print(f"GEMINI_API_KEY (Settings): {'설정됨' if settings.GEMINI_API_KEY else '❌ 미설정'}")
    if settings.GEMINI_API_KEY:
        print(f"  - 길이: {len(settings.GEMINI_API_KEY)} 문자")
        print(f"  - 시작: {settings.GEMINI_API_KEY[:10]}...")
        print(f"  - 환경 변수와 일치: {settings.GEMINI_API_KEY == gemini_env}")
    print()
    
    # 3. .env 파일 확인
    print("3. .env 파일 확인")
    print("-" * 80)
    env_file = project_root / ".env"
    if env_file.exists():
        print(f".env 파일 존재: ✅")
        with open(env_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            openai_in_file = False
            gemini_in_file = False
            for line in lines:
                if line.strip().startswith("OPENAI_API_KEY="):
                    openai_in_file = True
                    value = line.split("=", 1)[1].strip()
                    print(f"  - OPENAI_API_KEY: {'설정됨' if value else '❌ 빈 값'}")
                    if value:
                        print(f"    길이: {len(value)} 문자")
                        print(f"    시작: {value[:10]}...")
                elif line.strip().startswith("GEMINI_API_KEY="):
                    gemini_in_file = True
                    value = line.split("=", 1)[1].strip()
                    print(f"  - GEMINI_API_KEY: {'설정됨' if value else '❌ 빈 값'}")
                    if value:
                        print(f"    길이: {len(value)} 문자")
                        print(f"    시작: {value[:10]}...")
            
            if not openai_in_file:
                print("  - OPENAI_API_KEY: ❌ .env 파일에 없음")
            if not gemini_in_file:
                print("  - GEMINI_API_KEY: ❌ .env 파일에 없음")
    else:
        print(f".env 파일 존재: ❌")
    print()
    
    # 4. Vercel 환경 확인
    print("4. Vercel 환경 확인")
    print("-" * 80)
    is_vercel = os.getenv("VERCEL") == "1"
    print(f"Vercel 환경: {'✅ 예' if is_vercel else '❌ 아니오 (로컬)'}")
    if is_vercel:
        print("  - Vercel 환경에서는 환경 변수가 자동으로 로딩됩니다")
        print("  - .env 파일은 Vercel에서 무시됩니다")
    else:
        print("  - 로컬 환경에서는 .env 파일이 사용됩니다")
    print()
    
    # 5. API 키 일치 여부 확인
    print("5. API 키 일치 여부 확인")
    print("-" * 80)
    
    # OpenAI 키 일치 확인
    if settings.OPENAI_API_KEY and openai_env:
        openai_match = settings.OPENAI_API_KEY == openai_env
        print(f"OPENAI_API_KEY 일치: {'✅ 예' if openai_match else '❌ 아니오'}")
        if not openai_match:
            print("  ⚠️ Settings와 환경 변수가 다릅니다!")
    elif settings.OPENAI_API_KEY:
        print("OPENAI_API_KEY: Settings에만 있음 (환경 변수 없음)")
    elif openai_env:
        print("OPENAI_API_KEY: 환경 변수에만 있음 (Settings에 없음)")
    else:
        print("OPENAI_API_KEY: ❌ 모두 없음")
    
    # Gemini 키 일치 확인
    if settings.GEMINI_API_KEY and gemini_env:
        gemini_match = settings.GEMINI_API_KEY == gemini_env
        print(f"GEMINI_API_KEY 일치: {'✅ 예' if gemini_match else '❌ 아니오'}")
        if not gemini_match:
            print("  ⚠️ Settings와 환경 변수가 다릅니다!")
    elif settings.GEMINI_API_KEY:
        print("GEMINI_API_KEY: Settings에만 있음 (환경 변수 없음)")
    elif gemini_env:
        print("GEMINI_API_KEY: 환경 변수에만 있음 (Settings에 없음)")
    else:
        print("GEMINI_API_KEY: ❌ 모두 없음")
    print()
    
    # 6. 최종 상태 요약
    print("6. 최종 상태 요약")
    print("-" * 80)
    openai_ok = bool(settings.OPENAI_API_KEY)
    gemini_ok = bool(settings.GEMINI_API_KEY)
    
    print(f"OpenAI API 키: {'✅ 정상' if openai_ok else '❌ 미설정'}")
    print(f"Gemini API 키: {'✅ 정상' if gemini_ok else '❌ 미설정'}")
    
    if openai_ok or gemini_ok:
        print("\n✅ 최소 하나의 API 키가 설정되어 있습니다.")
        print("   AI 분석 기능을 사용할 수 있습니다.")
    else:
        print("\n❌ API 키가 설정되지 않았습니다.")
        print("   기본 분석 모드로만 작동합니다.")
    
    print()
    print("=" * 80)
    
    # 7. Vercel 배포 시 확인 사항
    if not is_vercel:
        print("\n📝 Vercel 배포 시 확인 사항:")
        print("   1. Vercel Dashboard > Project Settings > Environment Variables")
        print("   2. 다음 변수들이 설정되어 있는지 확인:")
        print("      - OPENAI_API_KEY")
        print("      - GEMINI_API_KEY")
        print("   3. Production, Preview, Development 환경 모두에 설정 권장")
        print("   4. 배포 후 Vercel 로그에서 환경 변수 로딩 확인")
        print()
    
    return openai_ok or gemini_ok

if __name__ == "__main__":
    try:
        success = verify_api_keys()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
