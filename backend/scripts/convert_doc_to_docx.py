#!/usr/bin/env python3
"""
将 .doc 文件转换为 .docx 格式
"""

import subprocess
from pathlib import Path


def convert_doc_to_docx(doc_file: str) -> bool:
    """
    使用 LibreOffice 将 .doc 转换为 .docx
    
    Args:
        doc_file: .doc 文件路径
    
    Returns:
        是否成功
    """
    try:
        doc_path = Path(doc_file)
        output_dir = doc_path.parent
        
        # 使用 LibreOffice 转换
        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to', 'docx',
            '--outdir', str(output_dir),
            str(doc_path)
        ]
        
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        
        if result.returncode == 0:
            print(f"✅ 转换成功: {doc_path.name}")
            return True
        else:
            print(f"❌ 转换失败: {doc_path.name}")
            print(f"   错误: {result.stderr.decode()}")
            return False
            
    except FileNotFoundError:
        print("❌ LibreOffice 未安装")
        return False
    except Exception as e:
        print(f"❌ 转换出错: {e}")
        return False


def main():
    """主函数"""
    
    samples_dir = Path(__file__).parent.parent.parent / "Samples"
    
    print("=" * 80)
    print("🔄 转换 .doc 文件为 .docx")
    print("=" * 80)
    print()
    
    # 查找所有 .doc 文件
    doc_files = list(samples_dir.glob('*.doc'))
    doc_files = [f for f in doc_files if not f.name.startswith('~$')]
    
    print(f"找到 {len(doc_files)} 个 .doc 文件")
    print()
    
    success_count = 0
    for doc_file in doc_files:
        if convert_doc_to_docx(str(doc_file)):
            success_count += 1
    
    print()
    print("=" * 80)
    print(f"✅ 转换完成: {success_count}/{len(doc_files)}")
    print("=" * 80)


if __name__ == "__main__":
    main()

