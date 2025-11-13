#!/usr/bin/env python3
"""
项目与标段管理 API 测试脚本
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

def print_header(title):
    """打印标题"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def print_result(title, data):
    """打印结果"""
    print(f"✅ {title}:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print()

def test_projects_api():
    """测试项目 API"""
    print_header("测试项目 API")
    
    # 1. 获取项目列表
    print("1️⃣  获取项目列表...")
    response = requests.get(f"{BASE_URL}/projects")
    projects = response.json()
    print_result("项目列表", projects)
    
    # 2. 创建新项目
    print("2️⃣  创建新项目...")
    response = requests.post(
        f"{BASE_URL}/projects",
        params={
            "project_name": f"测试项目_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "builder_unit": "测试建设单位"
        }
    )
    new_project = response.json()
    print_result("新建项目", new_project)
    project_id = new_project['id']
    
    # 3. 获取单个项目
    print("3️⃣  获取单个项目...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}")
    project = response.json()
    print_result("项目详情", project)
    
    # 4. 修改项目
    print("4️⃣  修改项目...")
    response = requests.put(
        f"{BASE_URL}/projects/{project_id}",
        params={
            "project_name": f"修改后的项目_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "builder_unit": "修改后的建设单位"
        }
    )
    updated_project = response.json()
    print_result("修改后的项目", updated_project)
    
    return project_id

def test_sections_api(project_id):
    """测试标段 API"""
    print_header("测试标段 API")
    
    # 1. 获取标段列表
    print("1️⃣  获取标段列表...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}/sections")
    sections = response.json()
    print_result("标段列表", sections)
    
    # 2. 创建新标段
    print("2️⃣  创建新标段...")
    response = requests.post(
        f"{BASE_URL}/sections",
        params={
            "project_id": project_id,
            "section_code": f"TEST-{datetime.now().strftime('%H%M%S')}",
            "section_name": "测试标段",
            "contractor_unit": "测试施工单位",
            "supervisor_unit": "测试监理单位",
            "designer_unit": "测试设计单位",
            "testing_unit": "测试检测单位"
        }
    )
    new_section = response.json()
    print_result("新建标段", new_section)
    section_id = new_section['id']
    
    # 3. 获取单个标段
    print("3️⃣  获取单个标段...")
    response = requests.get(f"{BASE_URL}/sections/{section_id}")
    section = response.json()
    print_result("标段详情", section)
    
    # 4. 修改标段
    print("4️⃣  修改标段...")
    response = requests.put(
        f"{BASE_URL}/sections/{section_id}",
        params={
            "section_code": f"MODIFIED-{datetime.now().strftime('%H%M%S')}",
            "section_name": "修改后的标段",
            "contractor_unit": "修改后的施工单位",
            "supervisor_unit": "修改后的监理单位",
            "designer_unit": "修改后的设计单位",
            "testing_unit": "修改后的检测单位"
        }
    )
    updated_section = response.json()
    print_result("修改后的标段", updated_section)
    
    # 5. 获取更新后的标段列表
    print("5️⃣  获取更新后的标段列表...")
    response = requests.get(f"{BASE_URL}/projects/{project_id}/sections")
    sections = response.json()
    print_result("更新后的标段列表", sections)
    
    return section_id

def test_delete_apis(project_id, section_id):
    """测试删除 API"""
    print_header("测试删除 API")
    
    # 1. 删除标段
    print("1️⃣  删除标段...")
    response = requests.delete(f"{BASE_URL}/sections/{section_id}")
    result = response.json()
    print_result("删除标段结果", result)
    
    # 2. 删除项目
    print("2️⃣  删除项目...")
    response = requests.delete(f"{BASE_URL}/projects/{project_id}", params={"cascade": True})
    result = response.json()
    print_result("删除项目结果", result)

def test_search_api():
    """测试搜索功能"""
    print_header("测试搜索功能")
    
    # 1. 搜索项目
    print("1️⃣  搜索项目（关键词：黄百）...")
    response = requests.get(f"{BASE_URL}/projects", params={"search": "黄百"})
    projects = response.json()
    print_result("搜索结果", projects)
    
    # 2. 搜索标段
    if projects['data']:
        project_id = projects['data'][0]['id']
        print(f"2️⃣  搜索标段（项目ID：{project_id}）...")
        response = requests.get(f"{BASE_URL}/projects/{project_id}/sections", params={"search": "QFSG"})
        sections = response.json()
        print_result("搜索结果", sections)

def main():
    """主函数"""
    print("\n" + "="*60)
    print("  项目与标段管理 API 测试")
    print("="*60)
    
    try:
        # 测试项目 API
        project_id = test_projects_api()
        
        # 测试标段 API
        section_id = test_sections_api(project_id)
        
        # 测试删除 API
        test_delete_apis(project_id, section_id)
        
        # 测试搜索功能
        test_search_api()
        
        print("\n" + "="*60)
        print("  ✅ 所有测试完成！")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}\n")

if __name__ == "__main__":
    main()

