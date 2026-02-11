#!/usr/bin/env python3
"""
追踪合湛铁路文档的每个段落处理过程
"""
import sys
sys.path.insert(0, 'backend')

from docx import Document
import re

# 文档路径
doc_path = "Samples/合湛铁路内部监督通知书（编号：南宁站[2026]（通知）合湛01号）-终版.docx"

print("=" * 80)
print("合湛铁路文档 - 段落级别追踪")
print("=" * 80)

# 读取文档
doc = Document(doc_path)
paragraphs = [p.text.strip() for p in doc.paragraphs]

# 模拟解析过程
in_rectification = False
issue_count = 0
current_section_code = None
current_description = None
current_requirements = None

print("\n只显示下发整改通知单部分的段落：\n")

for i, para in enumerate(paragraphs):
    if not para:
        continue
    
    # 检查是否进入下发整改通知单章节
    if '二、' in para and '下发整改通知单' in para:
        in_rectification = True
        print(f"段落 {i:3d}: [章节标题] {para}")
        continue
    
    # 检查是否进入其他章节
    if '三、' in para:
        print(f"\n段落 {i:3d}: [章节标题] {para}")
        print(">>> 停止解析下发整改通知单")
        break
    
    if in_rectification:
        # 检查各种条件
        is_level1 = re.match(r'^（[一二三四五六七八九十]）', para)
        is_check_situation = para.startswith('检查情况：')
        is_measures = para.startswith('处理措施：')
        
        print(f"\n段落 {i:3d}: {para[:80]}...")
        
        if is_level1:
            print(f"  ✓ 匹配：一级编号")
            if current_description:
                issue_count += 1
                print(f"  ⚠️  创建问题 #{issue_count}")
                print(f"      标段: {current_section_code}")
                print(f"      描述: {current_description[:50]}...")
            
            # 提取标段编号
            match = re.search(r'(HZZQ-\d+)', para)
            current_section_code = match.group(1) if match else None
            print(f"  → 设置标段: {current_section_code}")
            print(f"  → 重置 current_description = None")
            current_description = None
            current_requirements = None
        
        elif is_check_situation:
            desc = para.replace('检查情况：', '').strip()
            print(f"  ✓ 匹配：检查情况")
            print(f"  → 设置 current_description = '{desc[:50]}...'")
            current_description = desc
        
        elif is_measures:
            measures = para.replace('处理措施：', '').strip()
            print(f"  ✓ 匹配：处理措施")
            print(f"  → 设置 current_requirements = '{measures[:50]}...'")
            current_requirements = measures
            
            if current_description:
                issue_count += 1
                print(f"  ⚠️  创建问题 #{issue_count}")
                print(f"      标段: {current_section_code}")
                print(f"      描述: {current_description[:50]}...")
                print(f"  → 重置 current_description = None")
                current_description = None
                current_requirements = None
            else:
                print(f"  ⚠️  current_description 为空，不创建问题")
        
        else:
            print(f"  ✗ 不匹配任何条件")

# 循环结束后
if current_description:
    issue_count += 1
    print(f"\n⚠️  循环结束后创建问题 #{issue_count}")
    print(f"    标段: {current_section_code}")
    print(f"    描述: {current_description[:50]}...")

print("\n" + "=" * 80)
print(f"模拟解析：总共创建了 {issue_count} 个问题")
print("=" * 80)

# 实际解析
print("\n" + "=" * 80)
print("实际解析结果对比")
print("=" * 80)

from app.parsers.word_parser import WordDocumentParser
parser = WordDocumentParser(doc_path)
result = parser.parse()
rectification_issues = result.get('rectification_notices', [])

print(f"\n实际识别的下发整改通知单问题数: {len(rectification_issues)}")

for idx, issue in enumerate(rectification_issues, 1):
    section = issue.get('section_name', '未知')
    contractor = issue.get('contractor', '未知')
    desc = issue.get('description', '')[:60]
    print(f"\n问题 {idx}:")
    print(f"  标段: {section}")
    print(f"  施工单位: {contractor}")
    print(f"  描述: {desc}...")

