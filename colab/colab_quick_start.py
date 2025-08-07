#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Colab 빠른 시작 크롤러
간단한 테스트용 스크립트
"""

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import io

def setup_colab():
    """Colab 환경 설정"""
    # 필요한 패키지 설치
    os.system("pip install selenium pillow requests")
    
    # Chrome 드라이버 설치
    os.system("apt-get update")
    os.system("apt-get install -y chromium-chromedriver")
    
    # 환경 변수 설정
    os.environ['PATH'] += ':/usr/bin/chromedriver'
    
    print("✅ Colab 환경 설정 완료")

def create_crawler():
    """크롤러 생성"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def download_images(driver, query, save_dir, max_images=20):
    """이미지 다운로드"""
    search_url = f"https://www.google.com/search?q={query}&tbm=isch"
    
    try:
        driver.get(search_url)
        time.sleep(2)
        
        # 이미지 요소 찾기
        img_elements = driver.find_elements(By.CSS_SELECTOR, "img.rg_i")
        downloaded = 0
        
        os.makedirs(save_dir, exist_ok=True)
        
        for i, img in enumerate(img_elements[:max_images]):
            try:
                # 이미지 클릭
                img.click()
                time.sleep(1)
                
                # 큰 이미지 찾기
                large_img = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "img.r48jcc"))
                )
                
                src = large_img.get_attribute('src')
                if src and src.startswith('http'):
                    # 이미지 다운로드
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    
                    response = requests.get(src, headers=headers, timeout=10)
                    if response.status_code == 200:
                        # 이미지 처리
                        img_data = Image.open(io.BytesIO(response.content))
                        img_data = img_data.resize((224, 224), Image.Resampling.LANCZOS)
                        
                        # 저장
                        filename = f"{query.replace(' ', '_')}_{i+1:03d}.jpg"
                        save_path = os.path.join(save_dir, filename)
                        img_data.save(save_path, 'JPEG', quality=85)
                        
                        downloaded += 1
                        print(f"✅ 다운로드: {filename}")
                
            except Exception as e:
                print(f"⚠️ 이미지 다운로드 실패: {e}")
                continue
        
        return downloaded
        
    except Exception as e:
        print(f"❌ 검색 실패: {e}")
        return 0

def main():
    """메인 실행"""
    print("🚀 Colab 크롤러 시작")
    
    # 환경 설정
    setup_colab()
    
    # 크롤러 생성
    driver = create_crawler()
    
    try:
        # 테스트 수집
        test_queries = [
            "japanese female celebrity profile picture",
            "korean male celebrity profile picture"
        ]
        
        base_path = "/content/dataset"
        total_downloaded = 0
        
        for query in test_queries:
            print(f"\n📸 {query} 수집 중...")
            
            # 저장 경로 설정
            save_dir = os.path.join(base_path, query.split()[1], query.split()[0])
            
            downloaded = download_images(driver, query, save_dir, max_images=10)
            total_downloaded += downloaded
            
            print(f"✅ {query}: {downloaded}장 수집 완료")
            time.sleep(3)
        
        print(f"\n🎉 전체 수집 완료: {total_downloaded}장")
        
        # 결과 확인
        if os.path.exists(base_path):
            print("\n📊 수집된 데이터:")
            for root, dirs, files in os.walk(base_path):
                if files:
                    print(f"  {root}: {len(files)}개 파일")
        
    finally:
        driver.quit()
        print("✅ 크롤러 종료")

if __name__ == "__main__":
    main() 