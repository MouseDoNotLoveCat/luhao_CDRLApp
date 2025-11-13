#!/usr/bin/env python3
"""
交互式数据库查看工具
"""

import sqlite3
from pathlib import Path
from tabulate import tabulate


class DatabaseViewer:
    """数据库查看器"""
    
    def __init__(self, db_path: str):
        """初始化"""
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
    
    def show_menu(self):
        """显示菜单"""
        print("\n" + "=" * 80)
        print("📊 CDRL 数据库查看工具")
        print("=" * 80)
        print()
        print("1. 查看监督通知书")
        print("2. 查看隐患问题")
        print("3. 查看统计信息")
        print("4. 查看下发整改通知单的问题")
        print("5. 查看其它问题")
        print("6. 按通知书统计")
        print("7. 按严重程度统计")
        print("8. 按分类统计")
        print("9. 导出为 CSV")
        print("0. 退出")
        print()
    
    def view_notices(self):
        """查看监督通知书"""
        print("\n📋 监督通知书")
        print("-" * 80)
        
        self.cursor.execute("""
            SELECT id, notice_number, check_date, check_unit, check_personnel
            FROM supervision_notices
            ORDER BY check_date DESC
        """)
        
        rows = self.cursor.fetchall()
        headers = ['ID', '编号', '检查日期', '检查单位', '检查人员']
        print(tabulate(rows, headers=headers, tablefmt='grid'))
        print(f"\n总计: {len(rows)} 条")
    
    def view_issues(self):
        """查看隐患问题"""
        print("\n🔍 隐患问题（前 20 条）")
        print("-" * 80)
        
        self.cursor.execute("""
            SELECT id, issue_number, is_rectification_notice, severity, 
                   SUBSTR(description, 1, 50) as 描述
            FROM issues
            LIMIT 20
        """)
        
        rows = self.cursor.fetchall()
        headers = ['ID', '编号', '下发整改', '严重程度', '描述']
        print(tabulate(rows, headers=headers, tablefmt='grid'))
        print(f"\n总计: {len(rows)} 条（显示前 20 条）")
    
    def view_statistics(self):
        """查看统计信息"""
        print("\n📊 统计信息")
        print("-" * 80)
        
        # 通知书统计
        self.cursor.execute("SELECT COUNT(*) FROM supervision_notices")
        notice_count = self.cursor.fetchone()[0]
        
        # 问题统计
        self.cursor.execute("""
            SELECT 
              COUNT(*) as 总数,
              SUM(CASE WHEN is_rectification_notice = 1 THEN 1 ELSE 0 END) as 下发整改,
              SUM(CASE WHEN is_rectification_notice = 0 THEN 1 ELSE 0 END) as 其它问题
            FROM issues
        """)
        row = self.cursor.fetchone()
        
        print(f"监督通知书: {notice_count} 条")
        print(f"隐患问题总数: {row[0]} 条")
        print(f"  ├─ 下发整改通知单: {row[1]} 条")
        print(f"  └─ 其它问题: {row[2]} 条")
    
    def view_rectification_notices(self):
        """查看下发整改通知单的问题"""
        print("\n✅ 下发整改通知单的问题（前 10 条）")
        print("-" * 80)
        
        self.cursor.execute("""
            SELECT id, issue_number, SUBSTR(description, 1, 60) as 描述
            FROM issues
            WHERE is_rectification_notice = 1
            LIMIT 10
        """)
        
        rows = self.cursor.fetchall()
        headers = ['ID', '编号', '描述']
        print(tabulate(rows, headers=headers, tablefmt='grid'))
        print(f"\n总计: {len(rows)} 条（显示前 10 条）")
    
    def view_other_issues(self):
        """查看其它问题"""
        print("\n❌ 其它问题（前 10 条）")
        print("-" * 80)
        
        self.cursor.execute("""
            SELECT id, issue_number, SUBSTR(description, 1, 60) as 描述
            FROM issues
            WHERE is_rectification_notice = 0
            LIMIT 10
        """)
        
        rows = self.cursor.fetchall()
        headers = ['ID', '编号', '描述']
        print(tabulate(rows, headers=headers, tablefmt='grid'))
        print(f"\n总计: {len(rows)} 条（显示前 10 条）")
    
    def view_by_notice(self):
        """按通知书统计"""
        print("\n📋 按通知书统计")
        print("-" * 80)
        
        self.cursor.execute("""
            SELECT 
              s.notice_number,
              COUNT(i.id) as 问题数,
              SUM(CASE WHEN i.is_rectification_notice = 1 THEN 1 ELSE 0 END) as 下发整改,
              SUM(CASE WHEN i.is_rectification_notice = 0 THEN 1 ELSE 0 END) as 其它问题
            FROM supervision_notices s
            LEFT JOIN issues i ON s.id = i.supervision_notice_id
            GROUP BY s.id
            ORDER BY COUNT(i.id) DESC
        """)
        
        rows = self.cursor.fetchall()
        headers = ['通知书编号', '问题数', '下发整改', '其它问题']
        print(tabulate(rows, headers=headers, tablefmt='grid'))
    
    def view_by_severity(self):
        """按严重程度统计"""
        print("\n📊 按严重程度统计")
        print("-" * 80)
        
        self.cursor.execute("""
            SELECT severity, COUNT(*) as 数量
            FROM issues
            GROUP BY severity
            ORDER BY severity
        """)
        
        rows = self.cursor.fetchall()
        headers = ['严重程度', '数量']
        print(tabulate(rows, headers=headers, tablefmt='grid'))
    
    def view_by_category(self):
        """按分类统计"""
        print("\n📊 按分类统计")
        print("-" * 80)
        
        self.cursor.execute("""
            SELECT issue_category, COUNT(*) as 数量
            FROM issues
            WHERE issue_category IS NOT NULL
            GROUP BY issue_category
        """)
        
        rows = self.cursor.fetchall()
        headers = ['分类', '数量']
        print(tabulate(rows, headers=headers, tablefmt='grid'))
    
    def export_csv(self):
        """导出为 CSV"""
        print("\n💾 导出为 CSV")
        print("-" * 80)
        
        try:
            import csv
            
            # 导出通知书
            self.cursor.execute("SELECT * FROM supervision_notices")
            rows = self.cursor.fetchall()
            
            with open('supervision_notices.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', '编号', '检查日期', '检查单位', '检查人员', '创建时间', '更新时间'])
                writer.writerows(rows)
            
            print("✅ 导出成功: supervision_notices.csv")
            
            # 导出问题
            self.cursor.execute("SELECT * FROM issues LIMIT 100")
            rows = self.cursor.fetchall()
            
            with open('issues.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', '编号', '通知书ID', '工点ID', '分类', '子分类', '描述', '下发整改', '其它字段...'])
                writer.writerows(rows)
            
            print("✅ 导出成功: issues.csv")
            
        except Exception as e:
            print(f"❌ 导出失败: {e}")
    
    def run(self):
        """运行交互式菜单"""
        while True:
            self.show_menu()
            choice = input("请选择 (0-9): ").strip()
            
            if choice == '1':
                self.view_notices()
            elif choice == '2':
                self.view_issues()
            elif choice == '3':
                self.view_statistics()
            elif choice == '4':
                self.view_rectification_notices()
            elif choice == '5':
                self.view_other_issues()
            elif choice == '6':
                self.view_by_notice()
            elif choice == '7':
                self.view_by_severity()
            elif choice == '8':
                self.view_by_category()
            elif choice == '9':
                self.export_csv()
            elif choice == '0':
                print("\n👋 再见！")
                break
            else:
                print("❌ 无效选择，请重试")
        
        self.conn.close()


def main():
    """主函数"""
    db_path = Path(__file__).parent.parent / "cdrl.db"
    
    if not db_path.exists():
        print(f"❌ 数据库不存在: {db_path}")
        return
    
    viewer = DatabaseViewer(str(db_path))
    viewer.run()


if __name__ == "__main__":
    main()

