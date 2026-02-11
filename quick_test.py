import sys
import traceback
sys.path.insert(0, 'backend')

try:
    from app.parsers.word_parser import WordDocumentParser

    file_path = 'Samples/玉岑内部监督通知书（编号：南宁站〔2026〕（通知）玉岑1号）(1).docx'
    print('开始解析文件...')
    print(f'文件路径: {file_path}')

    parser = WordDocumentParser(file_path)
    print('解析器创建成功，开始解析...')

    result = parser.parse()
    print('解析完成！')

    other = result.get('other_issues', [])
    print(f'其它问题总数: {len(other)}')

    # 检查异常识别
    found_count = 0
    for i, issue in enumerate(other, 1):
        contractor = issue.get('contractor', '')
        if '安全防护' in contractor or '佩戴' in contractor or '警示' in contractor:
            found_count += 1
            print(f'问题{i}: 施工单位={contractor}')
            print(f'       问题描述={issue.get("description", "")[:60]}')

    if found_count == 0:
        print('✅ 修复成功！未发现异常识别')
    else:
        print(f'❌ 仍存在{found_count}个异常识别')

except Exception as e:
    print(f'错误: {e}')
    traceback.print_exc()

