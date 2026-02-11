#!/usr/bin/env python3
"""
详细分析合湛铁路文档的所有问题
"""
import sys
sys.path.insert(0, 'backend')

from app.parsers.word_parser import parse_word_document

doc_path = "Samples/合湛铁路内部监督通知书（编号：南宁站[2026]（通知）合湛01号）-终版.docx"

print("=" * 80)
print("合湛铁路文档问题详细分析")
print("=" * 80)

result = parse_word_document(doc_path)

rectification = result.get('rectification_notices', [])
other_issues = result.get('other_issues', [])

print(f"\n下发整改通知单问题数: {len(rectification)}")
print(f"其它问题数: {len(other_issues)}")
print(f"总问题数: {len(rectification) + len(other_issues)}")

print("\n" + "=" * 80)
print("下发整改通知单问题列表")
print("=" * 80)

for idx, issue in enumerate(rectification, 1):
    section = issue.get('section_name', '未知')
    site = issue.get('site_name', '未知')
    desc = issue.get('description', '')[:60]
    print(f"\n{idx}. 标段: {section}")
    print(f"   工点: {site}")
    print(f"   描述: {desc}...")

print("\n" + "=" * 80)
print("其它问题列表（按标段分组）")
print("=" * 80)

# 按标段分组
from collections import defaultdict
issues_by_section = defaultdict(list)

for issue in other_issues:
    section = issue.get('section_name', '未知')
    issues_by_section[section].append(issue)

for section_name in sorted(issues_by_section.keys()):
    issues = issues_by_section[section_name]
    print(f"\n【{section_name}】 - {len(issues)} 个问题")
    
    for idx, issue in enumerate(issues, 1):
        site = issue.get('site_name', '未知')
        desc = issue.get('description', '')[:60]
        print(f"  {idx}. 工点: {site}")
        print(f"     描述: {desc}...")

print("\n" + "=" * 80)
print("工点名称统计")
print("=" * 80)

# 统计所有工点名称
all_sites = set()
for issue in other_issues:
    site = issue.get('site_name')
    if site:
        all_sites.add(site)

print(f"\n唯一工点数: {len(all_sites)}")
for site in sorted(all_sites):
    print(f"  - {site}")

print("\n" + "=" * 80)
print("可疑问题检查（工点名称可能被误识别为问题描述）")
print("=" * 80)

suspicious_count = 0
for idx, issue in enumerate(other_issues, 1):
    desc = issue.get('description', '')
    site = issue.get('site_name', '')
    
    # 检查描述是否像工点名称（包含"检查时间"或"检查日期"）
    if '检查时间' in desc or '检查日期' in desc:
        suspicious_count += 1
        print(f"\n⚠️  可疑问题 #{idx}:")
        print(f"   标段: {issue.get('section_name', '未知')}")
        print(f"   工点: {site}")
        print(f"   描述: {desc[:80]}...")

