#!/usr/bin/env python3
"""
详细诊断合湛铁路文档的下发整改通知单解析过程
"""
import sys
sys.path.insert(0, 'backend')

from app.parsers.word_parser import WordDocumentParser
import re

# 文档路径
doc_path = "Samples/合湛铁路内部监督通知书（编号：南宁站[2026]（通知）合湛01号）-终版.docx"

print("=" * 80)
print("合湛铁路文档 - 下发整改通知单解析详细诊断")
print("=" * 80)

# 创建解析器
parser = WordDocumentParser(doc_path)

# 检测文档格式
doc_format = parser._detect_document_format()
print(f"\n文档格式: {doc_format}")

# 手动模拟解析过程
in_rectification = False
issue_count = 0
current_section_code = None
current_description = None

print("\n" + "=" * 80)
print("段落解析过程（只显示下发整改通知单部分）")
print("=" * 80)

for i, para in enumerate(parser.paragraphs):
    para_text = para.strip()
    if not para_text:
        continue
    
    # 检查是否进入下发整改通知单章节
    if '二、' in para_text and '下发整改通知单' in para_text:
        in_rectification = True
        print(f"\n>>> 进入下发整改通知单章节（段落 {i}）")
        continue
    
    # 检查是否进入其他章节
    if '三、' in para_text:
        print(f"\n>>> 进入其他章节（段落 {i}），停止解析下发整改通知单")
        break
    
    if in_rectification:
        # 检查是否是一级编号
        if re.match(r'^（[一二三四五六七八九十]）', para_text):
            if current_description:
                issue_count += 1
                print(f"\n  ⚠️  创建问题 #{issue_count}（遇到新的一级编号）")
                print(f"      描述: {current_description[:50]}...")
            
            # 提取标段编号
            match = re.search(r'(HZZQ-\d+)', para_text)
            current_section_code = match.group(1) if match else None
            
            print(f"\n段落 {i}: [一级编号] {para_text[:80]}...")
            print(f"  → 标段: {current_section_code}")
            
            current_description = None
        
        # 检查是否是"检查情况："
        elif para_text.startswith('检查情况：'):
            desc = para_text.replace('检查情况：', '').strip()
            current_description = desc
            print(f"\n段落 {i}: [检查情况] {desc[:60]}...")
            print(f"  → 设置 current_description")
        
        # 检查是否是"处理措施："
        elif para_text.startswith('处理措施：'):
            measures = para_text.replace('处理措施：', '').strip()
            print(f"\n段落 {i}: [处理措施] {measures[:60]}...")
            
            if current_description:
                issue_count += 1
                print(f"  ⚠️  创建问题 #{issue_count}（遇到处理措施）")
                print(f"      标段: {current_section_code}")
                print(f"      描述: {current_description[:50]}...")
                print(f"  → 重置 current_description = None")
                current_description = None
            else:
                print(f"  → current_description 为空，不创建问题")
        
        # 其他段落
        else:
            # 检查是否会被误识别为问题描述
            if doc_format == 'format2' and current_description is None:
                if (not para_text.startswith('处理措施：') and
                    not para_text.startswith('检查情况：') and
                    not re.match(r'^图\d+', para_text)):
                    print(f"\n段落 {i}: [可能被误识别] {para_text[:60]}...")
                    print(f"  ⚠️  可能设置 current_description（黄百格式兜底逻辑）")

# 循环结束后
if current_description:
    issue_count += 1
    print(f"\n  ⚠️  创建问题 #{issue_count}（循环结束后）")
    print(f"      描述: {current_description[:50]}...")

print("\n" + "=" * 80)
print(f"总共创建了 {issue_count} 个问题")
print("=" * 80)

# 实际解析结果
print("\n" + "=" * 80)
print("实际解析结果")
print("=" * 80)

result = parser.parse()
rectification_issues = result.get('rectification_notices', [])

print(f"\n下发整改通知单问题数: {len(rectification_issues)}")

for idx, issue in enumerate(rectification_issues, 1):
    section = issue.get('section_name', '未知')
    contractor = issue.get('contractor', '未知')
    desc = issue.get('description', '')[:80]
    print(f"\n问题 {idx}:")
    print(f"  标段: {section}")
    print(f"  施工单位: {contractor}")
    print(f"  描述: {desc}...")

print("\n" + "=" * 80)
print("诊断完成")
print("=" * 80)

