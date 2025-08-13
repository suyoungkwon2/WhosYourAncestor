#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Colab 크롤러 v7 - 대규모 데이터 수집 & Google Drive 자동 저장 (수정됨)
12개 국가 여성 셀카 사진 각각 최소 300장 수집
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
import zipfile
from google.colab import drive

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

def setup_google_drive():
    """Google Drive 마운트"""
    print("🔗 Google Drive 연결 중...")
    try:
        drive.mount('/content/drive')
        print("✅ Google Drive 연결 완료")
        return True
    except Exception as e:
        print(f"❌ Google Drive 연결 실패: {e}")
        return False

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

class LargeScaleColabCrawler:
    def __init__(self):
        """크롤러 초기화"""
        self.driver = None
        self.setup_driver()

    def setup_driver(self):
        """Chrome 드라이버 설정 - 안정성 최적화"""
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

        # 안정성을 위한 추가 옵션
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        chrome_options.add_argument('--disable-images')  # 이미지 로딩 비활성화로 속도 향상
        chrome_options.add_argument('--disable-javascript')  # JavaScript 비활성화로 안정성 향상
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            # 페이지 로드 타임아웃 설정
            self.driver.set_page_load_timeout(30)
            self.driver.implicitly_wait(10)

            print("✅ Chrome 드라이버 초기화 완료 (안정성 최적화)")
        except Exception as e:
            print(f"❌ 드라이버 초기화 실패: {e}")
            raise

    def scroll_page(self, max_scrolls=15):
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
            "img[alt*='portrait']",  # 초상화
            "img[alt*='face']",  # 얼굴
            "img[alt*='woman']",  # 여성
            "img[alt*='female']",  # 여성
            "img[alt*='influencer']",  # 인플루언서
            "img[alt*='model']",  # 모델
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
        """원본 이미지 URL 추출 - 완전히 새로운 접근 방식"""
        try:
            # 썸네일 URL 확인
            thumbnail_url = img_element.get_attribute('src')

            # 잘못된 URL 필터링
            if not thumbnail_url or not thumbnail_url.startswith('http'):
                return None

            # Google 썸네일 URL 처리 - 원본 URL 추출
            if 'gstatic.com' in thumbnail_url and 'encrypted-tbn' in thumbnail_url:
                # 방법 1: 부모 링크에서 원본 URL 추출
                try:
                    parent_link = img_element.find_element(By.XPATH, "./..")
                    if parent_link.tag_name == 'a':
                        original_url = parent_link.get_attribute('href')
                        if original_url and 'http' in original_url and not original_url.endswith('.gif'):
                            print(f"✅ 원본 URL 추출 (부모 링크): {original_url[:50]}...")
                            return original_url
                except:
                    pass

                # 방법 2: JavaScript로 원본 URL 추출
                try:
                    original_url = self.driver.execute_script("""
                        var img = arguments[0];
                        var parent = img.closest('a');
                        if (parent && parent.href) {
                            return parent.href;
                        }
                        return null;
                    """, img_element)

                    if original_url and 'http' in original_url and not original_url.endswith('.gif'):
                        print(f"✅ 원본 URL 추출 (JavaScript): {original_url[:50]}...")
                        return original_url
                except:
                    pass

                # 방법 3: 이미지 클릭으로 원본 URL 추출 (최적화)
                try:
                    # JavaScript로 클릭
                    self.driver.execute_script("arguments[0].click();", img_element)
                    time.sleep(3)  # 대기 시간 최적화

                    # 현재 페이지의 URL 확인
                    current_url = self.driver.current_url
                    if 'imgres' in current_url or 'search' in current_url:
                        # 이미지 뷰어 페이지에서 큰 이미지 찾기 (빠른 선택자만)
                        large_img_selectors = [
                            "img.r48jcc",  # Google 이미지 뷰어의 큰 이미지
                            "img[src*='http']",  # HTTP 이미지
                            ".n3VNCb",  # Google 이미지 클래스
                            "img[src*='usercontent']",  # 사용자 콘텐츠
                        ]

                        for selector in large_img_selectors:
                            try:
                                large_imgs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                                for large_img in large_imgs:
                                    url = large_img.get_attribute('src')
                                    if url and url.startswith('http') and not url.endswith('.gif'):
                                        if url != thumbnail_url and 'gstatic.com' not in url:
                                            print(f"✅ 클릭 후 원본 URL 발견: {url[:50]}...")
                                            return url
                            except Exception as e:
                                continue

                        # 페이지에서 직접 이미지 URL 추출 시도 (빠른 패턴만)
                        try:
                            page_source = self.driver.page_source
                            # 이미지 URL 패턴 찾기 (최적화된 패턴)
                            import re
                            img_patterns = [
                                r'https://[^"\s]+\.(?:jpg|jpeg|png|webp)',
                                r'https://[^"\s]+/images[^"\s]+',
                            ]

                            for pattern in img_patterns:
                                matches = re.findall(pattern, page_source)
                                for match in matches:
                                    if match != thumbnail_url and 'gstatic.com' not in match:
                                        print(f"✅ 페이지에서 원본 URL 발견: {match[:50]}...")
                                        return match
                        except:
                            pass

                except Exception as e:
                    print(f"⚠️ 이미지 클릭 실패: {e}")

                # 썸네일 URL 자체 사용 (마지막 수단)
                print(f"⚠️ Google 썸네일 URL 사용: {thumbnail_url[:50]}...")
                return thumbnail_url

            # 일반 이미지 URL 처리
            if thumbnail_url.startswith('http') and not thumbnail_url.endswith('.gif'):
                # 이미지 확장자 확인
                valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
                if any(ext in thumbnail_url.lower() for ext in valid_extensions):
                    print(f"✅ 직접 이미지 URL: {thumbnail_url[:50]}...")
                    return thumbnail_url

            # 썸네일 URL 사용 (마지막 수단)
            if thumbnail_url and thumbnail_url.startswith('http'):
                print(f"⚠️ 썸네일 URL 사용: {thumbnail_url[:50]}...")
                return thumbnail_url

            return None

        except Exception as e:
            print(f"⚠️ 이미지 URL 추출 실패: {e}")
            return None

    def download_image(self, url, save_path):
        """고화질 이미지 다운로드 및 검증 - 완전히 개선된 버전"""
        try:
            # 잘못된 URL 필터링
            if not url or not url.startswith('http'):
                print(f"⚠️ 잘못된 URL 형식: {url}")
                return False

            # Google 썸네일 URL 필터링 (원본 이미지만 다운로드)
            if 'gstatic.com' in url and 'encrypted-tbn' in url:
                print(f"⚠️ Google 썸네일 URL 제외 (원본 이미지 필요): {url[:50]}...")
                return False

            if any(bad in url.lower() for bad in ['fonts.gstatic.com', 'productlogos', 'favicon', 'logo']):
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

            response = requests.get(url, headers=headers, timeout=30)  # 타임아웃 증가
            response.raise_for_status()

            # Content-Type 확인
            content_type = response.headers.get('content-type', '').lower()
            if not content_type.startswith('image/'):
                print(f"⚠️ 이미지가 아닌 파일: {content_type}")
                return False

            # 이미지 검증
            try:
                img = Image.open(io.BytesIO(response.content))
            except Exception as e:
                print(f"⚠️ 이미지 파일이 아님: {e}")
                return False

            # 크기 기준 더욱 완화 (최소 100px로 다시 상향)
            min_size = min(img.width, img.height)
            if min_size < 100:
                print(f"⚠️ 이미지가 너무 작음: {img.width}x{img.height} (최소: 100px)")
                return False

            # 너무 가로세로 비율이 극단적인 이미지 제외 (1:5 이상)
            ratio = max(img.width, img.height) / min(img.width, img.height)
            if ratio > 5:
                print(f"⚠️ 이미지 비율이 너무 극단적: {img.width}x{img.height} (비율: {ratio:.1f})")
                return False

            # 이미지 모드 확인 및 변환
            if img.mode in ('RGBA', 'LA', 'P'):
                # 투명도가 있는 이미지는 RGB로 변환
                if img.mode == 'RGBA':
                    # 흰색 배경에 합성
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                else:
                    img = img.convert('RGB')

            # 고품질로 저장 (quality 파라미터 문제 완전 해결)
            try:
                # quality 파라미터 없이 저장
                img.save(save_path, 'JPEG', optimize=True)
            except Exception as e:
                # JPEG 실패 시 PNG로 시도
                try:
                    save_path_png = save_path.replace('.jpg', '.png')
                    img.save(save_path_png, 'PNG')
                    print(f"✅ PNG로 저장: {save_path_png}")
                    return True
                except Exception as e2:
                    print(f"⚠️ 이미지 저장 실패: {e2}")
                    return False

            print(f"✅ 이미지 저장: {img.width}x{img.height} (최소 크기: {min_size}px)")
            return True

        except requests.exceptions.RequestException as e:
            print(f"⚠️ 네트워크 오류: {url[:50]}... - {e}")
            return False
        except Exception as e:
            print(f"⚠️ 이미지 다운로드 실패: {url[:50]}... - {e}")
            return False

    def get_search_queries(self, country):
        """국가별 검색 쿼리 생성"""
        queries = {
            "british": [
                "british girl selfie", "british woman selfie", "uk girl selfie",
                "uk woman portrait", "british girl casual photo", "british woman candid"
            ],
            "chinese": [
                "中国女生 自拍", "中国女性 自拍", "中国女生 日常 自拍",
                "中国女性 生活照", "中国女生 街拍 自拍", "中国美女 自拍"
            ],
            "ethiopian": [
                "ethiopian girl selfie", "ethiopian woman selfie", "ethiopian girl portrait",
                "ethiopian woman casual photo", "ethiopian beauty selfie", "ethiopian girl candid"
            ],
            "french": [
                "femme française selfie", "fille française selfie", "femme française photo portrait",
                "selfie fille française", "photo de femme française", "photo portrait française"
            ],
            "indian": [
                "indian beauty selfie", "indian woman selfie", "indian girl selfie",
                "indian girl portrait", "indian woman candid", "भारतीय लड़की सेल्फी"
            ],
            "indigenous": [
                "native american woman selfie", "indigenous woman selfie", "first nations woman selfie",
                "native american girl portrait", "indigenous beauty selfie", "native woman casual photo"
            ],
            "japanese": [
                "日本人女性 自撮り", "日本人女性 セルフィー", "日本人 素人 自撮り",
                "日本人女性 普通 自撮り", "日本人女性 日常 自撮り", "日本人女性 カジュアル 写真"
            ],
            "korean": [
                "한국 여자 일반인 셀카", "한국 여성 셀카", "한국 여자 일상 셀카",
                "한국 여성 자연스러운 셀카", "한국 여자 사진", "한국 여성 일상 사진"
            ],
            "mexican": [
                "mujeres mexicanas selfie", "mujer mexicana selfie", "selfie mujer mexicana",
                "mujer mexicana foto casual", "foto retrato mujer mexicana", "mujer mexicana foto natural"
            ],
            "nigerian": [
                "nigerian girl selfie", "nigerian woman selfie", "nigerian beauty selfie",
                "nigerian girl portrait", "nigerian woman casual photo", "nigerian girl candid"
            ],
            "russian": [
                "русская девушка селфи", "русская женщина селфи", "селфи русской девушки",
                "фото русской женщины", "портрет русской девушки", "русская женщина фото"
            ],
            "saudi": [
                "فتاة سعودية سيلفي", "امرأة سعودية سيلفي", "صورة سيلفي سعودية",
                "سعودية فتاة صورة شخصية", "saudi girl selfie", "saudi woman selfie"
            ]
        }
        return queries.get(country, [])

    def search_and_download(self, country, save_dir, target_count=300, start_index=0):
        """이미지 검색 및 다운로드 - 안정성 최적화 버전"""
        search_queries = self.get_search_queries(country)

        total_downloaded = start_index
        query_index = 0
        consecutive_failures = 0  # 연속 실패 횟수 추적
        seen_image_urls = set()  # 다운로드한 이미지 URL 기록

        while total_downloaded < target_count and query_index < len(search_queries):
            search_query = search_queries[query_index]
            query_url = f"https://www.google.com/search?q={search_query}&tbm=isch&hl=en"

            try:
                print(f"🔍 검색 쿼리: {search_query}")
                print(f"📊 현재 수집: {total_downloaded}/{target_count}")

                self.driver.get(query_url)
                time.sleep(3)  # 대기 시간 증가 (안정성)

                # 페이지 스크롤 (보수적)
                self.scroll_page(max_scrolls=10)  # 스크롤 횟수 감소

                # 이미지 요소 찾기
                img_elements = self.find_image_elements()

                if not img_elements:
                    print("❌ 이미지 요소를 찾을 수 없습니다")
                    query_index += 1
                    consecutive_failures += 1
                    continue

                os.makedirs(save_dir, exist_ok=True)

                successful_downloads = 0  # 이 쿼리에서 성공한 다운로드 수
                processed_images = 0  # 처리한 이미지 수

                for i, img in enumerate(img_elements):
                    if total_downloaded >= target_count:
                        break

                    try:
                        print(f"📸 이미지 {total_downloaded + 1}/{target_count} 처리 중...")

                        # 이미지 URL 추출
                        image_url = self.extract_image_url(img)

                        if image_url:
                            # 중복 URL 체크
                            if image_url in seen_image_urls:
                                print(f"⚠️ 중복된 이미지 URL 건너뛰기: {image_url[:50]}...")
                                continue
                            
                            # 파일명 생성
                            filename = f"{country}_{total_downloaded + 1:04d}.jpg"
                            save_path = os.path.join(save_dir, filename)

                            # 이미지 다운로드
                            if self.download_image(image_url, save_path):
                                seen_image_urls.add(image_url)  # 다운로드 성공 시 URL 추가
                                total_downloaded += 1
                                successful_downloads += 1
                                consecutive_failures = 0  # 성공 시 실패 카운터 리셋
                                print(f"✅ 다운로드 완료: {filename}")
                                
                                # 10장 다운로드마다 진행 상황 저장
                                if total_downloaded % 10 == 0:
                                    completed, total = load_progress()[:2]
                                    progress = {
                                        "completed": completed,
                                        "total": total,
                                        "last_successful_image_index": total_downloaded
                                    }
                                    with open("/content/progress_v7.json", "w") as f:
                                        import json
                                        json.dump(progress, f, indent=2)
                                    print(f"💾 진행 상황 저장: {country} - {total_downloaded}장 완료")

                            else:
                                consecutive_failures += 1
                                print(f"❌ 다운로드 실패: {filename}")
                        else:
                            consecutive_failures += 1
                            print(f"⚠️ 이미지 URL 추출 실패")

                        processed_images += 1

                        # 연속 실패가 많으면 다음 쿼리로 넘어가기
                        if consecutive_failures >= 20:  # 실패 기준 더 보수적
                            print(f"⚠️ 연속 실패 {consecutive_failures}회 - 다음 쿼리로 넘어갑니다")
                            break

                        # 요청 간격 조절 (안정성)
                        time.sleep(0.5)  # 간격 증가

                    except Exception as e:
                        consecutive_failures += 1
                        print(f"⚠️ 이미지 처리 실패: {e}")
                        continue

                print(f"✅ '{search_query}' 검색으로 {successful_downloads}장 수집 (처리: {processed_images}개)")
                query_index += 1

                # 충분한 이미지를 수집했으면 종료
                if total_downloaded >= target_count:
                    break

            except Exception as e:
                print(f"❌ 검색 실패: {e}")
                consecutive_failures += 1
                query_index += 1
                continue

        return total_downloaded

    def save_to_google_drive(self, country, local_path):
        """Google Drive에 저장"""
        try:
            drive_path = f"/content/drive/MyDrive/WhosYourAncestor/data/female/{country}"
            os.makedirs(drive_path, exist_ok=True)

            # 파일 복사
            import shutil
            for file in os.listdir(local_path):
                if file.endswith('.jpg'):
                    src = os.path.join(local_path, file)
                    dst = os.path.join(drive_path, file)
                    shutil.copy2(src, dst)

            print(f"✅ Google Drive에 저장 완료: {drive_path}")
            return True

        except Exception as e:
            print(f"❌ Google Drive 저장 실패: {e}")
            return False

    def close(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            print("✅ 드라이버 종료")

def get_target_countries():
    """12개 주요 국가 목록 반환 - 전체 국가 활성화"""
    return [
        "korean",      # 대한민국
        "chinese",     # 중국
        "japanese",    # 일본
        "indian",      # 인도
        "saudi",       # 사우디아라비아
        "russian",     # 러시아
        "french",      # 프랑스
        "british",     # 영국
        "nigerian",    # 나이지리아
        "ethiopian",   # 에티오피아
        "indigenous",  # 미국 원주민 인디언
        "mexican",     # 멕시코
    ]

def save_progress(completed_countries, total_countries):
    """진행 상황 저장"""
    try:
        progress = {
            "completed": completed_countries,
            "total": total_countries,
            "timestamp": time.time(),
            "last_successful_image_index": 0 # 국가 완료 시 리셋
        }

        with open("/content/progress_v7.json", "w") as f:
            import json
            json.dump(progress, f, indent=2)

        print(f"💾 진행 상황 저장: {len(completed_countries)}/{len(total_countries)} 완료")

    except Exception as e:
        print(f"⚠️ 진행 상황 저장 실패: {e}")

def load_progress():
    """진행 상황 로드"""
    try:
        if os.path.exists("/content/progress_v7.json"):
            with open("/content/progress_v7.json", "r") as f:
                import json
                progress = json.load(f)

            completed = progress.get('completed', [])
            total = progress.get('total', [])
            last_index = progress.get('last_successful_image_index', 0)
            print(f"📂 진행 상황 복구: {len(completed)}/{len(total)} 완료 (마지막 이미지: {last_index})")
            return completed, total, last_index

    except Exception as e:
        print(f"⚠️ 진행 상황 로드 실패: {e}")

    return [], [], 0

def main():
    """메인 실행 - 안정성 최적화 버전"""
    print("🚀 대규모 Colab 크롤러 v7 시작 (안정성 최적화)")
    print("📊 12개 국가 여성 셀카 사진 각각 300장씩 수집")
    print("🌙 자동 재시작 및 안정성 최적화 모드")

    # Google Drive 연결
    if not setup_google_drive():
        print("❌ Google Drive 연결 실패. 로컬에만 저장합니다.")

    # 자동 재시작 카운터
    restart_count = 0
    max_restarts = 5

    while restart_count < max_restarts:
        try:
            # 크롤러 생성
            crawler = LargeScaleColabCrawler()

            # 13개 주요 국가 목록
            target_countries = get_target_countries()

            # 진행 상황 로드
            completed_countries, target_countries_from_progress, last_successful_image_index = load_progress()
            
            # target_countries가 비어있으면 새로 가져오기
            if not target_countries_from_progress:
                target_countries = get_target_countries()
            else:
                target_countries = target_countries_from_progress

            base_path = "/content/dataset"
            total_downloaded_session = 0

            print(f"📋 총 {len(target_countries)}개 국가 수집 예정")
            print(f"🔄 재시작 횟수: {restart_count}/{max_restarts}")

            for i, country in enumerate(target_countries):
                # 이미 완료된 국가 건너뛰기
                if country in completed_countries:
                    print(f"⏭️ [{i+1}/{len(target_countries)}] {country} 이미 완료됨")
                    continue

                print(f"\n📸 [{i+1}/{len(target_countries)}] {country} 수집 중...")

                # 저장 경로 설정
                save_dir = os.path.join(base_path, "female", country)
                os.makedirs(save_dir, exist_ok=True)

                # 재시도 로직 추가
                max_retries = 3
                downloaded = 0

                for retry in range(max_retries):
                    try:
                        print(f"🔄 시도 {retry + 1}/{max_retries}")
                        downloaded = crawler.search_and_download(country, save_dir, target_count=300, start_index=last_successful_image_index)

                        if downloaded > 0:
                            print(f"✅ {country}: {downloaded}장 수집 완료")
                            break
                        else:
                            print(f"⚠️ {country}: 수집 실패, 재시도 중...")
                            time.sleep(5)  # 재시도 전 대기 시간 증가

                    except Exception as e:
                        print(f"❌ {country} 수집 중 오류: {e}")
                        if retry < max_retries - 1:
                            print("🔄 재시도 중...")
                            time.sleep(10)  # 재시도 대기 시간 증가
                        else:
                            print(f"❌ {country} 수집 최종 실패")

                total_downloaded_session += downloaded

                # Google Drive에 저장
                if downloaded > 0:
                    crawler.save_to_google_drive(country, save_dir)

                # 진행 상황 저장 (더 자주)
                if downloaded >= 300: # 목표치 달성 시에만 완료 처리
                    completed_countries.append(country)
                    save_progress(completed_countries, target_countries)
                    last_successful_image_index = 0  # 다음 국가를 위해 리셋

                # 국가 간 간격 (서버 부하 방지) - 더 길게
                print(f"⏳ 다음 국가까지 30초 대기...")
                time.sleep(30)  # 간격 대폭 증가

            print(f"\n🎉 전체 수집 완료: {total_downloaded_session}장")

            # 결과 확인
            if os.path.exists(base_path):
                print("\n📊 수집된 데이터:")
                for root, dirs, files in os.walk(base_path):
                    if files:
                        print(f"  {root}: {len(files)}개 파일")

            # 🔥 자동 압축 및 다운로드 추가
            if os.path.exists(base_path) and total_downloaded_session > 0:
                print("\n📦 자동 압축 및 다운로드 시작...")
                auto_compress_and_download(base_path, total_downloaded_session)

            # 성공적으로 완료되면 루프 종료
            break

        except KeyboardInterrupt:
            print("\n⚠️ 사용자에 의해 중단됨")
            print("💾 현재까지의 진행 상황을 저장합니다...")
            completed, total, last_index = load_progress()
            save_progress(completed, total) # 여기서 last_index는 저장하지 않음. 국가 단위 저장.
            print("✅ 진행 상황 저장 완료")
            break

        except Exception as e:
            restart_count += 1
            print(f"\n❌ 예상치 못한 오류: {e}")
            print(f"🔄 자동 재시작 {restart_count}/{max_restarts}")
            print("💾 현재까지의 진행 상황을 저장합니다...")
            completed, total, last_index = load_progress()
            save_progress(completed, total) # 여기서 last_index는 저장하지 않음. 국가 단위 저장.
            print("✅ 진행 상황 저장 완료")

            if restart_count < max_restarts:
                print("⏳ 60초 후 자동 재시작...")
                time.sleep(60)
            else:
                print("❌ 최대 재시작 횟수 초과")
                break

        finally:
            try:
                crawler.close()
            except:
                pass

def auto_compress_and_download(dataset_path, total_files):
    """자동 압축 및 다운로드"""
    try:
        import zipfile

        zip_path = "/content/dataset_v7.zip"

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
            print(f"📁 다운로드된 파일: dataset_v7.zip ({zip_size:.1f} MB)")
            print(f"📊 총 {total_files}개 파일이 포함되었습니다.")

        except Exception as download_error:
            print(f"⚠️ 자동 다운로드 실패: {download_error}")
            print("\n💡 수동 다운로드 방법:")
            print("1. 다음 코드를 새 셀에서 실행하세요:")
            print("   from google.colab import files")
            print("   files.download('/content/dataset_v7.zip')")
            print("2. 또는 브라우저에서 직접 다운로드:")
            print("   - 파일 탐색기에서 /content/dataset_v7.zip 파일을 찾아 다운로드")
            print("3. 또는 다음 명령어로 다운로드:")
            print("   !wget --content-disposition /content/dataset_v7.zip")

    except Exception as e:
        print(f"❌ 자동 압축/다운로드 실패: {e}")
        print("💡 수동으로 다운로드 스크립트를 실행하세요.")

# 패키지 설치 및 환경 설정
if __name__ == "__main__":
    install_requirements()
    setup_environment()
    main()


