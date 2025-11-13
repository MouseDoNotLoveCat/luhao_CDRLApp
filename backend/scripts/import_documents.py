#!/usr/bin/env python3
"""
批量导入 Word 文档脚本
"""

import sys
import json
from pathlib import Path

# 添加后端路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.import_service import ImportService


def main():
    """主函数"""
    
    # 获取路径
    backend_dir = Path(__file__).parent.parent
    db_path = backend_dir / "cdrl.db"
    samples_dir = Path(__file__).parent.parent.parent / "Samples"
    
    print("=" * 80)
    print("📥 批量导入 Word 文档")
    print("=" * 80)
    print()
    
    # 检查数据库
    if not db_path.exists():
        print(f"❌ 数据库不存在: {db_path}")
        print("请先运行: python scripts/init_db.py")
        return
    
    print(f"✅ 数据库: {db_path}")
    print(f"✅ 文件夹: {samples_dir}")
    print()
    
    # 创建导入服务
    service = ImportService(str(db_path))
    
    # 批量导入
    print("📥 开始导入...")
    print()
    
    results = service.import_batch_documents(str(samples_dir))
    
    # 显示结果
    print("=" * 80)
    print("📊 导入结果")
    print("=" * 80)
    print()
    print(f"总文件数: {results['total_files']}")
    print(f"成功: {results['successful']}")
    print(f"失败: {results['failed']}")
    print(f"总问题数: {results['total_issues']}")
    print()
    
    # 显示详细信息
    print("=" * 80)
    print("📋 详细信息")
    print("=" * 80)
    print()
    
    for i, detail in enumerate(results['details'], 1):
        print(f"{i}. {detail['file_name']}")
        
        if detail['success']:
            print(f"   ✅ 成功")
            print(f"   编号: {detail['notice_number']}")
            print(f"   下发整改通知单: {detail['rectification_notices']}")
            print(f"   其它问题: {detail['other_issues']}")
            print(f"   总计: {detail['total_issues']}")
        else:
            print(f"   ❌ 失败")
            print(f"   错误: {detail['error']}")
        
        print()
    
    print("=" * 80)
    print("✅ 导入完成")
    print("=" * 80)


if __name__ == "__main__":
    main()

