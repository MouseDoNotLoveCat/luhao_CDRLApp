"""
FastAPI 主应用
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import tempfile
import shutil
from typing import List, Dict

from .services.import_service import ImportService
from .services.project_section_matcher import ProjectSectionMatcher


# 请求模型
class ImportSelectedRequest(BaseModel):
    """导入选中记录的请求模型"""
    notice_data: Dict
    selected_issue_ids: List[str]

# 创建应用
app = FastAPI(
    title="CDRL API",
    description="工程隐患库管理应用 API",
    version="1.0.0"
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 获取数据库路径
DB_PATH = Path(__file__).parent.parent / "cdrl.db"


@app.get("/")
async def root():
    """根路由"""
    return {
        "message": "CDRL API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/api/import/recognize")
async def recognize_document(file: UploadFile = File(...)):
    """
    识别 Word 文档（只识别不导入）

    Args:
        file: Word 文件

    Returns:
        识别结果（包含通知书和问题列表）
    """
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # 识别文档
        service = ImportService(str(DB_PATH))
        result = service.recognize_word_document(tmp_path)

        # 删除临时文件
        Path(tmp_path).unlink()

        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/import/document")
async def import_document(file: UploadFile = File(...)):
    """
    导入单个 Word 文档

    Args:
        file: Word 文件

    Returns:
        导入结果
    """
    try:
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name

        # 导入文档
        service = ImportService(str(DB_PATH))
        result = service.import_word_document(tmp_path)

        # 删除临时文件
        Path(tmp_path).unlink()

        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/import/batch")
async def import_batch(files: List[UploadFile] = File(...)):
    """
    批量导入 Word 文档

    Args:
        files: Word 文件列表

    Returns:
        批量导入结果
    """
    try:
        # 创建临时目录
        tmp_dir = tempfile.mkdtemp()

        # 保存所有文件
        for file in files:
            content = await file.read()
            file_path = Path(tmp_dir) / file.filename
            with open(file_path, 'wb') as f:
                f.write(content)

        # 批量导入
        service = ImportService(str(DB_PATH))
        result = service.import_batch_documents(tmp_dir)

        # 删除临时目录
        shutil.rmtree(tmp_dir)

        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/import/selected")
async def import_selected(request: ImportSelectedRequest):
    """
    导入选中的问题

    Args:
        request: 包含通知书数据和选中的问题 ID 列表

    Returns:
        导入结果
    """
    try:
        service = ImportService(str(DB_PATH))
        result = service.import_selected_issues(
            request.notice_data,
            request.selected_issue_ids
        )
        return result

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/statistics")
async def get_statistics():
    """
    获取统计信息
    
    Returns:
        统计数据
    """
    try:
        import sqlite3
        
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # 获取通知书数量
        cursor.execute("SELECT COUNT(*) FROM supervision_notices")
        notice_count = cursor.fetchone()[0]
        
        # 获取问题数量
        cursor.execute("SELECT COUNT(*) FROM issues")
        issue_count = cursor.fetchone()[0]
        
        # 获取下发整改通知单数量
        cursor.execute(
            "SELECT COUNT(*) FROM issues WHERE is_rectification_notice = 1"
        )
        rectification_count = cursor.fetchone()[0]
        
        # 获取其它问题数量
        cursor.execute(
            "SELECT COUNT(*) FROM issues WHERE is_rectification_notice = 0"
        )
        other_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'supervision_notices': notice_count,
            'total_issues': issue_count,
            'rectification_notices': rectification_count,
            'other_issues': other_count
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/issues")
async def get_issues(
    limit: int = 10,
    offset: int = 0,
    is_rectification: bool = None
):
    """
    获取问题列表

    Args:
        limit: 限制数量
        offset: 偏移量
        is_rectification: 是否下发整改通知单

    Returns:
        问题列表
    """
    try:
        import sqlite3

        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 构建基础查询（包含 JOIN 获取项目和标段信息）
        base_query = """
            SELECT i.id, i.issue_number, i.description, i.is_rectification_notice,
                   i.document_section, i.severity, i.site_name, i.issue_category,
                   i.issue_type_level1, i.issue_type_level2, i.inspection_date,
                   i.inspection_unit, i.inspection_personnel,
                   i.rectification_requirements, i.rectification_deadline,
                   i.rectification_date, i.rectification_status,
                   i.closure_date, i.closure_status, i.closure_personnel,
                   i.responsible_unit, i.responsible_person,
                   i.is_bad_behavior_notice,
                   s.section_name, p.project_name,
                   sn.check_date as notice_check_date, sn.check_unit as notice_check_unit
            FROM issues i
            LEFT JOIN sections s ON i.section_id = s.id
            LEFT JOIN projects p ON s.project_id = p.id
            LEFT JOIN supervision_notices sn ON i.supervision_notice_id = sn.id
        """

        if is_rectification is not None:
            cursor.execute(base_query + """
                WHERE i.is_rectification_notice = ?
                ORDER BY i.id DESC
                LIMIT ? OFFSET ?
            """, (1 if is_rectification else 0, limit, offset))
        else:
            cursor.execute(base_query + """
                ORDER BY i.id DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/issues/{issue_id}")
async def get_issue_detail(issue_id: int):
    """
    获取问题详情

    Args:
        issue_id: 问题 ID

    Returns:
        问题详情
    """
    try:
        import sqlite3

        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                i.*,
                s.section_name,
                s.section_code,
                p.project_name,
                p.builder_unit,
                sn.check_date,
                sn.check_unit
            FROM issues i
            LEFT JOIN sections s ON i.section_id = s.id
            LEFT JOIN projects p ON s.project_id = p.id
            LEFT JOIN supervision_notices sn ON i.supervision_notice_id = sn.id
            WHERE i.id = ?
        """, (issue_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="问题不存在")

        return dict(row)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 通知书管理 API ====================

@app.get("/api/notices")
async def get_notices(search: str = "", limit: int = 20, offset: int = 0):
    """
    获取通知书列表

    Args:
        search: 搜索关键词（通知书编号或项目名称）
        limit: 每页数量
        offset: 偏移量

    Returns:
        通知书列表和总数
    """
    try:
        import sqlite3

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # 构建查询条件
        where_clause = ""
        params = []
        if search:
            where_clause = "WHERE n.notice_number LIKE ?"
            params = [f"%{search}%"]

        # 获取总数
        count_query = f"SELECT COUNT(*) FROM supervision_notices n {where_clause}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]

        # 获取列表（包含问题数量）
        query = f"""
            SELECT
                n.id,
                n.notice_number,
                n.check_date,
                n.check_unit,
                COUNT(i.id) as issues_count,
                n.created_at
            FROM supervision_notices n
            LEFT JOIN issues i ON n.id = i.supervision_notice_id
            {where_clause}
            GROUP BY n.id
            ORDER BY n.created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [limit, offset])
        rows = cursor.fetchall()
        conn.close()

        return {
            'total': total,
            'data': [
                {
                    'id': row[0],
                    'notice_number': row[1],
                    'check_date': row[2],
                    'check_unit': row[3],
                    'issues_count': row[4],
                    'created_at': row[5]
                }
                for row in rows
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/notices/{notice_id}")
async def get_notice(notice_id: int):
    """
    获取通知书详情及其关联的问题列表

    Args:
        notice_id: 通知书 ID

    Returns:
        通知书详情和问题列表
    """
    try:
        import sqlite3

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # 获取通知书信息
        cursor.execute("""
            SELECT id, notice_number, check_date, check_unit, check_personnel, inspection_basis, created_at
            FROM supervision_notices
            WHERE id = ?
        """, (notice_id,))
        notice_row = cursor.fetchone()

        if not notice_row:
            conn.close()
            raise HTTPException(status_code=404, detail="通知书不存在")

        # 获取关联的问题列表（包含项目和标段信息）
        cursor.execute("""
            SELECT i.id, i.site_name, i.description, i.issue_category, i.issue_type_level1, i.issue_type_level2,
                   i.severity, i.rectification_deadline, i.is_rectification_notice,
                   i.document_section, i.created_at, sn.check_date, sn.check_unit,
                   s.section_name, p.project_name
            FROM issues i
            LEFT JOIN supervision_notices sn ON i.supervision_notice_id = sn.id
            LEFT JOIN sections s ON i.section_id = s.id
            LEFT JOIN projects p ON s.project_id = p.id
            WHERE i.supervision_notice_id = ?
            ORDER BY i.created_at DESC
        """, (notice_id,))
        issues_rows = cursor.fetchall()
        conn.close()

        return {
            'id': notice_row[0],
            'notice_number': notice_row[1],
            'check_date': notice_row[2],
            'check_unit': notice_row[3],
            'check_personnel': notice_row[4],
            'inspection_basis': notice_row[5],
            'created_at': notice_row[6],
            'issues': [
                {
                    'id': row[0],
                    'site_name': row[1],
                    'description': row[2],
                    'issue_category': row[3],
                    'issue_type_level1': row[4],
                    'issue_type_level2': row[5],
                    'severity': row[6],
                    'rectification_deadline': row[7],
                    'is_rectification': row[8],
                    'document_section': row[9],
                    'created_at': row[10],
                    'check_date': row[11],
                    'check_unit': row[12],
                    'section_name': row[13],
                    'project_name': row[14]
                }
                for row in issues_rows
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/notices/{notice_id}")
async def delete_notice(notice_id: int):
    """
    删除通知书及其关联的所有问题

    Args:
        notice_id: 通知书 ID

    Returns:
        删除结果
    """
    try:
        import sqlite3

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # 检查通知书是否存在
        cursor.execute("SELECT id FROM supervision_notices WHERE id = ?", (notice_id,))
        if not cursor.fetchone():
            conn.close()
            raise HTTPException(status_code=404, detail="通知书不存在")

        # 获取所有关联的问题 ID
        cursor.execute("SELECT id FROM issues WHERE supervision_notice_id = ?", (notice_id,))
        issue_ids = [row[0] for row in cursor.fetchall()]

        # 删除关联的数据
        for issue_id in issue_ids:
            # 删除处罚措施
            cursor.execute("DELETE FROM issue_penalties WHERE issue_id = ?", (issue_id,))
            # 删除责任单位
            cursor.execute("DELETE FROM responsibility_units WHERE issue_id = ?", (issue_id,))
            # 删除问题图片
            cursor.execute("DELETE FROM issue_images WHERE issue_id = ?", (issue_id,))

        # 删除问题
        cursor.execute("DELETE FROM issues WHERE supervision_notice_id = ?", (notice_id,))

        # 删除通知书
        cursor.execute("DELETE FROM supervision_notices WHERE id = ?", (notice_id,))

        conn.commit()
        conn.close()

        return {
            'success': True,
            'message': '通知书及其关联数据已删除'
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 项目管理 API ====================

@app.get("/api/projects")
async def get_projects(search: str = "", limit: int = 100, offset: int = 0):
    """
    获取项目列表

    Args:
        search: 搜索关键词（项目名称或建设单位）
        limit: 限制数量
        offset: 偏移量

    Returns:
        项目列表
    """
    try:
        import sqlite3

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # 构建查询条件
        where_clause = ""
        params = []
        if search:
            where_clause = "WHERE project_name LIKE ? OR builder_unit LIKE ?"
            params = [f"%{search}%", f"%{search}%"]

        # 获取总数
        count_query = f"SELECT COUNT(*) FROM projects {where_clause}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]

        # 获取列表
        query = f"""
            SELECT p.id, p.project_name, p.builder_unit, COUNT(s.id) as sections_count
            FROM projects p
            LEFT JOIN sections s ON p.id = s.project_id
            {where_clause}
            GROUP BY p.id
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [limit, offset])
        rows = cursor.fetchall()
        conn.close()

        return {
            'total': total,
            'data': [
                {
                    'id': row[0],
                    'project_name': row[1],
                    'builder_unit': row[2],
                    'sections_count': row[3]
                }
                for row in rows
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/projects/{project_id}")
async def get_project(project_id: int):
    """
    获取单个项目详情

    Args:
        project_id: 项目 ID

    Returns:
        项目详情
    """
    try:
        import sqlite3

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, project_name, builder_unit, created_at, updated_at
            FROM projects
            WHERE id = ?
        """, (project_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="项目不存在")

        return {
            'id': row[0],
            'project_name': row[1],
            'builder_unit': row[2],
            'created_at': row[3],
            'updated_at': row[4]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/projects")
async def create_project(project_name: str, builder_unit: str = ""):
    """
    新建项目

    Args:
        project_name: 项目名称
        builder_unit: 建设单位

    Returns:
        新建的项目
    """
    try:
        import sqlite3

        if not project_name or not project_name.strip():
            raise HTTPException(status_code=400, detail="项目名称不能为空")

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO projects (project_name, builder_unit)
                VALUES (?, ?)
            """, (project_name, builder_unit))

            conn.commit()
            project_id = cursor.lastrowid

            return {
                'id': project_id,
                'project_name': project_name,
                'builder_unit': builder_unit,
                'sections_count': 0,
                'message': '项目创建成功'
            }
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="项目名称已存在")
        finally:
            conn.close()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/projects/{project_id}")
async def update_project(project_id: int, project_name: str, builder_unit: str = ""):
    """
    修改项目

    Args:
        project_id: 项目 ID
        project_name: 项目名称
        builder_unit: 建设单位

    Returns:
        修改后的项目
    """
    try:
        import sqlite3

        if not project_name or not project_name.strip():
            raise HTTPException(status_code=400, detail="项目名称不能为空")

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        try:
            cursor.execute("""
                UPDATE projects
                SET project_name = ?, builder_unit = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (project_name, builder_unit, project_id))

            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="项目不存在")

            conn.commit()

            return {
                'id': project_id,
                'project_name': project_name,
                'builder_unit': builder_unit,
                'message': '项目修改成功'
            }
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="项目名称已存在")
        finally:
            conn.close()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: int, cascade: bool = False):
    """
    删除项目

    Args:
        project_id: 项目 ID
        cascade: 是否级联删除标段

    Returns:
        删除结果
    """
    try:
        import sqlite3

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # 检查项目是否存在
        cursor.execute("SELECT id FROM projects WHERE id = ?", (project_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="项目不存在")

        # 检查是否有标段
        cursor.execute("SELECT COUNT(*) FROM sections WHERE project_id = ?", (project_id,))
        sections_count = cursor.fetchone()[0]

        if sections_count > 0 and not cascade:
            conn.close()
            return {
                'success': False,
                'message': f'该项目下有 {sections_count} 个标段，请确认是否级联删除',
                'sections_count': sections_count
            }

        # 删除标段（如果级联）
        if cascade and sections_count > 0:
            cursor.execute("DELETE FROM sections WHERE project_id = ?", (project_id,))

        # 删除项目
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()
        conn.close()

        return {
            'success': True,
            'message': '项目删除成功',
            'deleted_sections': sections_count if cascade else 0
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 标段管理 API ====================

@app.get("/api/projects/{project_id}/sections")
async def get_sections(project_id: int, search: str = "", limit: int = 100, offset: int = 0):
    """
    获取某项目的标段列表

    Args:
        project_id: 项目 ID
        search: 搜索关键词
        limit: 限制数量
        offset: 偏移量

    Returns:
        标段列表
    """
    try:
        import sqlite3

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # 检查项目是否存在
        cursor.execute("SELECT id FROM projects WHERE id = ?", (project_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="项目不存在")

        # 构建查询条件
        where_clause = "WHERE project_id = ?"
        params = [project_id]

        if search:
            where_clause += " AND (section_name LIKE ? OR contractor_unit LIKE ? OR supervisor_unit LIKE ? OR designer_unit LIKE ? OR testing_unit LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param] * 5)

        # 获取总数
        count_query = f"SELECT COUNT(*) FROM sections {where_clause}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]

        # 获取列表
        query = f"""
            SELECT id, project_id, section_name, contractor_unit, supervisor_unit, designer_unit, testing_unit, created_at, updated_at
            FROM sections
            {where_clause}
            ORDER BY section_name ASC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [limit, offset])
        rows = cursor.fetchall()
        conn.close()

        return {
            'total': total,
            'data': [
                {
                    'id': row[0],
                    'project_id': row[1],
                    'section_name': row[2],
                    'contractor_unit': row[3],
                    'supervisor_unit': row[4],
                    'designer_unit': row[5],
                    'testing_unit': row[6],
                    'created_at': row[7],
                    'updated_at': row[8]
                }
                for row in rows
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sections/{section_id}")
async def get_section(section_id: int):
    """
    获取单个标段详情

    Args:
        section_id: 标段 ID

    Returns:
        标段详情
    """
    try:
        import sqlite3

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, project_id, section_name, contractor_unit, supervisor_unit, designer_unit, testing_unit, created_at, updated_at
            FROM sections
            WHERE id = ?
        """, (section_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="标段不存在")

        return {
            'id': row[0],
            'project_id': row[1],
            'section_name': row[2],
            'contractor_unit': row[3],
            'supervisor_unit': row[4],
            'designer_unit': row[5],
            'testing_unit': row[6],
            'created_at': row[7],
            'updated_at': row[8]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sections")
async def create_section(
    project_id: int,
    section_name: str,
    contractor_unit: str = "",
    supervisor_unit: str = "",
    designer_unit: str = "",
    testing_unit: str = ""
):
    """
    新建标段

    Args:
        project_id: 项目 ID
        section_name: 标段名称
        contractor_unit: 施工单位
        supervisor_unit: 监理单位
        designer_unit: 设计单位
        testing_unit: 第三方检测单位

    Returns:
        新建的标段
    """
    try:
        import sqlite3

        if not section_name or not section_name.strip():
            raise HTTPException(status_code=400, detail="标段名称不能为空")

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # 检查项目是否存在
        cursor.execute("SELECT id FROM projects WHERE id = ?", (project_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="项目不存在")

        try:
            cursor.execute("""
                INSERT INTO sections (project_id, section_name, contractor_unit, supervisor_unit, designer_unit, testing_unit)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (project_id, section_name, contractor_unit, supervisor_unit, designer_unit, testing_unit))

            conn.commit()
            section_id = cursor.lastrowid

            return {
                'id': section_id,
                'project_id': project_id,
                'section_name': section_name,
                'contractor_unit': contractor_unit,
                'supervisor_unit': supervisor_unit,
                'designer_unit': designer_unit,
                'testing_unit': testing_unit,
                'message': '标段创建成功'
            }
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="该项目下标段名称已存在")
        finally:
            conn.close()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/sections/{section_id}")
async def update_section(
    section_id: int,
    section_name: str,
    contractor_unit: str = "",
    supervisor_unit: str = "",
    designer_unit: str = "",
    testing_unit: str = ""
):
    """
    修改标段

    Args:
        section_id: 标段 ID
        section_name: 标段名称
        contractor_unit: 施工单位
        supervisor_unit: 监理单位
        designer_unit: 设计单位
        testing_unit: 第三方检测单位

    Returns:
        修改后的标段
    """
    try:
        import sqlite3

        if not section_name or not section_name.strip():
            raise HTTPException(status_code=400, detail="标段名称不能为空")

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # 检查标段是否存在
        cursor.execute("SELECT project_id FROM sections WHERE id = ?", (section_id,))
        result = cursor.fetchone()
        if not result:
            raise HTTPException(status_code=404, detail="标段不存在")

        project_id = result[0]

        try:
            cursor.execute("""
                UPDATE sections
                SET section_name = ?, contractor_unit = ?, supervisor_unit = ?, designer_unit = ?, testing_unit = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (section_name, contractor_unit, supervisor_unit, designer_unit, testing_unit, section_id))

            conn.commit()

            return {
                'id': section_id,
                'project_id': project_id,
                'section_name': section_name,
                'contractor_unit': contractor_unit,
                'supervisor_unit': supervisor_unit,
                'designer_unit': designer_unit,
                'testing_unit': testing_unit,
                'message': '标段修改成功'
            }
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=400, detail="该项目下标段名称已存在")
        finally:
            conn.close()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/sections/{section_id}")
async def delete_section(section_id: int):
    """
    删除标段

    Args:
        section_id: 标段 ID

    Returns:
        删除结果
    """
    try:
        import sqlite3

        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # 检查标段是否存在
        cursor.execute("SELECT id FROM sections WHERE id = ?", (section_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="标段不存在")

        # 删除标段
        cursor.execute("DELETE FROM sections WHERE id = ?", (section_id,))
        conn.commit()
        conn.close()

        return {
            'success': True,
            'message': '标段删除成功'
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 项目与标段匹配 API ====================

@app.post("/api/match/project")
async def match_project(project_name: str):
    """
    匹配项目名

    Args:
        project_name: 识别出的项目名

    Returns:
        匹配结果
    """
    try:
        matcher = ProjectSectionMatcher(str(DB_PATH))
        result = matcher.match_project(project_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/match/section")
async def match_section(project_id: int, section_code: str, section_name: str = None):
    """
    匹配标段

    Args:
        project_id: 项目 ID
        section_code: 识别出的标段编号
        section_name: 识别出的标段名称（可选）

    Returns:
        匹配结果
    """
    try:
        matcher = ProjectSectionMatcher(str(DB_PATH))
        result = matcher.match_section(project_id, section_code, section_name)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

