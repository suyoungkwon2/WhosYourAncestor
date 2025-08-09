#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cursor에서 Colab 원격 연결 설정
"""

import subprocess
import sys
import os

def setup_colab_connection():
    """Colab 원격 연결 설정"""
    
    print("🚀 Colab 원격 연결 설정 시작")
    
    # 1. ngrok 설치 (터널링용)
    try:
        subprocess.run(["pip", "install", "pyngrok"], check=True)
        print("✅ pyngrok 설치 완료")
    except Exception as e:
        print(f"❌ pyngrok 설치 실패: {e}")
        return False
    
    # 2. Colab 연결 코드 생성
    colab_code = '''
# Colab에서 실행할 코드
!pip install selenium pillow requests
!apt-get update
!apt-get install -y chromium-chromedriver

# ngrok 설치
!pip install pyngrok

# 터널 설정
from pyngrok import ngrok
import os

# SSH 터널 생성
ssh_tunnel = ngrok.connect(22, "tcp")
print(f"SSH 터널: {ssh_tunnel.public_url}")

# HTTP 터널 생성 (웹 인터페이스용)
http_tunnel = ngrok.connect(8080, "http")
print(f"HTTP 터널: {http_tunnel.public_url}")

print("✅ Colab 터널 설정 완료")
'''
    
    # 3. 로컬 연결 스크립트 생성
    local_script = '''
#!/usr/bin/env python3
import paramiko
import time

def connect_to_colab():
    """Colab에 SSH 연결"""
    
    # SSH 클라이언트 설정
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # Colab SSH 연결 (터널 URL 필요)
        tunnel_url = "YOUR_NGROK_TUNNEL_URL"  # Colab에서 받은 URL
        ssh.connect(tunnel_url, username="root", password="")
        
        print("✅ Colab에 연결됨")
        
        # 원격 명령 실행
        stdin, stdout, stderr = ssh.exec_command("python /content/colab_crawler.py")
        
        # 결과 출력
        for line in stdout:
            print(line.strip())
            
    except Exception as e:
        print(f"❌ 연결 실패: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    connect_to_colab()
'''
    
    # 4. 파일 저장
    with open("colab_tunnel_setup.py", "w", encoding="utf-8") as f:
        f.write(colab_code)
    
    with open("local_colab_connect.py", "w", encoding="utf-8") as f:
        f.write(local_script)
    
    print("✅ Colab 연결 스크립트 생성 완료")
    print("\n📋 사용 방법:")
    print("1. colab_tunnel_setup.py를 Colab에 업로드")
    print("2. Colab에서 실행하여 터널 URL 받기")
    print("3. local_colab_connect.py에서 URL 업데이트")
    print("4. 로컬에서 Colab 크롤러 실행")
    
    return True

def create_simple_colab_runner():
    """간단한 Colab 실행 스크립트"""
    
    simple_runner = '''
#!/usr/bin/env python3
"""
간단한 Colab 크롤러 실행 스크립트
"""

import requests
import json
import time

def run_colab_crawler():
    """Colab API를 통한 크롤러 실행"""
    
    # Colab API 엔드포인트 (예시)
    colab_api_url = "https://colab.research.google.com/api/notebooks"
    
    # 크롤링 작업 요청
    payload = {
        "action": "run_crawler",
        "script": "colab_crawler.py",
        "params": {
            "countries": ["japanese", "korean", "chinese"],
            "max_images": 50
        }
    }
    
    try:
        response = requests.post(colab_api_url, json=payload)
        if response.status_code == 200:
            print("✅ Colab 크롤러 실행 요청 완료")
            return response.json()
        else:
            print(f"❌ 요청 실패: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ API 호출 실패: {e}")
        return None

if __name__ == "__main__":
    run_colab_crawler()
'''
    
    with open("simple_colab_runner.py", "w", encoding="utf-8") as f:
        f.write(simple_runner)
    
    print("✅ 간단한 Colab 실행 스크립트 생성 완료")

if __name__ == "__main__":
    setup_colab_connection()
    create_simple_colab_runner() 