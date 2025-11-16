#!/usr/bin/env python3
"""
测试导入功能的脚本
"""
import requests
import json
import time

# API 基础 URL
BASE_URL = "http://localhost:8000"

# 测试文件路径
TEST_FILE = "/Users/haolu/Library/CloudStorage/OneDrive-个人/进行中的工作/工程监督/AppDev/CDRLApp/Samples/黄百铁路内部监督通知书2025-08号.docx"

def test_recognize():
    """测试识别功能"""
    print("\n" + "="*80)
    print("测试 1: 识别文档")
    print("="*80)
    
    with open(TEST_FILE, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{BASE_URL}/api/import/recognize", files=files)
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result.get('success'):
        return result
    else:
        print("❌ 识别失败")
        return None

def test_import_selected(notice_data, selected_issue_ids):
    """测试导入选中的问题"""
    print("\n" + "="*80)
    print("测试 2: 导入选中的问题")
    print("="*80)
    print(f"选中的问题 ID: {selected_issue_ids}")
    
    payload = {
        "notice_data": notice_data,
        "selected_issue_ids": selected_issue_ids
    }
    
    response = requests.post(f"{BASE_URL}/api/import/selected", json=payload)
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    return result

if __name__ == "__main__":
    # 第一步：识别文档
    recognize_result = test_recognize()
    
    if recognize_result:
        # 第二步：导入选中的问题（选择前 5 个）
        issues = recognize_result.get('issues', [])
        selected_ids = [issue['id'] for issue in issues[:5]]
        
        print(f"\n选择前 5 个问题进行导入: {selected_ids}")
        
        import_result = test_import_selected(recognize_result, selected_ids)
        
        print("\n" + "="*80)
        print("导入完成")
        print("="*80)
        print(f"成功导入: {import_result.get('imported_issues_count', 0)} 个")
        print(f"导入失败: {import_result.get('failed_issues_count', 0)} 个")
        if import_result.get('failed_issues'):
            print(f"失败的问题: {import_result.get('failed_issues')}")

