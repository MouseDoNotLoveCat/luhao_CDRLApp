
import sys
import re

# 测试正则表达式
patterns = [
    r'^\d+[.．](.+?)施工[、,](.+?)监理的(.+?)标(.+?)[（(]检查[时日]间?[：:]\s*(.+?)[）)]',
    r'^\d+[.．](.+?)施工[、,](.+?)监理的(.+?)标(.+?)[（(]检查[时日]间\s*(.+?)[）)]',
    r'^\d+[.．](.+?)施工[、,](.+?)监理的(.+?)标(.+?)\(检查[时日]间?[：:]\s*(.+?)\)',
    r'^\d+[.．](.+?)施工[、,](.+?)监理的(.+?)标(.+?)[（(]检查[时日]间\s*(\d{4}年\d{1,2}月\d{1,2}日)[）)]'
]

test1 = '1．中铁三局施工，广西宁铁监理的QFSG1标皇马隧道出口（检查时间2025年8月7日）'
test2 = '1.中铁上海局施工、内蒙古沁原监理的HBZQ-1标李家村隧道出口（检查时间：2025年8月22日）'

print('测试文本1:', test1)
print('测试文本2:', test2)
print()

for i, pattern in enumerate(patterns):
    print(f'模式 {i+1}: {pattern}')
    match1 = re.search(pattern, test1)
    match2 = re.search(pattern, test2)
    print(f'  测试1匹配结果: {match1}')
    if match1:
        print(f'    匹配组: {match1.groups()}')
    print(f'  测试2匹配结果: {match2}')
    if match2:
        print(f'    匹配组: {match2.groups()}')
    print()

print('按优先级顺序测试:')
# 模拟函数中的逻辑
def extract_info(para):
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, para)
        if match:
            print(f'  使用模式 {i+1} 匹配成功')
            return match.groups()
    return None

result1 = extract_info(test1)
result2 = extract_info(test2)

print('最终测试1结果:', result1)
print('最终测试2结果:', result2)

