"""
项目与标段匹配模块
用于在导入 Word 文档时，智能匹配项目和标段信息
"""

import sqlite3
import re
from typing import Dict, List, Optional
from difflib import SequenceMatcher


class ProjectSectionMatcher:
    """项目与标段匹配器"""

    def __init__(self, db_path: str):
        """
        初始化匹配器

        Args:
            db_path: 数据库路径
        """
        self.db_path = db_path

    def match_project(self, project_name: str) -> Dict:
        """
        匹配项目名

        Args:
            project_name: 识别出的项目名

        Returns:
            {
                'status': 'exact' | 'similar' | 'new' | 'error',
                'project_id': int (如果匹配到),
                'project_name': str,
                'message': str
            }
        """
        try:
            if not project_name or not project_name.strip():
                return {
                    'status': 'error',
                    'message': '项目名为空'
                }

            project_name = project_name.strip()

            # 查询所有项目
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT id, project_name FROM projects")
            all_projects = cursor.fetchall()
            conn.close()

            # 完全匹配
            for project_id, db_name in all_projects:
                if project_name == db_name:
                    return {
                        'status': 'exact',
                        'project_id': project_id,
                        'project_name': db_name,
                        'message': f'项目完全匹配：{db_name}'
                    }

            # 相近匹配
            similar = self._find_similar_project(project_name, all_projects)
            if similar:
                return {
                    'status': 'similar',
                    'project_id': similar['id'],
                    'project_name': similar['name'],
                    'message': f'项目相近匹配：识别为"{project_name}"，数据库中为"{similar["name"]}"'
                }

            # 新项目
            return {
                'status': 'new',
                'project_name': project_name,
                'message': f'新增项目：{project_name}'
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'项目匹配失败：{str(e)}'
            }

    def match_section(self, project_id: int, section_code: str, section_name: str = None) -> Dict:
        """
        匹配标段

        Args:
            project_id: 项目 ID
            section_code: 识别出的标段编号
            section_name: 识别出的标段名称（可选）

        Returns:
            {
                'status': 'exact' | 'similar' | 'new' | 'error',
                'section_id': int (如果匹配到),
                'section_code': str,
                'section_name': str,
                'message': str
            }
        """
        try:
            if not section_code or not section_code.strip():
                return {
                    'status': 'error',
                    'message': '标段编号为空'
                }

            section_code = section_code.strip()

            # 查询该项目的所有标段
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, section_name FROM sections WHERE project_id = ?",
                (project_id,)
            )
            all_sections = cursor.fetchall()
            conn.close()

            # 规范化标段编号（移除符号，转大写）
            normalized_code = self._normalize_section_code(section_code)

            # 完全匹配
            for section_id, db_name in all_sections:
                if normalized_code == self._normalize_section_code(db_name):
                    return {
                        'status': 'exact',
                        'section_id': section_id,
                        'section_code': section_code,
                        'section_name': db_name,
                        'message': f'标段完全匹配：{db_name}'
                    }

            # 相近匹配
            similar = self._find_similar_section(section_code, all_sections)
            if similar:
                return {
                    'status': 'similar',
                    'section_id': similar['id'],
                    'section_code': section_code,
                    'section_name': similar['name'],
                    'message': f'标段相近匹配：识别为"{section_code}"，数据库中为"{similar["name"]}"'
                }

            # 新标段
            return {
                'status': 'new',
                'section_code': section_code,
                'section_name': section_name or section_code,
                'message': f'新增标段：{section_code}'
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': f'标段匹配失败：{str(e)}'
            }

    def _find_similar_project(self, project_name: str, all_projects: List) -> Optional[Dict]:
        """查找相似的项目"""
        best_match = None
        best_score = 0.6  # 相似度阈值

        for project_id, db_name in all_projects:
            # 计算相似度
            score = SequenceMatcher(None, project_name.lower(), db_name.lower()).ratio()
            if score > best_score:
                best_score = score
                best_match = {'id': project_id, 'name': db_name}

        return best_match

    def _find_similar_section(self, section_code: str, all_sections: List) -> Optional[Dict]:
        """查找相似的标段"""
        best_match = None
        best_score = 0.7  # 相似度阈值

        normalized_code = self._normalize_section_code(section_code)

        for section_id, db_name in all_sections:
            # 计算相似度
            score = SequenceMatcher(None, normalized_code.lower(), self._normalize_section_code(db_name).lower()).ratio()
            if score > best_score:
                best_score = score
                best_match = {'id': section_id, 'name': db_name}

        return best_match

    def _normalize_section_code(self, code: str) -> str:
        """规范化标段编号（移除符号，转大写）"""
        # 移除所有非字母数字字符
        normalized = re.sub(r'[^a-zA-Z0-9]', '', code)
        return normalized.upper()

