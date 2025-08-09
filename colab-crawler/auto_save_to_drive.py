#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
자동 Google Drive 저장 스크립트
크롤링 완료 후 자동으로 Drive에 저장
"""

import os
import zipfile
from datetime import datetime

def mount_google_drive():
    """Google Drive 마운트"""
    try:
        from google.colab import drive
        drive.mount('/content/drive')
        print("✅ Google Drive 마운트 완료")
        return True
    except Exception as e:
        print(f"❌ Google Drive 마운트 실패: {e}")
        return False

def save_dataset_to_drive(stage_name):
    """데이터셋을 Drive에 저장"""
    dataset_path = "/content/dataset"
    
    if not os.path.exists(dataset_path):
        print("❌ /content/dataset 폴더가 존재하지 않습니다.")
        return False
    
    try:
        # Drive 경로 설정 (실제 경로 구조 반영)
        drive_base_path = "/content/drive/MyDrive/2025 Dev/whosyourancestor/datasets"
        drive_path = f"{drive_base_path}/{stage_name}"
        
        # 기존 폴더 삭제 (있다면)
        if os.path.exists(drive_path):
            import shutil
            shutil.rmtree(drive_path)
            print(f"🗑️ 기존 {stage_name} 폴더 삭제")
        
        # 새 폴더로 복사
        os.makedirs(drive_base_path, exist_ok=True)
        os.system(f"cp -r '{dataset_path}' '{drive_path}'")
        
        print(f"✅ {stage_name} 데이터 저장 완료: {drive_path}")
        
        # 저장된 파일 개수 확인
        total_files = 0
        for root, dirs, files in os.walk(drive_path):
            total_files += len(files)
        
        print(f"📊 총 {total_files}개 파일 저장됨")
        return True
        
    except Exception as e:
        print(f"❌ 저장 실패: {e}")
        return False

def main():
    """메인 실행"""
    print("🚀 Google Drive 자동 저장")
    print("=" * 50)
    
    # Drive 마운트
    if not mount_google_drive():
        return
    
    # 현재 단계 확인 (진행 상황 파일에서)
    if os.path.exists("/content/progress.json"):
        with open("/content/progress.json", "r") as f:
            import json
            progress = json.load(f)
        
        completed_count = len(progress.get("completed", []))
        total_count = len(progress.get("total", []))
        
        if completed_count >= 20:  # 1단계 완료
            print("📊 1단계 데이터 저장 중...")
            save_dataset_to_drive("stage1")
        elif completed_count >= 40:  # 2단계 완료
            print("📊 2단계 데이터 저장 중...")
            save_dataset_to_drive("stage2")
        else:
            print(f"📊 진행 중: {completed_count}/{total_count}")
            print("💡 모든 단계 완료 후 저장됩니다.")
    else:
        print("⚠️ 진행 상황 파일이 없습니다.")
        print("💡 크롤러를 먼저 실행해주세요.")

if __name__ == "__main__":
    main() 