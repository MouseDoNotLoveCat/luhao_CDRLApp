#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
导出 2026 年的问题数据到 Excel 文件
从 cdrl.db 数据库中导出 inspection_date 包含 "2026" 的所有问题记录
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

# 配置
DB_PATH = 'backend/cdrl.db'
OUTPUT_FILE = f'issues_2026_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'

def export_issues_to_excel():
    """导出问题数据到 Excel"""
    
    print(f"📂 连接数据库: {DB_PATH}")
    
    # 检查数据库文件是否存在
    if not os.path.exists(DB_PATH):
        print(f"❌ 错误: 数据库文件不存在: {DB_PATH}")
        return
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # 构建 SQL 查询，JOIN 关联表获取可读字段
        query = """
        SELECT 
            i.id AS '问题ID',
            i.issue_number AS '问题编号',
            sn.notice_number AS '通知书编号',
            sn.check_date AS '通知书检查日期',
            sn.check_unit AS '检查单位',
            p.project_name AS '项目名称',
            s.section_name AS '标段名称',
            i.site_name AS '工点名称',
            i.contractor AS '施工单位',
            i.supervisor AS '监理单位',
            i.issue_category AS '问题类别',
            i.issue_type_level1 AS '问题子类1',
            i.issue_type_level2 AS '问题子类2',
            i.description AS '问题描述',
            CASE i.severity
                WHEN 1 THEN '1-轻微'
                WHEN 2 THEN '2-一般'
                WHEN 3 THEN '3-中等'
                WHEN 4 THEN '4-严重'
                WHEN 5 THEN '5-极严重'
                ELSE '未设置'
            END AS '严重程度',
            i.keywords AS '关键词',
            i.inspection_unit AS '检查单位',
            i.inspection_date AS '检查时间',
            i.inspection_personnel AS '检查人员',
            i.rectification_requirements AS '整改要求',
            i.rectification_deadline AS '整改期限',
            i.rectification_date AS '整改完成日期',
            i.rectification_status AS '整改状态',
            i.closure_date AS '闭合日期',
            i.closure_status AS '闭合状态',
            i.closure_personnel AS '闭合人员',
            CASE WHEN i.is_rectification_notice = 1 THEN '是' ELSE '否' END AS '是否整改通知',
            CASE WHEN i.is_bad_behavior_notice = 1 THEN '是' ELSE '否' END AS '是否不良行为通知',
            i.responsible_unit AS '责任单位',
            i.responsible_person AS '责任人',
            i.document_section AS '文档章节',
            i.document_source AS '文档来源',
            i.created_at AS '创建时间',
            i.updated_at AS '更新时间'
        FROM issues i
        LEFT JOIN supervision_notices sn ON i.supervision_notice_id = sn.id
        LEFT JOIN sections s ON i.section_id = s.id
        LEFT JOIN projects p ON s.project_id = p.id
        WHERE i.inspection_date LIKE '%2026%'
        ORDER BY i.inspection_date, i.id
        """
        
        print("🔍 查询 2026 年的问题数据...")
        
        # 执行查询并读取到 DataFrame
        df = pd.read_sql_query(query, conn)
        
        print(f"✅ 找到 {len(df)} 条记录")
        
        if len(df) == 0:
            print("⚠️  没有找到 2026 年的问题数据")
            return
        
        # 导出到 Excel
        print(f"📝 导出到 Excel: {OUTPUT_FILE}")
        
        # 使用 openpyxl 引擎，支持更好的格式化
        with pd.ExcelWriter(OUTPUT_FILE, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='2026年问题数据', index=False)
            
            # 获取工作表对象
            worksheet = writer.sheets['2026年问题数据']
            
            # 自动调整列宽
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                
                for cell in column:
                    try:
                        if cell.value:
                            max_length = max(max_length, len(str(cell.value)))
                    except:
                        pass
                
                # 设置列宽，最小 10，最大 50
                adjusted_width = min(max(max_length + 2, 10), 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        print(f"✅ 导出成功！")
        print(f"📊 文件路径: {os.path.abspath(OUTPUT_FILE)}")
        print(f"📈 记录数量: {len(df)}")
        
        # 显示统计信息
        print("\n📊 数据统计:")
        print(f"  - 问题类别分布:")
        if '问题类别' in df.columns:
            for category, count in df['问题类别'].value_counts().items():
                print(f"    • {category}: {count} 个")
        
        print(f"\n  - 严重程度分布:")
        if '严重程度' in df.columns:
            for severity, count in df['严重程度'].value_counts().items():
                print(f"    • {severity}: {count} 个")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()
        print("\n🔒 数据库连接已关闭")

if __name__ == '__main__':
    print("=" * 60)
    print("📋 导出 2026 年问题数据到 Excel")
    print("=" * 60)
    print()
    
    export_issues_to_excel()
    
    print()
    print("=" * 60)
    print("✅ 完成！")
    print("=" * 60)

