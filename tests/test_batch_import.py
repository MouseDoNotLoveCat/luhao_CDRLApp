#!/usr/bin/env python3
"""
批量导入功能测试脚本
"""

import requests
import time
from pathlib import Path

# API 基础 URL
BASE_URL = "http://localhost:8000"

# 测试文件目录
SAMPLES_DIR = Path("Samples")

def test_batch_import():
    """测试批量导入功能"""
    
    print("=" * 80)
    print("🧪 批量导入功能测试")
    print("=" * 80)
    
    # 获取所有 .docx 文件（排除临时文件）
    docx_files = [
        f for f in SAMPLES_DIR.glob("*.docx")
        if not f.name.startswith("~$")
    ]
    
    if not docx_files:
        print("❌ 没有找到测试文件")
        return
    
    # 选择前 3 个文件进行测试
    test_files = docx_files[:3]
    
    print(f"\n📝 选择的测试文件:")
    for i, file in enumerate(test_files, 1):
        size = file.stat().st_size / 1024 / 1024
        print(f"   {i}. {file.name} ({size:.2f} MB)")
    
    # 准备文件
    print(f"\n📤 准备上传 {len(test_files)} 个文件...")
    files = []
    for file_path in test_files:
        with open(file_path, 'rb') as f:
            files.append(('files', (file_path.name, f.read(), 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')))
    
    # 发送批量导入请求
    print(f"\n🚀 发送批量导入请求...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/import/batch",
            files=files,
            timeout=60
        )
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ 批量导入成功 (耗时: {elapsed_time:.2f}s)")
            print(f"\n📊 导入结果:")
            print(f"   总文件数: {result.get('total_files', 0)}")
            print(f"   成功导入: {result.get('successful', 0)}")
            print(f"   导入失败: {result.get('failed', 0)}")
            print(f"   问题总数: {result.get('total_issues', 0)}")
            
            # 显示详细结果
            if result.get('details'):
                print(f"\n📋 详细结果:")
                for detail in result['details']:
                    if detail.get('success'):
                        print(f"   ✓ {detail.get('file_name')}")
                        print(f"     - 通知书编号: {detail.get('notice_number')}")
                        print(f"     - 问题数: {detail.get('total_issues')}")
                    else:
                        print(f"   ✗ {detail.get('file_name')}")
                        print(f"     - 错误: {detail.get('error')}")
        else:
            print(f"\n❌ 导入失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    test_batch_import()

