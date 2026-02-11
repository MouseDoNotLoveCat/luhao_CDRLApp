#!/usr/bin/env python3
"""
检查合湛铁路文档的结构类型和段落内容
"""
import sys
sys.path.insert(0, 'backend')

from app.parsers.word_parser import WordDocumentParser

doc_path = "Samples/合湛铁路内部监督通知书（编号：南宁站[2026]（通知）合湛01号）-终版.docx"

parser = WordDocumentParser(doc_path)
parser.doc = parser.doc or __import__('docx').Document(str(parser.file_path))
parser._extract_paragraphs()

# 检测文档结构
structure = parser._detect_document_structure()

print("=" * 80)
print(f"文档结构类型: {structure}")
print("=" * 80)

# 查找"三、其它问题"章节的段落
in_other = False
other_paras = []

for idx, para in enumerate(parser.paragraphs):
    section = parser._identify_section(para)
    if section == 'other':
        in_other = True
        print(f"\n找到'其它问题'章节，从第 {idx+1} 行开始")
        continue
    
    if in_other:
        # 检查是否结束
        if '三、' in para and ('有关要求' in para or '监督意见' in para):
            print(f"\n'其它问题'章节结束于第 {idx+1} 行")
            break
        if '四、' in para or '监督意见' in para:
            print(f"\n'其它问题'章节结束于第 {idx+1} 行")
            break
        
        other_paras.append((idx+1, para))

print(f"\n'其它问题'章节共 {len(other_paras)} 个段落")

# 显示前50个段落
print("\n" + "=" * 80)
print("前50个段落内容")
print("=" * 80)

for line_num, para in other_paras[:50]:
    # 检查段落类型
    para_type = "普通段落"
    
    if para.startswith('（一）') or para.startswith('（二）') or para.startswith('（三）') or para.startswith('（四）'):
        if '施工' in para and '监理' in para:
            para_type = "【标段行】"
    elif para.startswith('1.') or para.startswith('2.') or para.startswith('3.'):
        if '（检查时间' in para or '（检查日期' in para:
            para_type = "【工点行】"
        else:
            para_type = "【数字编号】"
    elif para.startswith('（1）') or para.startswith('（2）') or para.startswith('（3）'):
        para_type = "【问题编号】"
    elif para.startswith('检查情况：'):
        para_type = "【检查情况】"
    elif para.startswith('处理措施：'):
        para_type = "【处理措施】"
    
    print(f"\n第{line_num}行 {para_type}:")
    print(f"  {para[:100]}{'...' if len(para) > 100 else ''}")

