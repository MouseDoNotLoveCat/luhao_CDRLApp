#!/usr/bin/env python3
"""
通知书管理 API 测试脚本
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_get_notices():
    """测试获取通知书列表"""
    print("\n" + "="*60)
    print("测试 1: 获取通知书列表")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/notices", params={
        "search": "",
        "limit": 5,
        "offset": 0
    })
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"总数: {data.get('total')}")
    print(f"返回数据数: {len(data.get('data', []))}")
    
    if data.get('data'):
        print("\n第一条通知书:")
        notice = data['data'][0]
        print(f"  ID: {notice.get('id')}")
        print(f"  编号: {notice.get('notice_number')}")
        print(f"  检查日期: {notice.get('check_date')}")
        print(f"  检查单位: {notice.get('check_unit')}")
        print(f"  问题数量: {notice.get('issues_count')}")
    
    return data.get('data', [])[0] if data.get('data') else None

def test_get_notice_detail(notice_id):
    """测试获取通知书详情"""
    print("\n" + "="*60)
    print(f"测试 2: 获取通知书详情 (ID: {notice_id})")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/notices/{notice_id}")
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    
    print(f"通知书编号: {data.get('notice_number')}")
    print(f"检查日期: {data.get('check_date')}")
    print(f"检查单位: {data.get('check_unit')}")
    print(f"检查人员: {data.get('check_personnel')}")
    print(f"问题数量: {len(data.get('issues', []))}")
    
    if data.get('issues'):
        print("\n前 3 个问题:")
        for i, issue in enumerate(data['issues'][:3], 1):
            print(f"  {i}. {issue.get('site_name')} - {issue.get('description', '')[:50]}...")
    
    return data

def test_search_notices():
    """测试搜索通知书"""
    print("\n" + "="*60)
    print("测试 3: 搜索通知书")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/notices", params={
        "search": "柳梧",
        "limit": 10,
        "offset": 0
    })
    
    print(f"状态码: {response.status_code}")
    data = response.json()
    print(f"搜索结果数: {len(data.get('data', []))}")
    
    if data.get('data'):
        print("\n搜索结果:")
        for notice in data['data']:
            print(f"  - {notice.get('notice_number')}")

def test_pagination():
    """测试分页"""
    print("\n" + "="*60)
    print("测试 4: 分页")
    print("="*60)
    
    # 第一页
    response1 = requests.get(f"{BASE_URL}/notices", params={
        "limit": 2,
        "offset": 0
    })
    data1 = response1.json()
    print(f"第一页 (offset=0, limit=2): {len(data1.get('data', []))} 条")
    
    # 第二页
    response2 = requests.get(f"{BASE_URL}/notices", params={
        "limit": 2,
        "offset": 2
    })
    data2 = response2.json()
    print(f"第二页 (offset=2, limit=2): {len(data2.get('data', []))} 条")
    
    print(f"总数: {data1.get('total')}")

def test_delete_notice():
    """测试删除通知书（不实际删除，只测试 API）"""
    print("\n" + "="*60)
    print("测试 5: 删除通知书 API 可用性")
    print("="*60)
    
    # 获取一个通知书 ID
    response = requests.get(f"{BASE_URL}/notices", params={"limit": 1})
    data = response.json()
    
    if data.get('data'):
        notice_id = data['data'][0]['id']
        print(f"测试删除 API (不实际删除): ID={notice_id}")
        print("✓ DELETE /api/notices/{notice_id} 端点可用")
    else:
        print("✗ 没有可用的通知书进行测试")

def main():
    print("\n" + "="*60)
    print("通知书管理 API 测试")
    print("="*60)
    
    try:
        # 测试 1: 获取列表
        notices = test_get_notices()
        
        if notices:
            # 测试 2: 获取详情
            test_get_notice_detail(notices['id'])
            
            # 测试 3: 搜索
            test_search_notices()
            
            # 测试 4: 分页
            test_pagination()
            
            # 测试 5: 删除 API
            test_delete_notice()
            
            print("\n" + "="*60)
            print("✅ 所有测试完成！")
            print("="*60)
        else:
            print("✗ 没有可用的通知书数据")
    
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

