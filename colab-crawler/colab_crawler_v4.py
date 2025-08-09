#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
개선된 Colab 크롤러 v4 - 2단계 확장 국가 수집
"""

import os
import sys
import subprocess
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from PIL import Image
import io
import re

def install_requirements():
    """필요한 패키지 자동 설치"""
    print("📦 필요한 패키지 설치 중...")
    
    packages = [
        "selenium==4.15.2",
        "pillow==10.1.0", 
        "requests==2.31.0",
        "webdriver-manager==4.0.1"
    ]
    
    for package in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
            print(f"✅ {package} 설치 완료")
        except subprocess.CalledProcessError as e:
            print(f"❌ {package} 설치 실패: {e}")
    
    # Chrome 드라이버 설치
    try:
        subprocess.run(["apt-get", "update"], check=True, capture_output=True)
        subprocess.run(["apt-get", "install", "-y", "chromium-chromedriver"], 
                      check=True, capture_output=True)
        print("✅ Chrome 드라이버 설치 완료")
    except subprocess.CalledProcessError as e:
        print(f"❌ Chrome 드라이버 설치 실패: {e}")

def setup_environment():
    """환경 설정"""
    os.environ['PATH'] += ':/usr/bin/chromedriver'
    
    try:
        import torch
        if torch.cuda.is_available():
            print("🚀 GPU 가속 사용 가능")
        else:
            print("⚠️ GPU 사용 불가 - CPU 모드로 실행")
    except ImportError:
        print("⚠️ PyTorch 미설치 - CPU 모드로 실행")

class HighQualityColabCrawler:
    def __init__(self):
        """크롤러 초기화"""
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            print("✅ Chrome 드라이버 초기화 완료")
        except Exception as e:
            print(f"❌ 드라이버 초기화 실패: {e}")
            raise
    
    def scroll_page(self, max_scrolls=8):
        """페이지 스크롤하여 더 많은 이미지 로드"""
        for i in range(max_scrolls):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            print(f"📜 스크롤 {i+1}/{max_scrolls}")
    
    def find_image_elements(self):
        """다양한 CSS 선택자로 이미지 요소 찾기"""
        selectors = [
            "img.rg_i",  # 기존 선택자
            "img[data-src]",  # 지연 로딩 이미지
            "img[src*='http']",  # HTTP 이미지
            ".rg_i",  # 이미지 컨테이너
            "img[alt*='celebrity']",  # 셀럽 이미지
            "img[alt*='profile']",  # 프로필 이미지
            "img[alt*='actor']",  # 배우 이미지
            "img[alt*='actress']",  # 여배우 이미지
            "img[alt*='star']",  # 스타 이미지
            "img[alt*='famous']",  # 유명인 이미지
            "img[alt*='japanese']",  # 일본 관련
            "img[alt*='korean']",  # 한국 관련
            "img[alt*='chinese']",  # 중국 관련
        ]
        
        all_elements = []
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ {selector}로 {len(elements)}개 이미지 요소 발견")
                    all_elements.extend(elements)
            except Exception as e:
                print(f"⚠️ {selector} 선택자 실패: {e}")
                continue
        
        # 중복 제거
        unique_elements = []
        seen_urls = set()
        for element in all_elements:
            try:
                url = element.get_attribute('src')
                if url and url not in seen_urls:
                    unique_elements.append(element)
                    seen_urls.add(url)
            except:
                continue
        
        print(f"✅ 총 {len(unique_elements)}개 고유 이미지 요소 발견")
        return unique_elements
    
    def extract_image_url(self, img_element):
        """이미지 URL 추출 - 썸네일에서 원본 URL 추출"""
        try:
            # 썸네일 URL 확인
            thumbnail_url = img_element.get_attribute('src')
            
            # Google 썸네일 URL에서 원본 URL 추출
            if thumbnail_url and 'gstatic.com' in thumbnail_url:
                # 썸네일 URL에서 원본 URL 패턴 추출
                if 'encrypted-tbn0.gstatic.com' in thumbnail_url:
                    # 썸네일 URL에서 원본 URL 추출 시도
                    try:
                        # JavaScript로 원본 URL 추출
                        original_url = self.driver.execute_script("""
                            var img = arguments[0];
                            var parent = img.closest('a');
                            if (parent) {
                                return parent.href;
                            }
                            return null;
                        """, img_element)
                        
                        if original_url and 'http' in original_url:
                            print(f"✅ 원본 URL 추출: {original_url[:50]}...")
                            return original_url
                    except:
                        pass
                
                # 썸네일 URL 자체 사용 (Google 이미지인 경우)
                if 'gstatic.com' in thumbnail_url and 'encrypted-tbn' in thumbnail_url:
                    print(f"⚠️ Google 썸네일 URL 사용: {thumbnail_url[:50]}...")
                    return thumbnail_url
            
            # 이미지 클릭 시도 (더 안전한 방법)
            try:
                # JavaScript로 클릭
                self.driver.execute_script("arguments[0].click();", img_element)
                time.sleep(2)
                
                # 큰 이미지 찾기
                large_img_selectors = [
                    "img.r48jcc",  # Google 이미지 뷰어의 큰 이미지
                    "img[src*='gstatic.com']",  # Google 정적 이미지
                    "img[src*='googleusercontent.com']",  # Google 사용자 콘텐츠
                    "img[src*='http']",  # HTTP 이미지
                    "img[data-src*='http']",  # 지연 로딩 이미지
                    ".tvh9oe img",  # Google 이미지 뷰어
                    ".v4dQwb img",  # Google 이미지 뷰어
                    ".n3VNCb",  # Google 이미지 클래스
                ]
                
                for selector in large_img_selectors:
                    try:
                        large_img = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                        )
                        url = large_img.get_attribute('src')
                        if url and url.startswith('http') and not url.endswith('.gif'):
                            if url != thumbnail_url:
                                print(f"✅ 클릭 후 원본 URL 발견: {url[:50]}...")
                                return url
                    except TimeoutException:
                        continue
                    except Exception as e:
                        continue
                        
            except Exception as e:
                print(f"⚠️ 이미지 클릭 실패: {e}")
            
            # 썸네일 URL 사용 (마지막 수단)
            if thumbnail_url and thumbnail_url.startswith('http'):
                print(f"⚠️ 썸네일 URL 사용: {thumbnail_url[:50]}...")
                return thumbnail_url
            
            return None
            
        except Exception as e:
            print(f"⚠️ 이미지 URL 추출 실패: {e}")
            return None
    
    def download_image(self, url, save_path):
        """고화질 이미지 다운로드 및 검증"""
        try:
            # 잘못된 URL 필터링
            if 'fonts.gstatic.com' in url or 'productlogos' in url:
                print(f"⚠️ 잘못된 이미지 URL 제외: {url[:50]}...")
                return False
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://www.google.com/',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'no-cache',
                'Pragma': 'no-cache'
            }
            
            response = requests.get(url, headers=headers, timeout=20)
            response.raise_for_status()
            
            # 이미지 검증
            img = Image.open(io.BytesIO(response.content))
            
            # 크기 기준 더욱 완화 (최소 80px)
            min_size = min(img.width, img.height)
            if min_size < 80:
                print(f"⚠️ 이미지가 너무 작음: {img.width}x{img.height} (최소: 80px)")
                return False
            
            # 너무 가로세로 비율이 극단적인 이미지 제외 (1:6 이상)
            ratio = max(img.width, img.height) / min(img.width, img.height)
            if ratio > 6:
                print(f"⚠️ 이미지 비율이 너무 극단적: {img.width}x{img.height} (비율: {ratio:.1f})")
                return False
            
            # 원본 크기 유지 (리사이즈하지 않음)
            # 고품질로 저장
            img.save(save_path, 'JPEG', quality=95, optimize=True)
            
            print(f"✅ 이미지 저장: {img.width}x{img.height} (최소 크기: {min_size}px)")
            return True
            
        except Exception as e:
            print(f"⚠️ 이미지 다운로드 실패: {url[:50]}... - {e}")
            return False
    
    def search_and_download(self, query, save_dir, max_images=100):
        """이미지 검색 및 다운로드"""
        # 다양한 검색어 시도
        search_queries = [
            query,  # 원본 검색어
            f"{query} high resolution",  # 고해상도
            f"{query} large size",  # 큰 크기
            f"{query} professional",  # 전문적
            f"{query} official",  # 공식
            f"{query} HD",  # HD
            f"{query} HQ",  # 고품질
        ]
        
        total_downloaded = 0
        
        for search_query in search_queries:
            if total_downloaded >= max_images:
                break
                
            search_url = f"https://www.google.com/search?q={search_query}&tbm=isch&hl=en"
            
            try:
                print(f"🔍 검색 URL: {search_url}")
                self.driver.get(search_url)
                time.sleep(3)
                
                # 페이지 스크롤 (더 많이)
                self.scroll_page(max_scrolls=8)
                
                # 이미지 요소 찾기
                img_elements = self.find_image_elements()
                
                if not img_elements:
                    print("❌ 이미지 요소를 찾을 수 없습니다")
                    continue
                
                os.makedirs(save_dir, exist_ok=True)
                
                for i, img in enumerate(img_elements):
                    if total_downloaded >= max_images:
                        break
                        
                    try:
                        print(f"📸 이미지 {total_downloaded + 1}/{max_images} 처리 중...")
                        
                        # 이미지 URL 추출
                        image_url = self.extract_image_url(img)
                        
                        if image_url:
                            # 파일명 생성
                            filename = f"{query.replace(' ', '_')}_{total_downloaded + 1:03d}.jpg"
                            save_path = os.path.join(save_dir, filename)
                            
                            # 이미지 다운로드
                            if self.download_image(image_url, save_path):
                                total_downloaded += 1
                                print(f"✅ 다운로드 완료: {filename}")
                            else:
                                print(f"❌ 다운로드 실패: {filename}")
                        else:
                            print(f"⚠️ 이미지 URL 추출 실패")
                        
                        # 요청 간격 조절
                        time.sleep(0.5)  # 간격 줄임
                        
                    except Exception as e:
                        print(f"⚠️ 이미지 처리 실패: {e}")
                        continue
                
                print(f"✅ '{search_query}' 검색으로 {total_downloaded}장 수집")
                
                # 충분한 이미지를 수집했으면 다음 검색어로 넘어가지 않음
                if total_downloaded >= max_images:
                    break
                    
            except Exception as e:
                print(f"❌ 검색 실패: {e}")
                continue
        
        return total_downloaded
    
    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            print("✅ 드라이버 종료")


def get_priority_countries():
    """2단계 확장 국가 목록 반환"""
    return [
        # 유럽 확장 (21-30)
        ("swedish", "female"), ("swedish", "male"),
        ("norwegian", "female"), ("norwegian", "male"),
        ("danish", "female"), ("danish", "male"),
        ("polish", "female"), ("polish", "male"),
        ("czech", "female"), ("czech", "male"),
        ("dutch", "female"), ("dutch", "male"),
        ("belgian", "female"), ("belgian", "male"),
        ("swiss", "female"), ("swiss", "male"),
        ("austrian", "female"), ("austrian", "male"),
        ("irish", "female"), ("irish", "male"),
        
        # 동남아시아 확장 (31-34)
        ("vietnamese", "female"), ("vietnamese", "male"),
        ("filipino", "female"), ("filipino", "male"),
        ("malaysian", "female"), ("malaysian", "male"),
        ("singaporean", "female"), ("singaporean", "male"),
        
        # 중남미 확장 (35)
        ("argentine", "female"), ("argentine", "male"),
        
        # 중동 확장 (36-40)
        ("saudi", "female"), ("saudi", "male"),
        ("egyptian", "female"), ("egyptian", "male"),
        ("lebanese", "female"), ("lebanese", "male"),
        ("jordanian", "female"), ("jordanian", "male"),
        ("emirati", "female"), ("emirati", "male"),
    ]

def save_progress(completed_countries, total_countries):
    """진행 상황 저장"""
    try:
        progress = {
            "completed": completed_countries,
            "total": total_countries,
            "timestamp": time.time()
        }
        
        with open("/content/progress.json", "w") as f:
            import json
            json.dump(progress, f, indent=2)
        
        print(f"💾 진행 상황 저장: {len(completed_countries)}/{len(total_countries)} 완료")
        
    except Exception as e:
        print(f"⚠️ 진행 상황 저장 실패: {e}")

def load_progress():
    """진행 상황 로드"""
    try:
        if os.path.exists("/content/progress.json"):
            with open("/content/progress.json", "r") as f:
                import json
                progress = json.load(f)
            
            print(f"📂 진행 상황 복구: {len(progress['completed'])}/{len(progress['total'])} 완료")
            return progress['completed'], progress['total']
        
    except Exception as e:
        print(f"⚠️ 진행 상황 로드 실패: {e}")
    
    return [], []

def main():
    """메인 실행"""
    print("🚀 고화질 Colab 크롤러 v4 시작 (2단계 확장 국가)")
    
    # 크롤러 생성
    crawler = HighQualityColabCrawler()
    
    try:
        # 2단계 확장 국가 목록
        priority_countries = get_priority_countries()
        
        # 진행 상황 로드
        completed_countries, _ = load_progress()
        
        base_path = "/content/dataset"
        total_downloaded = 0
        
        print(f"📋 총 {len(priority_countries)}개 카테고리 수집 예정")
        
        for i, (country, gender) in enumerate(priority_countries):
            # 이미 완료된 국가 건너뛰기
            country_key = f"{country}_{gender}"
            if country_key in completed_countries:
                print(f"⏭️ [{i+1}/{len(priority_countries)}] {country} {gender} 이미 완료됨")
                continue
            
            print(f"\n📸 [{i+1}/{len(priority_countries)}] {country} {gender} 수집 중...")
            
            # 검색어 생성
            query = f"{country} {gender} celebrity profile picture"
            
            # 저장 경로 설정
            save_dir = os.path.join(base_path, gender, country.replace(' ', '_'))
            
            downloaded = crawler.search_and_download(query, save_dir, max_images=100)
            total_downloaded += downloaded
            
            print(f"✅ {country} {gender}: {downloaded}장 수집 완료")
            
            # 진행 상황 저장
            completed_countries.append(country_key)
            save_progress(completed_countries, priority_countries)
            
            # 국가 간 간격 (서버 부하 방지)
            time.sleep(5)
        
        print(f"\n🎉 전체 수집 완료: {total_downloaded}장")
        
        # 결과 확인
        if os.path.exists(base_path):
            print("\n📊 수집된 데이터:")
            for root, dirs, files in os.walk(base_path):
                if files:
                    print(f"  {root}: {len(files)}개 파일")
        
        # 🔥 자동 압축 및 다운로드 추가
        if os.path.exists(base_path) and total_downloaded > 0:
            print("\n📦 자동 압축 및 다운로드 시작...")
            auto_compress_and_download(base_path, total_downloaded)
        
    finally:
        crawler.close()

def auto_compress_and_download(dataset_path, total_files):
    """자동 압축 및 다운로드"""
    try:
        import zipfile
        
        zip_path = "/content/dataset.zip"
        
        # 기존 압축 파일 삭제
        if os.path.exists(zip_path):
            os.remove(zip_path)
            print("🗑️ 기존 압축 파일 삭제")
        
        print("📦 데이터셋 압축 중...")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files_list in os.walk(dataset_path):
                for file in files_list:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, dataset_path)
                    zipf.write(file_path, arcname)
        
        # 압축 파일 크기 확인
        zip_size = os.path.getsize(zip_path) / (1024 * 1024)  # MB
        print(f"✅ 압축 완료: {zip_path} ({zip_size:.1f} MB)")
        
        # 안전한 다운로드 시도
        try:
            from google.colab import files
            print("📥 데이터셋 다운로드 시작...")
            files.download(zip_path)
            print("🎉 자동 다운로드 완료!")
            print(f"📁 다운로드된 파일: dataset.zip ({zip_size:.1f} MB)")
            print(f"📊 총 {total_files}개 파일이 포함되었습니다.")
            
        except Exception as download_error:
            print(f"⚠️ 자동 다운로드 실패: {download_error}")
            print("\n💡 수동 다운로드 방법:")
            print("1. 다음 코드를 새 셀에서 실행하세요:")
            print("   from google.colab import files")
            print("   files.download('/content/dataset.zip')")
            print("2. 또는 브라우저에서 직접 다운로드:")
            print("   - 파일 탐색기에서 /content/dataset.zip 파일을 찾아 다운로드")
            print("3. 또는 다음 명령어로 다운로드:")
            print("   !wget --content-disposition /content/dataset.zip")
        
    except Exception as e:
        print(f"❌ 자동 압축/다운로드 실패: {e}")
        print("💡 수동으로 다운로드 스크립트를 실행하세요.")

# 패키지 설치 및 환경 설정
if __name__ == "__main__":
    install_requirements()
    setup_environment()
    main() 