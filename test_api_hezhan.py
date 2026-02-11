#!/usr/bin/env python3
"""
直接测试后端API的识别结果
"""
import requests
import json

# 上传文件并识别
doc_path = "Samples/合湛铁路内部监督通知书（编号：南宁站[2026]（通知）合湛01号）-终版.docx"

print("=" * 80)
print("测试后端API识别结果")
print("=" * 80)

# 上传文件
with open(doc_path, 'rb') as f:
    files = {'file': (doc_path.split('/')[-1], f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
    response = requests.post('http://localhost:8000/api/import/upload', files=files)

if response.status_code == 200:
    result = response.json()
    
    print(f"\n状态: {result.get('status')}")
    print(f"通知书编号: {result.get('notice_number')}")
    print(f"项目名称: {result.get('project_name')}")
    
    rectification_notices = result.get('rectification_notices', [])
    other_issues = result.get('other_issues', [])
    
    print(f"\n下发整改通知单问题数: {len(rectification_notices)}")
    print(f"其他问题数: {len(other_issues)}")
    print(f"总问题数: {len(rectification_notices) + len(other_issues)}")
    
    print("\n" + "=" * 80)
    print("下发整改通知单问题详情")
    print("=" * 80)
    
    for idx, issue in enumerate(rectification_notices, 1):
        section = issue.get('section_name', '未知')
        contractor = issue.get('contractor', '未知')
        desc = issue.get('description', '')[:80]
        
        print(f"\n问题 {idx}:")
        print(f"  标段: {section}")
        print(f"  施工单位: {contractor}")
        print(f"  描述: {desc}...")
    
    # 检查是否有重复
    print("\n" + "=" * 80)
    print("重复检查")
    print("=" * 80)
    
    desc_list = [issue.get('description', '')[:100] for issue in rectification_notices]
    unique_desc = set(desc_list)
    
    if len(desc_list) != len(unique_desc):
        print(f"\n⚠️  发现重复！")
        print(f"  总问题数: {len(desc_list)}")
        print(f"  唯一问题数: {len(unique_desc)}")
        
        # 找出重复的问题
        from collections import Counter
        counter = Counter(desc_list)
        for desc, count in counter.items():
            if count > 1:
                print(f"\n  重复 {count} 次: {desc}...")
    else:
        print(f"\n✓ 没有重复问题")
        print(f"  总问题数: {len(desc_list)}")
        print(f"  唯一问题数: {len(unique_desc)}")

else:
    print(f"\n错误: {response.status_code}")
    print(response.text)

