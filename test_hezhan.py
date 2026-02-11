#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

try:
    from app.parsers.word_parser import WordParser
    
    doc_path = "Samples/合湛铁路内部监督通知书（编号：南宁站[2026]（通知）合湛01号）-终版.docx"
    
    with open('hezhan_diagnosis.txt', 'w', encoding='utf-8') as f:
        f.write("开始解析...\n")
        f.flush()
        
        parser = WordParser(doc_path)
        result = parser.parse()
        
        f.write(f"解析状态: {result['status']}\n")
        f.write(f"其它问题数: {len(result.get('other_issues', []))}\n")
        f.write(f"整改通知单问题数: {len(result.get('rectification_issues', []))}\n")
        f.write(f"总问题数: {len(result.get('other_issues', [])) + len(result.get('rectification_issues', []))}\n")
        
    print("诊断完成，结果已保存到 hezhan_diagnosis.txt")
    
except Exception as e:
    with open('hezhan_diagnosis.txt', 'w', encoding='utf-8') as f:
        f.write(f"错误: {str(e)}\n")
        import traceback
        f.write(traceback.format_exc())
    print(f"发生错误: {e}")

