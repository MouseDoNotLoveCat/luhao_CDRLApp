"""
Word 文档解析模块
用于解析监督通知书 Word 文档
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from docx import Document
from datetime import datetime


class WordDocumentParser:
    """Word 文档解析器"""

    def __init__(self, file_path: str):
        """
        初始化解析器

        Args:
            file_path: Word 文件路径
        """
        self.file_path = Path(file_path)
        self.doc = None
        self.paragraphs = []
        self.current_section = None
        self.document_structure = None  # 文档结构类型：'two_level' 或 'three_level'

    def parse(self) -> Dict:
        """
        解析 Word 文档

        Returns:
            解析结果字典
        """
        try:
            self.doc = Document(str(self.file_path))
            self._extract_paragraphs()

            # 自动检测文档结构（二级 vs 三级）
            self.document_structure = self._detect_document_structure()

            result = {
                'file_name': self.file_path.name,
                'notice_number': self._extract_notice_number(),
                'check_date': self._extract_check_date(),
                'builder_unit': self._extract_builder_unit(),
                'inspection_unit': self._extract_inspection_unit_from_first_para(),
                'inspection_personnel': self._extract_inspection_personnel_from_first_para(),
                'inspection_basis': self._extract_inspection_basis(),
                'project_name': self._extract_project_name_from_first_para(),
                'check_unit': self._extract_check_unit() or '未知单位',
                'check_personnel': self._extract_check_personnel(),
                'project_name_old': self._extract_project_name(),
                'rectification_notices': self._extract_rectification_notices(),
                'other_issues': self._extract_other_issues(),
                'total_issues': 0,
                'declared_issues_count': None,
                'warnings': [],
                'status': 'success',
                'document_structure': self.document_structure  # 添加结构信息到结果中
            }

            result['total_issues'] = len(result['rectification_notices']) + len(result['other_issues'])

            # 验证问题总数
            declared_count_info = self._extract_total_issues_count()
            if declared_count_info:
                result['declared_issues_count'] = declared_count_info
                declared_count = declared_count_info.get('total')
                actual_count = result['total_issues']

                if declared_count != actual_count:
                    result['warnings'].append(
                        f'问题总数不匹配：文档声明 {declared_count} 个，实际识别 {actual_count} 个'
                    )

            return result

        except Exception as e:
            return {
                'file_name': self.file_path.name,
                'status': 'error',
                'error': str(e)
            }
    
    def _extract_paragraphs(self):
        """提取所有段落"""
        # 保存段落对象和文本，以便后续可以访问段落的格式属性（如Word自动编号）
        self.paragraph_objects = [p for p in self.doc.paragraphs if p.text.strip()]
        self.paragraphs = [p.text.strip() for p in self.paragraph_objects]

    def _detect_document_structure(self) -> str:
        """
        自动检测文档的层级结构

        返回值：
        - 'two_level': 二级结构（标段+问题），标段行中包含具体工点名称
        - 'three_level': 三级结构（标段+工点+问题），标段行中不包含具体工点名称

        检测逻辑：
        1. 找到第一个标段行（以（一）、（二）等开头，包含"施工"和"监理"）
        2. 检查该标段行中是否包含具体工点名称（如桥梁名、隧道名、站场名等）
        3. 根据是否包含工点名称来判断结构类型
        """
        # 工点名称的特征词汇（用于识别具体工点名称）
        site_name_keywords = [
            '桥', '隧道', '站', '路基', '基坑', '挡墙', '边坡', '排水', '防护',
            '梁', '墩', '拱', '涵', '通道', '通路', '斜井', '竖井', '出口', '入口',
            '接触网', '信号', '通信', '电力', '给水', '污水', '雨水', '燃气',
            '大桥', '特大桥', '中桥', '小桥', '高架', '地下', '地面'
        ]

        # 查找第一个标段行
        for para in self.paragraphs:
            # 检查是否是标段行（以（一）、（二）等开头，包含"施工"和"监理"）
            if re.match(r'^（[一二三四五六七八九十]）', para) and '施工' in para and '监理' in para:
                # 检查标段行中是否包含工点名称关键词
                has_site_name = any(keyword in para for keyword in site_name_keywords)

                if has_site_name:
                    # 标段行中包含工点名称 → 二级结构
                    return 'two_level'
                else:
                    # 标段行中不包含工点名称 → 三级结构
                    return 'three_level'

        # 如果没有找到标段行，默认返回三级结构
        return 'three_level'

    def _extract_notice_number(self) -> Optional[str]:
        """
        提取通知书编号
        
        格式示例：
        - 南宁站〔2025〕（通知）玉岑08号
        - 南宁站[2025]（通知）柳梧10号
        - 宁建监2025-11
        """
        # 查找编号模式
        patterns = [
            r'南宁站[〔\[]2025[〕\]]\（通知\）\S+\d+号',
            r'宁建监\d{4}-\d+',
            r'编号[：:]\s*(\S+)',
        ]
        
        for para in self.paragraphs[:20]:  # 只查看前 20 段
            for pattern in patterns:
                match = re.search(pattern, para)
                if match:
                    return match.group(0)
        
        return None
    
    def _extract_check_date(self) -> Optional[str]:
        """
        提取检查日期
        
        格式示例：2025-08-07, 2025年8月7日
        """
        date_patterns = [
            r'(\d{4})[年-](\d{1,2})[月-](\d{1,2})[日]?',
        ]
        
        for para in self.paragraphs[:30]:
            for pattern in date_patterns:
                match = re.search(pattern, para)
                if match:
                    year, month, day = match.groups()
                    return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return None
    
    def _extract_check_unit(self) -> Optional[str]:
        """
        提取检查单位
        
        通常在"检查单位"或"监督单位"之后
        """
        for i, para in enumerate(self.paragraphs[:20]):
            if '检查单位' in para or '监督单位' in para:
                # 尝试从当前或下一段提取
                if i + 1 < len(self.paragraphs):
                    return self.paragraphs[i + 1]
                # 或从当前段提取冒号后的内容
                if '：' in para or ':' in para:
                    parts = re.split('[：:]', para)
                    if len(parts) > 1:
                        return parts[1].strip()
        
        return None
    
    def _extract_check_personnel(self) -> Optional[str]:
        """
        提取检查人员
        """
        for i, para in enumerate(self.paragraphs[:20]):
            if '检查人员' in para or '监督人员' in para:
                if i + 1 < len(self.paragraphs):
                    return self.paragraphs[i + 1]
                if '：' in para or ':' in para:
                    parts = re.split('[：:]', para)
                    if len(parts) > 1:
                        return parts[1].strip()

        return None

    def _extract_project_name(self) -> Optional[str]:
        """
        提取项目名称

        通常在文档开头或通知书编号附近
        示例：柳梧铁路、黄百铁路等
        """
        for para in self.paragraphs[:30]:
            # 查找"铁路"关键词
            if '铁路' in para:
                # 提取"xxx铁路"
                match = re.search(r'(\S+铁路)', para)
                if match:
                    return match.group(1)

        return None

    def _extract_builder_unit(self) -> Optional[str]:
        """
        提取建设单位

        位置：通知书编号的下一行
        识别规则：
        1. 查找编号行（包含"编号"、"〔"或"["）
        2. 在编号后的 1-3 行查找建设单位
        3. 建设单位通常以"指挥部"或"公司"结尾
        4. 如果包含冒号，提取冒号前的部分

        示例：
        - 柳州铁路工程建设指挥部
        - 广西铁路投资集团有限公司
        - 云桂铁路广西有限责任公司：
        """
        # 通常在编号后的 1-3 行
        for i, para in enumerate(self.paragraphs[:10]):
            # 查找编号
            if '编号' in para or '〔' in para or '[' in para:
                # 在编号后的 1-3 行查找建设单位
                for j in range(i + 1, min(i + 4, len(self.paragraphs))):
                    next_para = self.paragraphs[j]
                    # 查找"指挥部"或"公司"
                    if '指挥部' in next_para or '公司' in next_para:
                        # 提取单位名称（去掉冒号后的内容）
                        if '：' in next_para or ':' in next_para:
                            parts = re.split('[：:]', next_para)
                            return parts[0].strip()
                        else:
                            return next_para.strip()

        return None

    def _extract_inspection_unit_from_first_para(self) -> Optional[str]:
        """
        从第一段话中提取检查单位

        句子结构：`南宁监督站****对*****铁路****标****、****、****、****，****标*******、*******等工点`

        识别规则：
        1. 检查单位通常是"南宁监督站"或类似的监督站名称
        2. 位于第一段话中

        示例：
        南宁监督站蒋德义、卢浩对柳梧铁路...
        """
        # 查找第一段话（通常在前 10 段）
        for para in self.paragraphs[:10]:
            # 查找"监督站"关键词
            if '监督站' in para:
                # 提取"xxx监督站"（只提取到"监督站"为止）
                match = re.search(r'([^，。；\s]+监督站)', para)
                if match:
                    return match.group(1)

        return None

    def _extract_inspection_personnel_from_first_para(self) -> Optional[str]:
        """
        从第一段话中提取检查人员

        句子结构：
        - 情况1：`南宁监督站【检查人员】根据...对*****铁路...`
        - 情况2：`按照...南宁监督站【检查人员】对*****铁路...`

        识别规则：
        1. 检查人员位于"监督站"之后
        2. 通常是人名列表，用、分隔
        3. 在"根据"/"按照"或"对"处截断，只提取人名部分
        4. 优先在"根据"/"按照"处截断

        示例：
        - 南宁监督站【卢浩、陈胜及建设部第四检查组胡云龙】根据《...》...对黄百铁路...
        - 按照...南宁监督站【唐小林、罗斌、蒋德义】对柳梧铁路...
        """
        # 查找第一段话
        for para in self.paragraphs[:10]:
            # 查找"监督站"
            if '监督站' in para:
                # 查找"监督站"的位置
                station_pos = para.find('监督站')
                after_station = para[station_pos + 3:]

                # 查找"根据"或"按照"的位置
                basis_keywords = ['根据', '按照']
                basis_pos = -1
                for keyword in basis_keywords:
                    pos = after_station.find(keyword)
                    if pos != -1 and (basis_pos == -1 or pos < basis_pos):
                        basis_pos = pos

                # 查找"对"的位置
                dui_pos = after_station.find('对')

                # 确定截断位置：优先使用"根据"/"按照"，否则使用"对"
                end_pos = -1
                if basis_pos != -1:
                    end_pos = basis_pos
                elif dui_pos != -1:
                    end_pos = dui_pos

                if end_pos != -1:
                    # 提取"监督站"和截断位置之间的文字
                    personnel = after_station[:end_pos].strip()
                    # 去掉可能的空格和特殊字符
                    personnel = re.sub(r'[\s\u3000]+', '', personnel)
                    if personnel:
                        return personnel

        return None

    def _extract_inspection_basis(self) -> Optional[str]:
        """
        从第一段话中提取检查依据

        句子结构：`...对*****铁路...根据《...》、《...》...`

        识别规则：
        1. 检查依据位于"根据"或"按照"之后
        2. 通常包含多个文件名称和文号
        3. 以"等文件的要求"、"等文件"、"等规定"、"等要求"等词语结尾
        4. 或者以"，"后面跟着新的语义段落结尾

        示例：
        根据《国铁集团关于开展在建铁路桥梁施工安全隐患排查整治的紧急通知》(铁建设电〔2025〕44号)、
        《国家铁路局综合司关于开展铁路桥梁工程质量安全问题隐患排查治理的通知》（国铁综工程监函[2025]351号）、
        《中国铁路南宁局集团有限公司关于集中开展铁路建设项目安全隐患排查整治工作的通知》（宁铁建函〔2025〕243号）
        """
        # 查找第一段话
        for para in self.paragraphs[:10]:
            # 查找"根据"或"按照"
            if '根据' in para or '按照' in para:
                # 查找"根据"或"按照"的位置
                basis_start = -1
                if '根据' in para:
                    basis_start = para.find('根据')
                if '按照' in para and (basis_start == -1 or para.find('按照') < basis_start):
                    basis_start = para.find('按照')

                if basis_start != -1:
                    # 从"根据"或"按照"之后开始提取
                    basis_text = para[basis_start:]

                    # 查找结束标志
                    # 优先查找"等文件的要求"、"等文件"、"等规定"、"等要求"
                    end_patterns = [
                        r'等文件的要求',
                        r'等文件',
                        r'等规定',
                        r'等要求',
                        r'等通知',
                        r'等文件精神',
                    ]

                    for pattern in end_patterns:
                        match = re.search(pattern, basis_text)
                        if match:
                            # 提取到匹配位置的末尾
                            basis_text = basis_text[:match.end()]
                            break
                    else:
                        # 如果没有找到明确的结束标志，查找下一个"，"后面是否有新的语义段落
                        # 通常新段落会以"对"、"在"、"为"等词开头
                        comma_matches = list(re.finditer(r'，', basis_text))
                        if comma_matches:
                            # 检查最后一个逗号之后是否有新的语义段落
                            last_comma_pos = comma_matches[-1].end()
                            after_comma = basis_text[last_comma_pos:].strip()
                            # 如果逗号后面是新的语义段落（不是继续列举文件），则在逗号处截断
                            if after_comma and not after_comma[0] in '《【':
                                basis_text = basis_text[:last_comma_pos - 1]

                    basis_text = basis_text.strip()
                    if basis_text:
                        return basis_text

        return None

    def _extract_project_name_from_first_para(self) -> Optional[str]:
        """
        从第一段话中提取项目名称

        句子结构：`南宁监督站****对【项目名称】****标****、****、****、****，****标*******、*******等工点`

        识别规则：
        1. 项目名称位于"对"之后
        2. 包含"铁路"两个字
        3. 在标段编号（如"HBZQ-1标"、"LWZQ-8标"）之前
        4. 支持"铁路广西段"这样的完整项目名称

        示例：
        - 南宁监督站蒋德义、卢浩对【柳梧铁路】LWZQ-8标...
        - 南宁监督站李规录、陈胜对【黄百铁路广西段】HBZQ-1标...
        """
        # 查找第一段话
        for para in self.paragraphs[:10]:
            # 查找"对"和"铁路"
            if '对' in para and '铁路' in para:
                # 提取"对"之后的内容
                after_dui = para.split('对', 1)
                if len(after_dui) > 1:
                    content = after_dui[1]
                    # 提取项目名称：从"对"之后到标段编号（如"HBZQ-1标"、"LWZQ-8标"）之前
                    # 正则表达式：匹配"xxx铁路xxx"，但在标段编号前停止
                    # 标段编号格式：[A-Z]{2}[A-Z]+(?:-?\d+)?标（如HBZQ-1标、LWZQ-8标）
                    match = re.search(r'([^，。；\s]+铁路[^，。；\s]*?)(?=[A-Z]{2}[A-Z]+(?:-?\d+)?标)', content)
                    if match:
                        project_name = match.group(1).strip()
                        return project_name

        return None
    
    def _identify_section(self, para: str) -> Optional[str]:
        """
        识别段落所属的章节

        Returns:
            'rectification' - 下发整改通知单章节
            'other' - 其它问题章节
            None - 其它章节
        """
        # 下发整改通知单章节（第二章）
        if '二、' in para and ('下发整改通知单' in para or '不良行为' in para or '工点及问题' in para):
            return 'rectification'
        # 其它问题章节（第三章或第二章的"主要质量安全问题"）
        elif ('三、' in para or '其他主要' in para or '其它主要' in para or
              ('二、' in para and ('主要质量安全问题' in para or '主要安全质量问题' in para))) and \
             ('其他' in para or '其它' in para or '主要' in para or '问题' in para):
            return 'other'
        # 监督意见/有关要求章节（第三/四章）- 这些章节标志着问题部分的结束
        elif '四、' in para or '三、' in para or '监督意见' in para or '监督有关' in para or '有关要求' in para:
            return None

        return None
    
    def _extract_rectification_notices(self) -> List[Dict]:
        """
        提取下发整改通知单的问题

        支持两种格式：

        格式1（柳梧）：
        （一）由[施工单位]施工、[监理单位]监理的[标段名称][工点名称]（检查日期：[日期]）
        检查情况：[问题描述]
        处理措施：[处理内容]

        格式2（黄百）：
        1.中铁五局施工、西南交大监理的HBZQ-2标布柳河特大桥（检查时间：2025年9月10日）
        [问题描述]
        处理措施：[处理内容]

        返回：包含标段、工点、问题的问题列表
        """
        issues = []
        in_rectification = False
        current_section_code = None
        current_section_name = None
        current_contractor = None
        current_supervisor = None
        current_site_name = None
        current_inspection_date = None
        current_description = None
        current_requirements = None
        current_deadline = None
        current_responsible_unit = None

        # 检测文档格式
        doc_format = self._detect_document_format()

        # 提前获取检查单位和检查人员（用于所有问题）
        inspection_unit = self._extract_inspection_unit_from_first_para()
        inspection_personnel = self._extract_inspection_personnel_from_first_para()

        for para in self.paragraphs:
            # 检查是否进入新章节
            section = self._identify_section(para)
            if section == 'rectification':
                in_rectification = True
                continue
            elif section == 'other':
                # 进入其它问题章节，停止收集整改通知单
                in_rectification = False
                break

            # 如果在整改通知单章节
            if in_rectification:
                # 格式1：检查是否是新标段/工点（以（一）、（二）等开头）
                if re.match(r'^（[一二三四五六七八九十]）', para):
                    # 保存前一个问题
                    if current_description:
                        issue = {
                            'section_code': current_section_code,
                            'section_name': current_section_name,
                            'site_name': current_site_name,
                            'contractor': current_contractor,
                            'supervisor': current_supervisor,
                            'inspection_unit': inspection_unit,
                            'inspection_personnel': inspection_personnel,
                            'inspection_date': current_inspection_date,
                            'description': current_description,
                            'rectification_requirements': current_requirements,
                            'rectification_deadline': current_deadline,
                            'responsible_unit': current_responsible_unit,
                            'is_rectification_notice': True,
                            'is_bad_behavior_notice': False,
                            'document_section': 'rectification'
                        }
                        issues.append(issue)

                    # 解析新的标段/工点信息
                    current_section_code = self._extract_section_code(para)
                    current_section_name = self._extract_section_name(para)
                    current_site_name = self._extract_site_name(para)
                    current_contractor = self._extract_contractor(para)
                    current_supervisor = self._extract_supervisor(para)
                    current_inspection_date = self._extract_check_date_from_para(para)
                    current_description = None
                    current_requirements = None
                    current_deadline = None
                    current_responsible_unit = None

                # 格式2：检查是否是黄百格式的数字编号行（如"1.中铁五局施工..."）
                elif doc_format == 'format2' and re.match(r'^\d+\.', para):
                    # 检查是否是黄百格式的标段/工点行（包含"施工"、"监理"、"标"）
                    if '施工' in para and '监理' in para and '标' in para:
                        # 保存前一个问题
                        if current_description:
                            issue = {
                                'section_code': current_section_code,
                                'section_name': current_section_name,
                                'site_name': current_site_name,
                                'contractor': current_contractor,
                                'supervisor': current_supervisor,
                                'inspection_unit': inspection_unit,
                                'inspection_personnel': inspection_personnel,
                                'inspection_date': current_inspection_date,
                                'description': current_description,
                                'rectification_requirements': current_requirements,
                                'rectification_deadline': current_deadline,
                                'responsible_unit': current_responsible_unit,
                                'is_rectification_notice': True,
                                'is_bad_behavior_notice': '不良行为' in (current_requirements or ''),
                                'document_section': 'rectification'
                            }
                            issues.append(issue)

                        # 从数字编号行提取信息
                        contractor, supervisor, section_code, site_name, check_date = self._extract_info_from_numbered_line(para)
                        current_contractor = contractor
                        current_supervisor = supervisor
                        current_section_code = section_code
                        current_site_name = site_name
                        current_inspection_date = check_date
                        current_section_name = f"{section_code}标" if section_code else None
                        current_description = None
                        current_requirements = None
                        current_deadline = None
                        current_responsible_unit = None
                    else:
                        # 这可能是问题描述（黄百格式中，问题描述可能直接跟在工点行后面）
                        if current_site_name is not None:
                            current_description = para.replace(r'^\d+\.', '').strip()
                        else:
                            # 如果还没有工点信息，这可能是其他内容
                            pass

                # 检查是否是"检查情况："段落
                elif para.startswith('检查情况：'):
                    current_description = para.replace('检查情况：', '').strip()

                # 检查是否是"处理措施："段落
                elif para.startswith('处理措施：'):
                    measures = para.replace('处理措施：', '').strip()
                    current_requirements = measures

                    # 从处理措施中提取整改期限
                    deadline = self._extract_deadline_from_measures(measures)
                    if deadline:
                        current_deadline = deadline

                    # 从处理措施中提取责任单位
                    responsible = self._extract_responsible_unit_from_measures(measures)
                    if responsible:
                        current_responsible_unit = responsible

                    # 判断是否是不良行为通知单
                    if '不良行为' in measures:
                        # 这是一个不良行为通知单，需要创建问题
                        if current_description:
                            issue = {
                                'section_code': current_section_code,
                                'section_name': current_section_name,
                                'site_name': current_site_name,
                                'contractor': current_contractor,
                                'supervisor': current_supervisor,
                                'inspection_unit': inspection_unit,
                                'inspection_personnel': inspection_personnel,
                                'inspection_date': current_inspection_date,
                                'description': current_description,
                                'rectification_requirements': current_requirements,
                                'rectification_deadline': current_deadline,
                                'responsible_unit': current_responsible_unit,
                                'is_rectification_notice': True,
                                'is_bad_behavior_notice': True,
                                'document_section': 'rectification'
                            }
                            issues.append(issue)
                    else:
                        # 普通整改通知单：每个工点只创建一个问题，无论有多少份通知单
                        if current_description:
                            issue = {
                                'section_code': current_section_code,
                                'section_name': current_section_name,
                                'site_name': current_site_name,
                                'contractor': current_contractor,
                                'supervisor': current_supervisor,
                                'inspection_unit': inspection_unit,
                                'inspection_personnel': inspection_personnel,
                                'inspection_date': current_inspection_date,
                                'description': current_description,
                                'rectification_requirements': current_requirements,
                                'rectification_deadline': current_deadline,
                                'responsible_unit': current_responsible_unit,
                                'is_rectification_notice': True,
                                'is_bad_behavior_notice': False,
                                'document_section': 'rectification'
                            }
                            issues.append(issue)

                    # 重置
                    current_description = None
                    current_requirements = None
                    current_deadline = None
                    current_responsible_unit = None

                # 黄百格式：如果当前有工点信息但没有问题描述，且这不是特殊段落，则作为问题描述
                elif doc_format == 'format2' and current_site_name is not None and current_description is None:
                    if not para.startswith('处理措施：') and not para.startswith('检查情况：'):
                        # 这是问题描述
                        current_description = para

        # 添加最后一个问题
        if current_description:
            issue = {
                'section_code': current_section_code,
                'section_name': current_section_name,
                'site_name': current_site_name,
                'contractor': current_contractor,
                'supervisor': current_supervisor,
                'inspection_unit': inspection_unit,
                'inspection_personnel': inspection_personnel,
                'inspection_date': current_inspection_date,
                'description': current_description,
                'rectification_requirements': current_requirements,
                'rectification_deadline': current_deadline,
                'responsible_unit': current_responsible_unit,
                'is_rectification_notice': True,
                'is_bad_behavior_notice': '不良行为' in (current_requirements or ''),
                'document_section': 'rectification'
            }
            issues.append(issue)

        return issues

    def _extract_check_date_from_para(self, para: str) -> Optional[str]:
        """
        从单个段落中提取检查日期

        格式示例：2025年5月21日
        """
        date_patterns = [
            r'(\d{4})年(\d{1,2})月(\d{1,2})日',
        ]

        for pattern in date_patterns:
            match = re.search(pattern, para)
            if match:
                year, month, day = match.groups()
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"

        return None

    def _detect_document_format(self) -> str:
        """
        检测文档格式

        返回：
        - 'format1'：有一级编号（（一）、（二）等）- 柳梧格式
        - 'format2'：无一级编号，直接使用数字编号 - 黄百格式
        """
        # 查找"二、下发整改通知单"或"三、其他"章节
        in_section = False
        for para in self.paragraphs:
            if '二、' in para or '三、' in para:
                in_section = True
                continue

            if in_section:
                # 检查是否有一级编号
                if re.match(r'^（[一二三四五六七八九十]）', para):
                    return 'format1'
                # 检查是否有数字编号（且包含标段信息）
                elif re.match(r'^\d+\.', para) and ('标' in para or '施工' in para):
                    return 'format2'
                # 如果找到了其他章节标记，停止检测
                elif re.match(r'^[四五六七八九十]、', para):
                    break

        # 默认返回 format1
        return 'format1'

    def _extract_section_code(self, para: str) -> Optional[str]:
        """提取标段编号，如 LWZF-2, LWXQ, LWZQ-8, HBZQ-1 等"""
        # 匹配 LW 或 HB 开头，后跟字母和可选的数字
        match = re.search(r'([LH]W[A-Z]+(?:-?\d+)?)', para)
        if match:
            return match.group(1)
        return None

    def _extract_section_name(self, para: str) -> Optional[str]:
        """提取标段名称（包含标段编号和"标"字）"""
        # 格式：LWZF-2标
        match = re.search(r'(LW[A-Z]+(?:-?\d+)?标)', para)
        if match:
            return match.group(1)
        return None

    def _extract_site_name(self, para: str) -> Optional[str]:
        """提取工点名称"""
        # 格式1（柳梧）：由中铁上海局施工、北京现代监理的LWZF-2标藤县北站（检查日期：
        match = re.search(r'标(.+?)（检查日期', para)
        if match:
            return match.group(1)

        # 格式2（黄百）：由中铁上海局施工、北京现代监理的HBZQ-1标幼平隧道进口（检查时间：
        match = re.search(r'标(.+?)（检查时间', para)
        if match:
            return match.group(1)

        return None

    def _extract_info_from_numbered_line(self, para: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Optional[str]]:
        """
        从黄百格式的数字编号行中提取信息

        格式：1.中铁五局施工、西南交大监理的HBZQ-2标布柳河特大桥（检查时间：2025年9月10日）
        或：11.中铁十四局施工、广西宁铁监理的HBZQ-4标凌云隧道2斜小里程(检查时间：2025年9月11日)。

        返回：(施工单位, 监理单位, 标段编号, 工点名称, 检查日期)
        """
        # 正则表达式：支持全角和半角括号
        # 先尝试全角括号
        pattern = r'^\d+\.(.+?)施工、(.+?)监理的(.+?)标(.+?)（检查[时日]间?[：:]\s*(.+?)）'
        match = re.search(pattern, para)

        # 如果没有匹配，尝试半角括号
        if not match:
            pattern = r'^\d+\.(.+?)施工、(.+?)监理的(.+?)标(.+?)\(检查[时日]间?[：:]\s*(.+?)\)'
            match = re.search(pattern, para)

        if match:
            contractor = match.group(1)
            supervisor = match.group(2)
            section_code = match.group(3)
            site_name = match.group(4)
            check_date_str = match.group(5)

            # 解析检查日期
            check_date = None
            date_match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', check_date_str)
            if date_match:
                year, month, day = date_match.groups()
                check_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

            return contractor, supervisor, section_code, site_name, check_date

        return None, None, None, None, None

    def _extract_point_name(self, para: str) -> Optional[str]:
        """提取工点名称（兼容旧方法）"""
        return self._extract_site_name(para)

    def _extract_deadline_from_measures(self, measures: str) -> Optional[str]:
        """从处理措施中提取整改期限"""
        # 格式：2025年5月24日前完成整改
        match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', measures)
        if match:
            year, month, day = match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        return None

    def _extract_responsible_unit_from_measures(self, measures: str) -> Optional[str]:
        """从处理措施中提取责任单位"""
        # 查找"施工单位"、"监理单位"等
        if '施工单位' in measures:
            return '施工单位'
        elif '监理单位' in measures:
            return '监理单位'
        elif '设计单位' in measures:
            return '设计单位'
        return None

    def _extract_contractor(self, para: str) -> Optional[str]:
        """提取施工单位"""
        match = re.search(r'由(.+?)施工', para)
        if match:
            return match.group(1)
        return None

    def _extract_supervisor(self, para: str) -> Optional[str]:
        """提取监理单位"""
        match = re.search(r'、(.+?)监理', para)
        if match:
            return match.group(1)
        return None
    
    def _extract_total_issues_count(self) -> Optional[Dict]:
        """
        提取文档中声明的问题总数

        支持多种格式：
        格式1（柳梧）：检查发现各类安全质量问题53个（安全问题12个、质量问题21个、管理行为问题20个）
        格式2（黄百）：共计发现各类问题79个,其中质量问题27个，安全问题29个，管理行为及其他问题23个

        返回：
        {
            'total': 53,
            'safety': 12,
            'quality': 21,
            'management': 20
        }
        或 None 如果未找到
        """
        # 查找包含问题总数的段落
        for para in self.paragraphs[:20]:  # 只查看前 20 段
            if '发现' in para and '问题' in para:
                # 尝试多种格式的正则表达式
                total_count = None

                # 格式1：检查发现各类...问题(\d+)个
                match = re.search(r'检查发现各类.*?问题(\d+)个', para)
                if match:
                    total_count = int(match.group(1))

                # 格式2：共计发现各类问题(\d+)个 或 发现各类问题(\d+)个
                if not match:
                    match = re.search(r'(?:共计)?发现各类问题(\d+)个', para)
                    if match:
                        total_count = int(match.group(1))

                if total_count:
                    result = {'total': total_count}

                    # 提取安全问题数
                    safety_match = re.search(r'安全问题(\d+)个', para)
                    if safety_match:
                        result['safety'] = int(safety_match.group(1))

                    # 提取质量问题数
                    quality_match = re.search(r'质量问题(\d+)个', para)
                    if quality_match:
                        result['quality'] = int(quality_match.group(1))

                    # 提取管理行为问题数（支持多种格式）
                    # 格式1：管理行为问题(\d+)个
                    # 格式2：管理行为及其他问题(\d+)个 或 管理行为及其它问题(\d+)个
                    management_match = re.search(r'管理行为(?:及其[他它])?问题(\d+)个', para)
                    if management_match:
                        result['management'] = int(management_match.group(1))

                    return result

        return None

    def _extract_other_issues(self) -> List[Dict]:
        """
        提取其它安全质量问题

        支持多种格式：

        格式1（柳梧）：标段和工点分开
        （一）由[施工单位]施工、[监理单位]监理的[标段名称]（检查日期：[日期]）
        1. [工点名称]
        （1）[问题描述]
        （2）[问题描述]

        格式2（柳梧）：标段和工点合并（单工点情况）
        （一）由[施工单位]施工、[监理单位]监理的[标段名称][工点名称]（检查日期：[日期]）
        （1）[问题描述]
        （2）[问题描述]

        格式3（黄百）：无一级编号，直接使用数字编号
        1.中铁上海局施工、内蒙古沁原监理的HBZQ-1标幼平隧道进口（检查时间：2025年9月9日）
        （1）[问题描述]
        （2）[问题描述]

        返回：包含标段、工点、问题的问题列表
        """
        issues = []
        in_other = False
        in_problem_list = False  # 标记是否已经进入问题列表（用于三级结构）
        current_section_code = None
        current_section_name = None
        current_contractor = None
        current_supervisor = None
        current_inspection_date = None
        current_site_name = None

        # 检测文档格式
        doc_format = self._detect_document_format()

        # 提前获取检查单位和检查人员（用于所有问题）
        inspection_unit = self._extract_inspection_unit_from_first_para()
        inspection_personnel = self._extract_inspection_personnel_from_first_para()

        for idx, para in enumerate(self.paragraphs):
            # 获取对应的段落对象，用于检查Word格式属性
            para_obj = self.paragraph_objects[idx] if idx < len(self.paragraph_objects) else None

            # 检查是否进入新章节
            section = self._identify_section(para)
            if section == 'other':
                in_other = True
                continue
            elif section == 'rectification':
                # 不应该回到整改通知单章节
                continue

            # 如果进入其它章节（如"三、有关要求"或"四、监督意见"），停止收集
            # 但要排除"三、其它问题"这样的章节
            if in_other and (re.match(r'^[四五六七八九十]、', para) or
                            ('三、' in para and ('有关要求' in para or '监督意见' in para)) or
                            '监督意见' in para):
                break

            # 如果在其它问题章节
            if in_other:
                # 检查段落是否有Word自动编号
                has_word_numbering = False
                if para_obj is not None:
                    pPr = para_obj._element.get_or_add_pPr()
                    numPr = pPr.find('.//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr')
                    has_word_numbering = numPr is not None

                # 检查是否是新标段（以（一）、（二）等开头，且包含"由...施工、...监理的"）
                # 这是标段编号行，不是问题编号行
                if re.match(r'^（[一二三四五六七八九十]）', para) and '施工' in para and '监理' in para:
                    # 解析新的标段信息
                    current_section_code = self._extract_section_code(para)
                    current_section_name = self._extract_section_name(para)
                    current_contractor = self._extract_contractor(para)
                    current_supervisor = self._extract_supervisor(para)
                    current_inspection_date = self._extract_check_date_from_para(para)

                    # 尝试从一级编号中提取工点名称（格式2：标段和工点合并）
                    # 格式：由[施工单位]施工、[监理单位]监理的[标段名称][工点名称]（检查日期：[日期]）
                    current_site_name = self._extract_site_name(para)
                    # 如果没有提取到工点名称，说明是格式1（标段和工点分开），重置为None
                    if current_site_name is None:
                        current_site_name = None

                    # 重置问题列表标记
                    in_problem_list = False

                # 检查是否是数字项（以数字.或数字、开头，如"1.工点名称"、"1、工点名称"或"1.问题描述"）
                elif re.match(r'^\d+[\.、]', para):
                    # 格式3（黄百）：检查是否是黄百格式的数字编号行（包含标段和工点信息）
                    if doc_format == 'format2' and ('施工' in para and '监理' in para and '标' in para):
                        # 从数字编号行提取信息
                        contractor, supervisor, section_code, site_name, check_date = self._extract_info_from_numbered_line(para)
                        current_contractor = contractor
                        current_supervisor = supervisor
                        current_section_code = section_code
                        current_site_name = site_name
                        current_inspection_date = check_date
                        current_section_name = f"{section_code}标" if section_code else None
                    else:
                        # 格式1/2（柳梧）：提取内容
                        match = re.search(r'^\d+[\.、](.+)$', para)
                        if match:
                            content = match.group(1).strip()

                            # 根据文档结构类型判断是工点名称还是问题描述
                            # 三级结构：数字编号行通常是工点编号行（1.工点名称）
                            # 二级结构：数字编号行通常是问题编号行（1.问题描述）

                            # 管理类工点名称的关键词列表
                            management_keywords = ['管理方面', '管理行为', '管理问题', '管理制度']

                            # 首先检查是否是管理类工点名称（优先级最高）
                            if content in management_keywords or content.endswith('管理方面'):
                                # 这是管理类工点名称
                                current_site_name = content
                            # 检查是否是新的工点名称（包含"（检查时间"或"（检查日期"）
                            elif '（检查时间' in content or '（检查日期' in content:
                                # 这是新的工点名称
                                current_site_name = content
                            # 根据文档结构类型判断
                            elif self.document_structure == 'three_level':
                                # 三级结构：数字编号行可能是工点编号或问题编号
                                # 判断规则：
                                # 1. 如果内容很短（<30字）且不包含问题特征词汇，则是工点名称
                                # 2. 如果内容很长（>30字）或包含问题特征词汇，则是问题描述

                                # 问题特征词汇
                                problem_keywords = ['存在', '不符', '未', '缺', '破损', '脱焊', '松脱', '不足', '过大', '过小', '不到位', '隐患', '质量', '安全']
                                has_problem_keyword = any(keyword in content for keyword in problem_keywords)

                                if len(content) < 30 and not has_problem_keyword:
                                    # 这是工点名称
                                    current_site_name = content
                                else:
                                    # 这是问题描述
                                    in_problem_list = True
                                    issue = {
                                        'section_code': current_section_code,
                                        'section_name': current_section_name,
                                        'site_name': current_site_name,
                                        'contractor': current_contractor,
                                        'supervisor': current_supervisor,
                                        'inspection_unit': inspection_unit,
                                        'inspection_personnel': inspection_personnel,
                                        'inspection_date': current_inspection_date,
                                        'description': content,
                                        'is_rectification_notice': False,
                                        'is_bad_behavior_notice': False,
                                        'document_section': 'other'
                                    }
                                    issues.append(issue)
                            elif self.document_structure == 'two_level':
                                # 二级结构：数字编号行是问题编号行
                                # 规则：如果当前工点名称已经从一级编号中提取，则这是问题描述
                                if current_site_name is not None:
                                    # 这是问题描述（格式2的情况）
                                    issue = {
                                        'section_code': current_section_code,
                                        'section_name': current_section_name,
                                        'site_name': current_site_name,
                                        'contractor': current_contractor,
                                        'supervisor': current_supervisor,
                                        'inspection_unit': inspection_unit,
                                        'inspection_personnel': inspection_personnel,
                                        'inspection_date': current_inspection_date,
                                        'description': content,
                                        'is_rectification_notice': False,
                                        'is_bad_behavior_notice': False,
                                        'document_section': 'other'
                                    }
                                    issues.append(issue)
                                else:
                                    # 这是工点名称（还没有提取到工点名称）
                                    current_site_name = content
                            elif not re.match(r'^（[0-9０-９]）', content) and not re.match(r'^[⑴-⑽]', content):
                                # 这是工点名称（格式1的情况）
                                # 规则：不以问题编号开头（（1）、⑴等）
                                current_site_name = content
                            else:
                                # 这是问题描述（没有工点名称的情况）
                                # 创建问题记录
                                issue = {
                                    'section_code': current_section_code,
                                    'section_name': current_section_name,
                                    'site_name': current_site_name,
                                    'contractor': current_contractor,
                                    'supervisor': current_supervisor,
                                    'inspection_unit': inspection_unit,
                                    'inspection_personnel': inspection_personnel,
                                    'inspection_date': current_inspection_date,
                                    'description': content,
                                    'is_rectification_notice': False,
                                    'is_bad_behavior_notice': False,
                                    'document_section': 'other'
                                }
                                issues.append(issue)

                # 检查是否是具体问题（以（1）、（2）、⑴、⑵等开头，或有Word自动编号）
                # 支持：（1）、(1)、（１）、(１)、（10）、(10)、⑴、⑵ 等格式，以及Word自动编号
                # 但要排除工点名称行（包含"（检查时间"或"（检查日期"）
                elif (re.match(r'^[（(⑴-⑽]', para) or has_word_numbering) and not ('（检查时间' in para or '（检查日期' in para):
                    # 提取问题编号和描述
                    # 支持：（1）、(1)、（１）、(１)、（10）、(10)、⑴、⑵ 等格式
                    # 先尝试括号格式
                    match = re.search(r'^[（(][0-9０-９]+[）)](.+)$', para)
                    if not match:
                        # 尝试带圈数字格式
                        match = re.search(r'^[⑴-⑽](.+)$', para)

                    # 如果没有匹配到文本编号，但有Word自动编号，则整行都是描述
                    if not match and has_word_numbering:
                        description = para
                    elif match:
                        description = match.group(1).strip()
                    else:
                        description = None

                    if description:
                        # 标记已经进入问题列表
                        in_problem_list = True
                        # 创建问题记录
                        issue = {
                            'section_code': current_section_code,
                            'section_name': current_section_name,
                            'site_name': current_site_name,
                            'contractor': current_contractor,
                            'supervisor': current_supervisor,
                            'inspection_unit': inspection_unit,
                            'inspection_personnel': inspection_personnel,
                            'inspection_date': current_inspection_date,
                            'description': description,
                            'is_rectification_notice': False,
                            'is_bad_behavior_notice': False,
                            'document_section': 'other'
                        }
                        issues.append(issue)

                # 启发式规则：识别无编号的问题
                # 如果一行既没有文本编号，也没有Word编号，但在工点名称之后，且长度足够长，则认为它是问题描述
                elif (current_site_name is not None and
                      not re.match(r'^（[一二三四五六七八九十]）', para) and
                      not re.match(r'^\d+[\.、]', para) and
                      not re.match(r'^[（(⑴-⑽]', para) and
                      not ('（检查时间' in para or '（检查日期' in para) and
                      len(para) > 20):
                    # 这是一个无编号的问题描述
                    issue = {
                        'section_code': current_section_code,
                        'section_name': current_section_name,
                        'site_name': current_site_name,
                        'contractor': current_contractor,
                        'supervisor': current_supervisor,
                        'inspection_unit': inspection_unit,
                        'inspection_personnel': inspection_personnel,
                        'inspection_date': current_inspection_date,
                        'description': para,
                        'is_rectification_notice': False,
                        'is_bad_behavior_notice': False,
                        'document_section': 'other'
                    }
                    issues.append(issue)

        return issues


def parse_word_document(file_path: str) -> Dict:
    """
    解析 Word 文档的便捷函数
    
    Args:
        file_path: Word 文件路径
    
    Returns:
        解析结果
    """
    parser = WordDocumentParser(file_path)
    return parser.parse()

