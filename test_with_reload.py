import sys
import os
import importlib

# 清除已导入的模块
if 'app.parsers.word_parser' in sys.modules:
    del sys.modules['app.parsers.word_parser']
if 'app.parsers' in sys.modules:
    del sys.modules['app.parsers']
if 'app' in sys.modules:
    del sys.modules['app']

sys.path.insert(0, 'backend')

# 设置输出文件
output_file = 'parser_test_result_new.txt'

try:
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('='*80 + '\n')
        f.write('Word 文档解析器测试 (强制重新加载)\n')
        f.write('='*80 + '\n\n')
        
        # 重新导入模块
        from app.parsers.word_parser import WordDocumentParser
        
        file_path = 'Samples/玉岑内部监督通知书（编号：南宁站〔2026〕（通知）玉岑1号）(1).docx'
        
        if not os.path.exists(file_path):
            f.write(f'错误：文件不存在 - {file_path}\n')
            sys.exit(1)
        
        f.write(f'测试文件: {file_path}\n')
        f.write('开始解析...\n\n')
        
        parser = WordDocumentParser(file_path)
        result = parser.parse()
        
        f.write(f'解析状态: {result.get("status")}\n')
        f.write(f'通知书编号: {result.get("notice_number", "N/A")}\n\n')
        
        other = result.get('other_issues', [])
        f.write(f'其它问题总数: {len(other)}\n')
        f.write('='*80 + '\n\n')
        
        # 查找 YCZQ-1 标段的问题
        f.write('查找 YCZQ-1 标段的问题:\n')
        f.write('-'*80 + '\n')
        
        yczq1_issues = [issue for issue in other if 'YCZQ-1' in issue.get('section_code', '')]
        f.write(f'找到 {len(yczq1_issues)} 个 YCZQ-1 标段的问题\n\n')
        
        # 显示前10个 YCZQ-1 标段的问题
        for i, issue in enumerate(yczq1_issues[:10], 1):
            f.write(f'问题 {i}:\n')
            f.write(f'  标段: {issue.get("section_name", "N/A")}\n')
            f.write(f'  工点: {issue.get("site_name", "N/A")}\n')
            f.write(f'  施工单位: {issue.get("contractor", "N/A")}\n')
            f.write(f'  监理单位: {issue.get("supervisor", "N/A")}\n')
            desc = issue.get('description', '')
            if len(desc) > 80:
                desc = desc[:77] + '...'
            f.write(f'  问题描述: {desc}\n')
            f.write('-'*80 + '\n')
        
        # 检查异常识别
        f.write('\n检查异常识别:\n')
        f.write('='*80 + '\n')
        
        found_count = 0
        for i, issue in enumerate(other, 1):
            contractor = issue.get('contractor', '')
            if '安全防护' in contractor or '佩戴' in contractor or '警示' in contractor:
                found_count += 1
                f.write(f'\n❌ 发现异常识别 - 问题 {i}:\n')
                f.write(f'  标段: {issue.get("section_name", "N/A")}\n')
                f.write(f'  工点: {issue.get("site_name", "N/A")}\n')
                f.write(f'  施工单位: {contractor}\n')
                f.write(f'  监理单位: {issue.get("supervisor", "N/A")}\n')
                f.write(f'  问题描述: {issue.get("description", "N/A")[:100]}\n')
                f.write('-'*80 + '\n')
        
        if found_count == 0:
            f.write('\n✅ 未发现异常识别，修复成功！\n')
        else:
            f.write(f'\n❌ 发现 {found_count} 个异常识别\n')
        
        f.write('\n测试完成！\n')
        
    print(f'测试完成，结果已保存到: {output_file}')
    
except Exception as e:
    with open(output_file, 'a', encoding='utf-8') as f:
        f.write(f'\n\n错误: {e}\n')
        import traceback
        f.write(traceback.format_exc())
    print(f'测试出错，错误信息已保存到: {output_file}')

