#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Google Drive에서 데이터셋 로드 스크립트 (진행 상황 표시)
학습용 데이터를 Drive에서 가져오기
"""

import os
import shutil
import time
from tqdm import tqdm

def check_drive_mounted():
    """Drive 마운트 상태 확인"""
    if os.path.exists("/content/drive"):
        print("✅ Google Drive가 마운트되어 있습니다.")
        return True
    else:
        print("❌ Google Drive가 마운트되어 있지 않습니다.")
        return False

def count_files_in_directory(path):
    """디렉토리 내 파일 개수 계산"""
    total_files = 0
    for root, dirs, files in os.walk(path):
        total_files += len(files)
    return total_files

def copy_with_progress(src, dst):
    """진행 상황을 표시하며 파일 복사"""
    try:
        # 전체 파일 개수 계산
        print("📊 파일 개수 계산 중...")
        total_files = count_files_in_directory(src)
        print(f"📁 총 {total_files:,}개 파일 복사 예정")
        
        # 기존 대상 폴더 삭제
        if os.path.exists(dst):
            shutil.rmtree(dst)
            print("🗑️ 기존 로컬 데이터셋 삭제")
        
        # 복사 시작
        print("📦 파일 복사 시작...")
        start_time = time.time()
        
        # tqdm을 사용한 진행 상황 표시
        with tqdm(total=total_files, desc="복사 진행률") as pbar:
            for root, dirs, files in os.walk(src):
                # 대상 디렉토리 생성
                rel_path = os.path.relpath(root, src)
                dst_dir = os.path.join(dst, rel_path)
                os.makedirs(dst_dir, exist_ok=True)
                
                # 파일 복사
                for file in files:
                    src_file = os.path.join(root, file)
                    dst_file = os.path.join(dst_dir, file)
                    
                    try:
                        shutil.copy2(src_file, dst_file)
                        pbar.update(1)
                        
                        # 100개 파일마다 진행 상황 출력
                        if pbar.n % 100 == 0:
                            elapsed = time.time() - start_time
                            rate = pbar.n / elapsed if elapsed > 0 else 0
                            print(f"\n⏱️ {pbar.n:,}개 완료 ({rate:.1f} 파일/초)")
                            
                    except Exception as e:
                        print(f"\n⚠️ 파일 복사 실패: {src_file} - {e}")
                        continue
        
        elapsed = time.time() - start_time
        print(f"\n✅ 복사 완료! 소요 시간: {elapsed:.1f}초")
        return True
        
    except Exception as e:
        print(f"❌ 복사 실패: {e}")
        return False

def load_dataset_from_drive(stage_name):
    """Drive에서 데이터셋 로드 (진행 상황 표시)"""
    # 실제 Drive 경로 구조 반영
    drive_path = f"/content/drive/MyDrive/2025 Dev/whosyourancestor/datasets/{stage_name}"
    local_path = "/content/dataset"
    
    if not os.path.exists(drive_path):
        print(f"❌ Drive 경로가 존재하지 않습니다: {drive_path}")
        print("💡 다음 경로를 확인해주세요:")
        print("   /content/drive/MyDrive/2025 Dev/whosyourancestor/datasets/")
        
        # 사용 가능한 경로 확인
        if os.path.exists("/content/drive/MyDrive"):
            print("\n📁 사용 가능한 Drive 경로:")
            for root, dirs, files in os.walk("/content/drive/MyDrive"):
                if "whosyourancestor" in root or "datasets" in root:
                    print(f"  📂 {root}")
                if len(dirs) > 10:  # 너무 많은 결과 방지
                    break
        return False
    
    print(f"📂 소스 경로: {drive_path}")
    print(f"📂 대상 경로: {local_path}")
    
    # 파일 크기 확인
    total_size = 0
    file_count = 0
    for root, dirs, files in os.walk(drive_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total_size += os.path.getsize(file_path)
                file_count += 1
            except:
                continue
    
    print(f"📊 총 {file_count:,}개 파일, {total_size / (1024*1024):.1f} MB")
    
    # 복사 실행
    if copy_with_progress(drive_path, local_path):
        # 결과 확인
        print("\n📊 복사 결과 확인:")
        total_files = 0
        for root, dirs, files in os.walk(local_path):
            if files:
                rel_path = os.path.relpath(root, local_path)
                print(f"  📂 {rel_path}: {len(files):,}개 파일")
                total_files += len(files)
        
        print(f"\n📊 총 {total_files:,}개 파일 로드됨")
        return True
    else:
        return False

def check_available_stages():
    """사용 가능한 단계 확인"""
    base_path = "/content/drive/MyDrive/2025 Dev/whosyourancestor/datasets"
    
    if not os.path.exists(base_path):
        print("❌ 기본 경로가 존재하지 않습니다.")
        return []
    
    available_stages = []
    for item in os.listdir(base_path):
        if item.startswith("stage"):
            available_stages.append(item)
    
    return sorted(available_stages)

def create_sample_dataset():
    """샘플 데이터셋 생성 (테스트용)"""
    print("🧪 샘플 데이터셋 생성 중...")
    
    sample_path = "/content/dataset"
    os.makedirs(sample_path, exist_ok=True)
    
    # 샘플 구조 생성
    countries = ["japanese", "korean", "chinese"]
    genders = ["female", "male"]
    
    for gender in genders:
        gender_path = os.path.join(sample_path, gender)
        os.makedirs(gender_path, exist_ok=True)
        
        for country in countries:
            country_path = os.path.join(gender_path, country)
            os.makedirs(country_path, exist_ok=True)
            
            # 빈 파일 생성 (테스트용)
            test_file = os.path.join(country_path, "test.txt")
            with open(test_file, "w") as f:
                f.write(f"Sample data for {country} {gender}")
    
    print("✅ 샘플 데이터셋 생성 완료")
    print("💡 이제 ai_training_stage1.py를 테스트할 수 있습니다.")

def main():
    """메인 실행"""
    print("🚀 Google Drive 데이터 로드 (진행 상황 표시)")
    print("=" * 50)
    
    # 1. Drive 마운트 상태 확인
    if not check_drive_mounted():
        print("\n💡 수동 Google Drive 마운트 방법:")
        print("1. 다음 코드를 새 셀에서 실행하세요:")
        print("   from google.colab import drive")
        print("   drive.mount('/content/drive')")
        print("2. 브라우저에서 Google 계정 인증")
        print("3. 인증 코드를 입력")
        print("4. 마운트 완료 후 이 스크립트를 다시 실행")
        return
    
    # 2. 사용 가능한 단계 확인
    available_stages = check_available_stages()
    
    if not available_stages:
        print("❌ 사용 가능한 데이터셋이 없습니다.")
        print("💡 다음 중 하나를 선택하세요:")
        print("  1. 크롤러를 먼저 실행하여 데이터를 수집")
        print("  2. 샘플 데이터셋 생성 (테스트용)")
        
        choice = input("\n선택하세요 (1 또는 2): ").strip()
        
        if choice == "2":
            create_sample_dataset()
        return
    
    print(f"📁 사용 가능한 단계: {', '.join(available_stages)}")
    
    # 3. 1단계 데이터 로드 (우선순위)
    if "stage1" in available_stages:
        print("\n📊 1단계 데이터 로드 중...")
        print("⏳ 대용량 데이터 복사로 시간이 오래 걸릴 수 있습니다.")
        print("💡 진행 상황이 실시간으로 표시됩니다.")
        
        if load_dataset_from_drive("stage1"):
            print("🎉 데이터 로드 완료! AI 학습을 시작할 수 있습니다.")
        else:
            print("❌ 1단계 데이터 로드에 실패했습니다.")
    else:
        print("⚠️ 1단계 데이터가 없습니다.")
        print("💡 다른 단계를 시도하거나 크롤러를 먼저 실행해주세요.")

if __name__ == "__main__":
    main() 