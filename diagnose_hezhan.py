#!/usr/bin/env python3
"""
诊断合湛铁路文档解析问题
"""
import sys
sys.path.insert(0, 'backend')

from app.parsers.word_parser import WordParser

# 文档路径
doc_path = "Samples/合湛铁路内部监督通知书（编号：南宁站[2026]（通知）合湛01号）-终版.docx"

# 输出到文件
output_file = open('hezhan_diagnosis.txt', 'w', encoding='utf-8')

def log(msg):
    print(msg)
    output_file.write(msg + '\n')
    output_file.flush()

log("=" * 80)
log("=" * 80)
log("合湛铁路文档解析诊断")
log("=" * 80)
log(f"\n文档路径: {doc_path}\n")

# 解析文档
parser = WordParser(doc_path)
result = parser.parse()

log(f"解析状态: {result['status']}")
log(f"通知书编号: {result.get('notice_number', 'N/A')}")
log(f"项目名称: {result.get('project_name', 'N/A')}")
log(f"建设单位: {result.get('builder_unit', 'N/A')}")
log("")

# 统计问题
other_issues = result.get('other_issues', [])
rectification_issues = result.get('rectification_issues', [])

log(f"其它问题总数: {len(other_issues)}")
log(f"下发整改通知单问题数: {len(rectification_issues)}")
log(f"总问题数: {len(other_issues) + len(rectification_issues)}")
log("")

# 分析其它问题
log("=" * 80)
log("其它问题分析")
log("=" * 80)

# 按标段分组
section_groups = {}
for idx, issue in enumerate(other_issues, 1):
    section = issue.get('section_name', '未知标段')
    if section not in section_groups:
        section_groups[section] = []
    section_groups[section].append((idx, issue))

for section, issues in sorted(section_groups.items()):
    log(f"\n【{section}】- {len(issues)} 个问题")
    for idx, issue in issues[:3]:  # 只显示前3个
        contractor = issue.get('contractor', '未知')
        supervisor = issue.get('supervisor', '未知')
        site = issue.get('site_name', '未知')
        desc = issue.get('description', '')[:50]
        log(f"  问题{idx}: 施工={contractor}, 监理={supervisor}, 工点={site}")
        log(f"         描述: {desc}...")
    if len(issues) > 3:
        log(f"  ... 还有 {len(issues) - 3} 个问题")

# 分析下发整改通知单问题
log("\n" + "=" * 80)
log("下发整改通知单问题分析")
log("=" * 80)

for idx, issue in enumerate(rectification_issues, 1):
    section = issue.get('section_name', '未知标段')
    contractor = issue.get('contractor', '未知')
    supervisor = issue.get('supervisor', '未知')
    site = issue.get('site_name', '未知')
    desc = issue.get('description', '')[:80]

    log(f"\n问题{idx}:")
    log(f"  标段: {section}")
    log(f"  施工单位: {contractor}")
    log(f"  监理单位: {supervisor}")
    log(f"  工点: {site}")
    log(f"  描述: {desc}...")

# 检查重复问题
log("\n" + "=" * 80)
log("重复问题检查")
log("=" * 80)

desc_count = {}
for issue in other_issues + rectification_issues:
    desc = issue.get('description', '')[:100]
    if desc:
        desc_count[desc] = desc_count.get(desc, 0) + 1

duplicates = {desc: count for desc, count in desc_count.items() if count > 1}
if duplicates:
    log(f"\n发现 {len(duplicates)} 个重复的问题描述:")
    for desc, count in list(duplicates.items())[:5]:
        log(f"  重复{count}次: {desc}...")
else:
    log("\n未发现重复问题")

# 检查施工单位识别
log("\n" + "=" * 80)
log("施工单位识别统计")
log("=" * 80)

contractor_count = {}
for issue in other_issues + rectification_issues:
    contractor = issue.get('contractor', '未知施工单位')
    contractor_count[contractor] = contractor_count.get(contractor, 0) + 1

log("\n施工单位分布:")
for contractor, count in sorted(contractor_count.items(), key=lambda x: -x[1]):
    log(f"  {contractor}: {count} 个问题")

# 特别检查HZZQ-1标
log("\n" + "=" * 80)
log("HZZQ-1标详细分析")
log("=" * 80)

hzzq1_issues = [issue for issue in other_issues if issue.get('section_name') == 'HZZQ-1标']
log(f"\nHZZQ-1标问题数: {len(hzzq1_issues)}")

if hzzq1_issues:
    log("\n前5个问题的施工单位:")
    for idx, issue in enumerate(hzzq1_issues[:5], 1):
        contractor = issue.get('contractor', '未知')
        site = issue.get('site_name', '未知')
        desc = issue.get('description', '')[:50]
        log(f"  问题{idx}: 施工={contractor}, 工点={site}, 描述={desc}...")

log("\n" + "=" * 80)
log("诊断完成")
log("=" * 80)

output_file.close()
log("结果已保存到 hezhan_diagnosis.txt")

