#!/usr/bin/env python3
"""
调试文件导入功能的脚本
"""

import sys
import os

# 添加后端路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.main import app
from fastapi.testclient import TestClient

# 创建测试客户端
client = TestClient(app)

print("=" * 60)
print("🔍 调试文件导入功能")
print("=" * 60)

# 测试 1: 检查 API 路由
print("\n✅ 测试 1: 检查 API 路由")
print("-" * 60)

# 获取所有路由
routes = []
for route in app.routes:
    if hasattr(route, 'path'):
        routes.append(f"{route.methods if hasattr(route, 'methods') else 'N/A'} {route.path}")

# 查找导入相关的路由
import_routes = [r for r in routes if 'import' in r.lower()]
print(f"导入相关的路由:")
for route in import_routes:
    print(f"  - {route}")

# 测试 2: 检查后端是否能加载
print("\n✅ 测试 2: 检查后端应用")
print("-" * 60)
print(f"应用名称: {app.title}")
print(f"应用版本: {app.version}")
print(f"总路由数: {len(app.routes)}")

# 测试 3: 测试根路由
print("\n✅ 测试 3: 测试根路由")
print("-" * 60)
response = client.get("/")
print(f"状态码: {response.status_code}")
print(f"响应: {response.json()}")

# 测试 4: 检查识别端点是否存在
print("\n✅ 测试 4: 检查识别端点")
print("-" * 60)
print("识别端点应该是: POST /import/recognize")
print("前端调用的 URL: /api/import/recognize")
print("Vite 代理应该将 /api 转发到后端")

print("\n" + "=" * 60)
print("✅ 调试完成")
print("=" * 60)

