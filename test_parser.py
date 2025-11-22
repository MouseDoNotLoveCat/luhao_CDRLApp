
import sys
sys.path.append('backend')
from app.parsers.word_parser import WordDocumentParser

# 创建一个实例来测试修改后的函数
parser = WordDocumentParser('backend/app/parsers/word_parser.py')

# 测试第一个例子：'1．中铁三局施工，广西宁铁监理的QFSG1标皇马隧道出口（检查时间2025年8月7日）'
test1 = '1．中铁三局施工，广西宁铁监理的QFSG1标皇马隧道出口（检查时间2025年8月7日）'
result1 = parser._extract_info_from_numbered_line(test1)
print('测试1结果:', result1)

# 测试第二个例子：'1.中铁上海局施工、内蒙古沁原监理的HBZQ-1标李家村隧道出口（检查时间：2025年8月22日）'
test2 = '1.中铁上海局施工、内蒙古沁原监理的HBZQ-1标李家村隧道出口（检查时间：2025年8月22日）'
result2 = parser._extract_info_from_numbered_line(test2)
print('测试2结果:', result2)

