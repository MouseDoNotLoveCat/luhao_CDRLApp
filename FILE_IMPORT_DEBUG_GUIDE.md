# 文件导入功能调试指南

## 问题现象
- 点击"导入文件"按钮后，界面卡在"识别过程中"
- 浏览器 Network 标签显示 response 为空
- 怀疑后端未收到请求

## 已实施的改进

### 前端改进
1. **importStore.js** - 添加详细的识别过程日志
2. **importService.js** - 添加请求/响应日志
3. **api.js** - 改进拦截器日志，增加超时时间（30s→60s）

### 后端改进
1. **main.py** - 添加请求接收、处理、错误日志

## 快速调试步骤

### 1. 启动应用
```bash
./start-dev.sh
```

### 2. 打开浏览器
- 访问 http://localhost:3000
- 按 F12 打开开发者工具
- 切换到 Console 标签

### 3. 测试导入
1. 选择 .docx 文件
2. 点击"导入文件"
3. 观察日志输出

## 日志分析

### 前端日志应该显示
```
🔄 开始识别文件: xxx.docx 大小: xxxxx
📤 发送 API 请求: {...}
📤 发送识别请求: {...}
📥 收到识别响应: {...}
✅ API 响应成功: {...}
📦 收到识别结果: {...}
✅ 识别成功，问题数: xxx
```

### 后端日志应该显示
```
📥 收到识别请求: xxx.docx, 大小: xxxxx
📝 临时文件已创建: /tmp/xxx.docx
✅ 识别成功: xxx 个问题
```

## 问题排查

### 如果前端日志显示请求已发送，但后端无日志
- 检查 Vite 代理配置 (vite.config.js)
- 检查网络连接
- 检查浏览器 Network 标签

### 如果后端日志显示识别失败
- 查看错误堆栈跟踪
- 检查文件格式是否正确
- 检查数据库连接

### 如果前端收到响应但显示错误
- 检查响应中是否包含 `success` 字段
- 检查错误信息内容
- 查看浏览器 Network 标签的响应内容

## 文件修改清单
- ✅ frontend/src/stores/importStore.js
- ✅ frontend/src/services/importService.js
- ✅ frontend/src/services/api.js
- ✅ backend/app/main.py

## 下一步
1. 运行应用并测试
2. 收集日志信息
3. 根据日志分析具体问题

