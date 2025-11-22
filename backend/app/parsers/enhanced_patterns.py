"""
增强的正则表达式模式，用于提取标段编号、工点名称和检查时间
支持多种格式变体和标点符号
"""

import re
from typing import Tuple, Optional

# 单行模式 - 带"由"字版本 - 全角括号
PATTERN_WITH_BY_FULL_BRACKET = r'^\d+[\.．、]\s*由(.+?)施工[、，]\s*(.+?)监理的([A-Z]{2,}[A-Z0-9]*(?:-?\d+)?)(?=标)标(.+?)（检查(?:时间|日期)[：:]?\s*(.+?)）'

# 单行模式 - 带"由"字版本 - 半角括号
PATTERN_WITH_BY_HALF_BRACKET = r'^\d+[\.．、]\s*由(.+?)施工[、，]\s*(.+?)监理的([A-Z]{2,}[A-Z0-9]*(?:-?\d+)?)(?=标)标(.+?)\(检查(?:时间|日期)[：:]?\s*(.+?)\)'

# 单行模式 - 无"由"字版本 - 全角括号
PATTERN_WITHOUT_BY_FULL_BRACKET = r'^\d+[\.．、]\s*(.+?)施工[、，]\s*(.+?)监理的([A-Z]{2,}[A-Z0-9]*(?:-?\d+)?)(?=标)标(.+?)（检查(?:时间|日期)[：:]?\s*(.+?)）'

# 单行模式 - 无"由"字版本 - 半角括号
PATTERN_WITHOUT_BY_HALF_BRACKET = r'^\d+[\.．、]\s*(.+?)施工[、，]\s*(.+?)监理的([A-Z]{2,}[A-Z0-9]*(?:-?\d+)?)(?=标)标(.+?)\(检查(?:时间|日期)[：:]?\s*(.+?)\)'

# 单行模式 - 单位+标段+施工/监理 - 全角括号
PATTERN_UNIT_WITH_SECTION_FULL_BRACKET = r'^\d+[\.．、]\s*(.+?)([A-Z]{2,}[A-Z0-9]*(?:-?\d+)?)(?=标)标施工[、，]\s*(.+?)([A-Z]{2,}[A-Z0-9]*(?:-?\d+)?)(?=标)标监理的(.+?)（检查(?:时间|日期)[：:]?\s*(.+?)）'

# 单行模式 - 单位+标段+施工/监理 - 半角括号
PATTERN_UNIT_WITH_SECTION_HALF_BRACKET = r'^\d+[\.．、]\s*(.+?)([A-Z]{2,}[A-Z0-9]*(?:-?\d+)?)(?=标)标施工[、，]\s*(.+?)([A-Z]{2,}[A-Z0-9]*(?:-?\d+)?)(?=标)标监理的(.+?)\(检查(?:时间|日期)[：:]?\s*(.+?)\)'

# 跨行模式 - 第一行 - 带"由"字版本
CROSS_LINE_PATTERN_WITH_BY = r'^（[一二三四五六七八九十]+）\s*由(.+?)施工[、，]\s*(.+?)监理的([A-Z]{2,}[A-Z0-9]*(?:-?\d+)?)(?=标)标\s*$'

# 跨行模式 - 第一行 - 无"由"字版本
CROSS_LINE_PATTERN_WITHOUT_BY = r'^（[一二三四五六七八九十]+）\s*(.+?)施工[、，]\s*(.+?)监理的([A-Z]{2,}[A-Z0-9]*(?:-?\d+)?)(?=标)标\s*$'

# 跨行模式 - 第二行 - 全角括号
CROSS_LINE_SITE_PATTERN_FULL_BRACKET = r'^\d+[\.．、]\s*(.+?)（检查(?:时间|日期)[：:]?\s*(.+?)）'

# 跨行模式 - 第二行 - 半角括号
CROSS_LINE_SITE_PATTERN_HALF_BRACKET = r'^\d+[\.．、]\s*(.+?)\(检查(?:时间|日期)[：:]?\s*(.+?)\)'

# 日期解析模式
DATE_PATTERN = r'(\d{4})年(\d{1,2})月(\d{1,2})日'

def parse_date(date_str: str) -> Optional[str]:
    """解析日期字符串为标准格式 YYYY-MM-DD"""
    date_match = re.search(DATE_PATTERN, date_str)
    if date_match:
        year, month, day = date_match.groups()
        return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
    return None
