#!/usr/bin/env python3
"""
Stitch 프로젝트 목록을 조회하는 스크립트
"""
import json
import subprocess
import sys
import os

def list_stitch_projects():
    """Stitch 프로젝트 목록을 조회합니다."""
    # 환경 변수 설정
    env = os.environ.copy()
    env['GOOGLE_CLOUD_PROJECT'] = 'gen-lang-client-0445807298'
    
    # MCP 프로토콜을 통해 list_projects 도구 호출
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "list_projects",
            "arguments": {}
        }
    }
    
    try:
        # stitch-mcp 실행
        process = subprocess.Popen(
            ['npx', '-y', 'stitch-mcp'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env
        )
        
        # 요청 전송
        request_json = json.dumps(request) + '\n'
        stdout, stderr = process.communicate(input=request_json, timeout=30)
        
        # stderr에서 로그 확인
        if stderr:
            print("서버 로그:", file=sys.stderr)
            for line in stderr.split('\n'):
                if line.strip():
                    print(f"  {line}", file=sys.stderr)
        
        # 응답 파싱
        for line in stdout.split('\n'):
            if line.strip():
                try:
                    response = json.loads(line)
                    if 'result' in response:
                        return response['result']
                    elif 'error' in response:
                        print(f"오류: {response['error']}", file=sys.stderr)
                        return None
                except json.JSONDecodeError:
                    continue
        
        return None
        
    except subprocess.TimeoutExpired:
        print("요청 시간 초과", file=sys.stderr)
        process.kill()
        return None
    except Exception as e:
        print(f"오류 발생: {e}", file=sys.stderr)
        return None

if __name__ == '__main__':
    result = list_stitch_projects()
    if result:
        print("\n=== Stitch 프로젝트 목록 ===\n")
        projects = result.get('projects', [])
        if projects:
            for i, project in enumerate(projects, 1):
                name = project.get('name', 'N/A')
                title = project.get('title', '제목 없음')
                create_time = project.get('createTime', 'N/A')
                device_type = project.get('deviceType', 'N/A')
                
                print(f"{i}. {title}")
                print(f"   ID: {name}")
                print(f"   생성일: {create_time}")
                print(f"   디바이스 타입: {device_type}")
                print()
        else:
            print("프로젝트가 없습니다.")
            print("\n새 프로젝트를 생성하려면 Stitch 웹사이트(https://stitch.withgoogle.com/)를 방문하세요.")
    else:
        print("프로젝트 목록을 가져오는데 실패했습니다.")
