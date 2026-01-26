#!/bin/bash
# 서버 실행 스크립트

# 포트 8000이 사용 중인지 확인
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "포트 8000이 이미 사용 중입니다."
    echo "기존 프로세스를 종료하시겠습니까? (y/n)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo "기존 프로세스 종료 중..."
        lsof -ti:8000 | xargs kill -9
        sleep 2
    else
        echo "다른 포트를 사용하시겠습니까? (포트 번호 입력, 기본값: 8001)"
        read -r port
        PORT=${port:-8001}
        echo "포트 $PORT로 서버를 시작합니다..."
        python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port "$PORT"
        exit 0
    fi
fi

# 서버 실행
echo "서버를 시작합니다..."
cd "$(dirname "$0")"
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
