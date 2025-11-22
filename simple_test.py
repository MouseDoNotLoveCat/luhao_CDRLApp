# -*- coding: utf-8 -*-
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.parsers.word_parser import WordParser

def test_cross_line_parsing():
    """测试跨行格式解析"""
    print("=== 测试跨行格式解析 ===")
    
    # 失败示例（当前识别不到标段编号，但能识别工点名称）
    text = """三、其他主要质量安全问题
（一）中铁五局施工、中铁路安监理的YCZQ-4标
1、路基DK262+635.41～DK263+079.5段（检查时间2025年7月23日）
存在问题描述"""
    
    parser = WordParser(text)
    issues = parser.extract_other_issues()
    
    print("输入文本:")
    print(text)
    print("\n提取结果:")
    
    if issues:
        for i, issue in enumerate(issues):
            print("问题 " + str(i+1) + ":")
            print("  标段编号: " + str(issue.get('section_code', 'None')))
            print("  工点名称: " + str(issue.get('site_name', 'None')))
            print("  检查时间: " + str(issue.get('inspection_date', 'None')))
            print("  施工单位: " + str(issue.get('contractor', 'None')))
            print("  监理单位: " + str(issue.get('supervisor', 'None')))
    else:
        print("未提取到任何问题")
    
    print("\n期望结果:")
    print("  标段编号: YCZQ-4")
    print("  工点名称: 路基DK262+635.41～DK263+079.5段")
    print("  检查时间: 2025-07-23")

def test_single_line_parsing():
    """测试单行格式解析"""
    print("\n=== 测试单行格式解析 ===")
    
    # 成功示例（基准对照）
    text = """三、其他主要质量安全问题
（一）由中建八局施工、甘肃铁科监理的LWZQ-8标（检查日期：2025年5月20日）
1.双峰隧道进口
存在问题描述"""
    
    parser = WordParser(text)
    issues = parser.extract_other_issues()
    
    print("输入文本:")
    print(text)
    print("\n提取结果:")
    
    if issues:
        for i, issue in enumerate(issues):
            print("问题 " + str(i+1) + ":")
            print("  标段编号: " + str(issue.get('section_code', 'None')))
            print("  工点名称: " + str(issue.get('site_name', 'None')))
            print("  检查时间: " + str(issue.get('inspection_date', 'None')))
            print("  施工单位: " + str(issue.get('contractor', 'None')))
            print("  监理单位: " + str(issue.get('supervisor', 'None')))
    else:
        print("未提取到任何问题")
    
    print("\n期望结果:")
    print("  标段编号: LWZQ-8")
    print("  工点名称: 双峰隧道进口")
    print("  检查时间: 2025-05-20")

if __name__ == "__main__":
    test_cross_line_parsing()
    test_single_line_parsing()
