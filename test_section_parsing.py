#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
验证标段编号、工点名称、检查时间解析功能的测试用例
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.parsers.word_parser import WordParser

def test_case_a():
    """用例A（对照 - 必须保持兼容）"""
    print("=== 用例A（对照） ===")
    text = "（一）由中建八局施工、甘肃铁科监理的LWZQ-8标（检查日期：2025年5月20日）\n1.双峰隧道进口"
    
    parser = WordParser(text)
    issues = parser.extract_other_issues()
    
    expected = {
        'section_code': 'LWZQ-8',
        'site_name': '双峰隧道进口', 
        'check_date': '2025-05-20'
    }
    
    print("输入: " + text)
    print("期望: " + str(expected))
    
    if issues:
        actual = {
            'section_code': issues[0].get('section_code'),
            'site_name': issues[0].get('site_name'),
            'check_date': issues[0].get('inspection_date')
        }
        print("实际: " + str(actual))

        success = (actual['section_code'] == expected['section_code'] and
                  actual['site_name'] == expected['site_name'] and
                  actual['check_date'] == expected['check_date'])
        print("结果: " + ("✓ 通过" if success else "✗ 失败"))
    else:
        print("实际: 未提取到任何信息")
        print("结果: ✗ 失败")
    print()

def test_case_b():
    """用例B（失败修复 - 跨行格式）"""
    print("=== 用例B（失败修复） ===")
    text = "（一）中铁五局施工、中铁路安监理的YCZQ-4标\n1、路基DK262+635.41～DK263+079.5段（检查时间2025年7月23日）"
    
    parser = WordParser(text)
    issues = parser.extract_other_issues()
    
    expected = {
        'section_code': 'YCZQ-4',
        'site_name': '路基DK262+635.41～DK263+079.5段',
        'check_date': '2025-07-23'
    }
    
    print(f"输入: {text}")
    print(f"期望: {expected}")
    
    if issues:
        actual = {
            'section_code': issues[0].get('section_code'),
            'site_name': issues[0].get('site_name'),
            'check_date': issues[0].get('inspection_date')
        }
        print(f"实际: {actual}")
        
        success = (actual['section_code'] == expected['section_code'] and
                  actual['site_name'] == expected['site_name'] and
                  actual['check_date'] == expected['check_date'])
        print(f"结果: {'✓ 通过' if success else '✗ 失败'}")
    else:
        print("实际: 未提取到任何信息")
        print("结果: ✗ 失败")
    print()

def test_case_c():
    """用例C（顺序变体B - 单位+标段+施工/监理）"""
    print("=== 用例C（顺序变体B） ===")
    text = "1.中铁五局YCZQ-4标施工、中铁路安YCJL-2标监理的DK262+635.41～DK263+079.5段路基工程（检查时间：2025年7月23日）"
    
    parser = WordParser(text)
    issues = parser.extract_rectification_notices()
    
    expected = {
        'section_code': 'YCZQ-4',
        'site_name': 'DK262+635.41～DK263+079.5段路基工程',
        'check_date': '2025-07-23'
    }
    
    print(f"输入: {text}")
    print(f"期望: {expected}")
    
    if issues:
        actual = {
            'section_code': issues[0].get('section_code'),
            'site_name': issues[0].get('site_name'),
            'check_date': issues[0].get('inspection_date')
        }
        print(f"实际: {actual}")
        
        success = (actual['section_code'] == expected['section_code'] and
                  actual['site_name'] == expected['site_name'] and
                  actual['check_date'] == expected['check_date'])
        print(f"结果: {'✓ 通过' if success else '✗ 失败'}")
    else:
        print("实际: 未提取到任何信息")
        print("结果: ✗ 失败")
    print()

def test_case_d():
    """用例D（标点变体 - 全角点+逗号+无冒号）"""
    print("=== 用例D（标点变体） ===")
    text = "1．中铁三局施工，广西宁铁监理的QFSG1标皇马隧道出口（检查时间2025年8月7日）"
    
    parser = WordParser(text)
    issues = parser.extract_rectification_notices()
    
    expected = {
        'section_code': 'QFSG1',
        'site_name': '皇马隧道出口',
        'check_date': '2025-08-07'
    }
    
    print(f"输入: {text}")
    print(f"期望: {expected}")
    
    if issues:
        actual = {
            'section_code': issues[0].get('section_code'),
            'site_name': issues[0].get('site_name'),
            'check_date': issues[0].get('inspection_date')
        }
        print(f"实际: {actual}")
        
        success = (actual['section_code'] == expected['section_code'] and
                  actual['site_name'] == expected['site_name'] and
                  actual['check_date'] == expected['check_date'])
        print(f"结果: {'✓ 通过' if success else '✗ 失败'}")
    else:
        print("实际: 未提取到任何信息")
        print("结果: ✗ 失败")
    print()

if __name__ == "__main__":
    print("标段编号、工点名称、检查时间解析验证测试")
    print("=" * 50)
    
    test_case_a()
    test_case_b() 
    test_case_c()
    test_case_d()
    
    print("测试完成")
