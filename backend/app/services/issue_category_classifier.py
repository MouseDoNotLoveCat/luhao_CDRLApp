"""
问题类别分类器
根据问题描述、工点名称等信息，自动识别问题的一级分类
"""

import re
from typing import Optional


class IssueCategoryClassifier:
    """问题类别分类器"""

    # 管理行为的关键词
    MANAGEMENT_KEYWORDS = [
        '管理', '制度', '资源配置', '方案', '技术交底', '检验', '试验', '验收',
        '建设单位', '勘察', '设计单位', '监理单位', '施工单位', '检测单位', '审核单位',
        '组织', '协调', '沟通', '文件', '记录', '档案', '报告', '总结'
    ]

    # 施工安全的关键词
    SAFETY_KEYWORDS = [
        '安全', '隧道施工', '脚手架', '支架', '高空', '临边', '水上', '模板', '挂篮',
        '用电', '既有线', '基坑', '边坡', '开挖', '高墩', '大跨', '交叉', '铺轨',
        '架梁', '起重', '吊装', '钢结构', '火工', '特种设备', '防护', '消防', '防火',
        '坍塌', '触电', '坠落', '伤害', '事故', '隐患', '防护用具', '安全帽', '安全带'
    ]

    # 工程质量的关键词
    QUALITY_KEYWORDS = [
        '质量', '混凝土', '路基', '桥', '隧道', '轨道', '站房', '四电', '工程',
        '原材料', '模板', '钢筋', '配合比', '拌合', '拌制', '运输', '浇筑', '养护',
        '冬期', '高温', '大体积', '地基', '填料', '填筑', '路堑', '过渡段', '排水',
        '支挡', '防护', '沉降', '观测', '基础', '承台', '墩', '台身', '现浇梁',
        '场制梁', '钢梁', '支座', '涵洞', '地下通道', '架梁', '桥面', '附属',
        '无砟轨道', 'CRTS', '弹性支撑', '长钢轨', '焊接', '无缝线路', '应力',
        '打磨', '精调', '道岔', '有砟轨道', '铺砟', '大机整道', '基坑支护',
        '桩基础', '建筑防水', '砌体', '装饰', '装修', '幕墙', '屋面', '机电',
        '建筑节能', '综合接地', '接口', '杆塔', '设备安装', '电缆', '敷设',
        '接触网', '通信', '信号', '缺陷', '不符', '破损', '脱焊', '松脱', '不足',
        '过大', '过小', '不到位', '偏差', '错位', '变形', '裂纹', '渗漏'
    ]

    @classmethod
    def classify(cls, description: str, site_name: str = None, section_name: str = None) -> str:
        """
        根据问题描述、工点名称、标段名称等信息，识别问题的一级分类

        Args:
            description: 问题描述
            site_name: 工点名称
            section_name: 标段名称

        Returns:
            问题一级分类：'工程质量'、'施工安全'、'管理行为' 或 '其它'
        """
        if not description:
            return '其它'

        # 合并所有文本用于分类
        all_text = description
        if site_name:
            all_text += ' ' + site_name
        if section_name:
            all_text += ' ' + section_name

        # 转换为小写以便匹配
        text_lower = all_text.lower()

        # 计算各类别的匹配分数
        management_score = cls._calculate_score(text_lower, cls.MANAGEMENT_KEYWORDS)
        safety_score = cls._calculate_score(text_lower, cls.SAFETY_KEYWORDS)
        quality_score = cls._calculate_score(text_lower, cls.QUALITY_KEYWORDS)

        # 根据分数判断分类
        scores = {
            '管理行为': management_score,
            '施工安全': safety_score,
            '工程质量': quality_score
        }

        # 找到分数最高的分类
        max_score = max(scores.values())

        # 如果没有匹配到任何关键词，返回其它
        if max_score == 0:
            return '其它'

        # 返回分数最高的分类
        for category, score in scores.items():
            if score == max_score:
                return category

        return '其它'

    @classmethod
    def _calculate_score(cls, text: str, keywords: list) -> int:
        """
        计算文本与关键词列表的匹配分数

        Args:
            text: 要匹配的文本
            keywords: 关键词列表

        Returns:
            匹配分数
        """
        score = 0
        for keyword in keywords:
            # 使用单词边界匹配，避免部分匹配
            pattern = r'\b' + re.escape(keyword) + r'\b'
            matches = len(re.findall(pattern, text))
            score += matches

        return score

    @classmethod
    def classify_with_confidence(cls, description: str, site_name: str = None, section_name: str = None) -> dict:
        """
        根据问题描述等信息，识别问题的一级分类，并返回置信度

        Args:
            description: 问题描述
            site_name: 工点名称
            section_name: 标段名称

        Returns:
            {
                'category': '工程质量' | '施工安全' | '管理行为' | '其它',
                'confidence': 0.0-1.0,
                'scores': {
                    '工程质量': score,
                    '施工安全': score,
                    '管理行为': score
                }
            }
        """
        if not description:
            return {
                'category': '其它',
                'confidence': 0.0,
                'scores': {'工程质量': 0, '施工安全': 0, '管理行为': 0}
            }

        # 合并所有文本用于分类
        all_text = description
        if site_name:
            all_text += ' ' + site_name
        if section_name:
            all_text += ' ' + section_name

        # 转换为小写以便匹配
        text_lower = all_text.lower()

        # 计算各类别的匹配分数
        management_score = cls._calculate_score(text_lower, cls.MANAGEMENT_KEYWORDS)
        safety_score = cls._calculate_score(text_lower, cls.SAFETY_KEYWORDS)
        quality_score = cls._calculate_score(text_lower, cls.QUALITY_KEYWORDS)

        scores = {
            '工程质量': quality_score,
            '施工安全': safety_score,
            '管理行为': management_score
        }

        # 找到分数最高的分类
        max_score = max(scores.values())
        total_score = sum(scores.values())

        # 计算置信度
        if max_score == 0:
            category = '其它'
            confidence = 0.0
        else:
            # 找到分数最高的分类
            for cat, score in scores.items():
                if score == max_score:
                    category = cat
                    break

            # 置信度 = 最高分 / 总分
            confidence = max_score / total_score if total_score > 0 else 0.0

        return {
            'category': category,
            'confidence': confidence,
            'scores': scores
        }

