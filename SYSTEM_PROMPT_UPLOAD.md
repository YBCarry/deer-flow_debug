# System Prompt File Upload 功能说明

## 概述

DeerFlow 新增了系统 Prompt 文件上传功能，允许用户通过 Web UI 界面管理和更新 AI 智能体的系统提示模板。此功能支持对话、计划、研究、编程和报告五个核心智能体的 Prompt 文件上传和管理。

## 功能特性

### 🎯 核心功能
- **在线上传**：通过 Web 界面直接上传和更新 Prompt 文件
- **文件预览**：查看现有 Prompt 文件的基本信息和内容预览
- **自动备份**：上传前自动备份现有文件，防止意外覆盖
- **实时验证**：上传过程中进行文件名和内容验证
- **状态反馈**：提供详细的上传状态和错误信息

### 📁 支持的文件类型
系统仅支持以下 5 个核心智能体的 Prompt 文件：

1. **coordinator.md** - 协调器智能体
2. **planner.md** - 规划器智能体  
3. **researcher.md** - 研究员智能体
4. **coder.md** - 编程助手智能体
5. **reporter.md** - 报告生成智能体

## 使用方法

### 1. 访问 Prompt 管理界面

1. 启动 DeerFlow Web 应用：
   ```bash
   # 启动完整开发环境
   ./bootstrap.sh -d
   
   # 或仅启动后端
   make serve
   
   # 单独启动前端 (在 web/ 目录下)
   cd web && pnpm dev
   ```

2. 打开浏览器访问 `http://localhost:3000`

3. 进入 **Settings** 设置页面

4. 点击 **Prompt Templates** 选项卡

### 2. 查看现有文件

在 "Current Prompt Files" 部分可以看到：
- 文件名和状态（Available/Not Found）
- 文件大小
- 最后修改时间
- 内容预览（前200个字符）

### 3. 上传新文件

在 "Upload Prompt File" 部分：

1. **选择文件**：从下拉菜单中选择要上传的 Prompt 文件名
   - coordinator.md
   - planner.md
   - researcher.md
   - coder.md
   - reporter.md

2. **输入内容**：在文本框中输入或粘贴 Prompt 内容
   - 支持 Markdown 格式
   - 内容不能为空
   - 建议使用清晰的结构化 Prompt

3. **执行上传**：点击 "Upload File" 按钮
   - 系统会自动验证文件名和内容
   - 现有文件会被自动备份到 `data/backups/` 目录
   - 上传成功后会显示成功提示

### 4. Prompt 编写建议

以下是编写高质量 Prompt 的建议：

```markdown
# 智能体名称

## 角色定义
明确定义智能体的角色和职责

## 核心能力
- 列出主要功能和技能
- 明确处理的任务类型

## 工作流程
1. 描述标准工作步骤
2. 说明决策逻辑
3. 定义输出格式

## 约束条件
- 明确限制和边界
- 定义不应执行的操作

## 示例
提供具体的输入输出示例
```

## API 接口

### 获取文件列表
```http
GET /api/prompts
```

**响应示例：**
```json
{
  "files": [
    {
      "filename": "coordinator.md",
      "size": 2048,
      "last_modified": "2025-01-15T10:30:00Z",
      "content_preview": "# Coordinator Agent\nYou are responsible for..."
    }
  ],
  "allowed_files": ["coordinator.md", "planner.md", "researcher.md", "coder.md", "reporter.md"]
}
```

### 上传文件
```http
POST /api/prompts/upload
Content-Type: application/json

{
  "filename": "coordinator.md",
  "content": "# Coordinator Agent\n\nYour detailed prompt content here..."
}
```

**响应示例：**
```json
{
  "success": true,
  "message": "Successfully uploaded coordinator.md",
  "filename": "coordinator.md"
}
```

## 文件结构

```
src/prompts/                    # Prompt 文件存储目录
├── coordinator.md              # 协调器 Prompt
├── planner.md                  # 规划器 Prompt
├── researcher.md               # 研究员 Prompt
├── coder.md                   # 编程助手 Prompt
└── reporter.md                 # 报告生成 Prompt

data/backups/                   # 自动备份目录
├── coordinator.md.1642234567.bak
├── planner.md.1642234890.bak
└── ...
```

## 技术实现

### 后端实现 (`src/server/app.py`)
- **GET /api/prompts**: 获取文件列表和基本信息
- **POST /api/prompts/upload**: 处理文件上传和备份逻辑
- 文件验证和安全检查
- 自动备份机制

### 前端实现 (`web/src/app/settings/tabs/prompt-tab.tsx`)
- React 组件实现的用户界面
- 文件选择和内容编辑
- 实时状态反馈和错误处理
- 响应式设计和用户体验优化

### 数据模型 (`src/server/prompt_request.py`)
- `PromptFileInfo`: 文件信息模型
- `PromptUploadRequest`: 上传请求模型
- `PromptUploadResponse`: 上传响应模型
- `PromptListResponse`: 文件列表响应模型

## 安全特性

### 文件安全
- **白名单机制**：仅允许上传预定义的 5 个文件
- **路径验证**：防止路径遍历攻击
- **内容检查**：验证文件内容不为空

### 备份保护
- **自动备份**：上传前自动备份现有文件
- **时间戳命名**：备份文件使用时间戳避免冲突
- **目录分离**：备份文件存储在独立目录

### 错误处理
- 详细的错误信息和状态码
- 前端用户友好的错误提示
- 后端完整的日志记录

## 注意事项

### ⚠️ 重要提醒
1. **备份检查**：虽然系统会自动备份，但建议在重要修改前手动备份
2. **语法验证**：上传前请检查 Markdown 语法的正确性
3. **测试验证**：修改 Prompt 后建议进行功能测试
4. **性能影响**：大型 Prompt 文件可能影响智能体响应速度

### 💡 最佳实践
1. **增量修改**：建议分步骤进行 Prompt 优化，便于问题定位
2. **版本管理**：重要版本可以手动备份到版本控制系统
3. **团队协作**：团队环境下建议建立 Prompt 修改审核流程
4. **性能监控**：关注修改后智能体的性能表现

## 故障排除

### 常见问题

**Q: 上传失败，提示"Invalid filename"**
- A: 请确认选择的是系统支持的5个文件名之一

**Q: 内容为空无法上传**  
- A: 请确保在文本框中输入了有效的 Prompt 内容

**Q: 文件列表显示"Not Found"**
- A: 表示该文件尚未创建，可以通过上传功能创建

**Q: 备份文件在哪里**
- A: 自动备份文件存储在 `data/backups/` 目录下

### 日志查看
```bash
# 查看应用日志
tail -f logs/app.log

# 查看上传相关日志
grep "upload" logs/app.log
```

## 版本信息

- **功能版本**: v1.0.0
- **支持的 DeerFlow 版本**: v0.1.0+
- **最后更新**: 2025-01-15

---

*DeerFlow 系统 Prompt 文件上传功能 | 智能研究助手平台*