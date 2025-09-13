# Docker环境下的Prompt文件管理

## 问题说明

在Docker环境中，容器内文件系统的更改在容器重启后会丢失。为了实现prompt文件的持久化和自动备份，我们使用了Docker数据卷(volumes)。

## 解决方案

### 1. 数据卷配置

在`docker-compose.yml`中配置了数据卷：

```yaml
volumes:
  - ./conf.yaml:/app/conf.yaml:ro
  - ./data/prompts:/app/src/prompts:rw      # prompt文件持久化
  - ./data/backups:/app/data/backups:rw     # 备份文件持久化
```

### 2. 目录结构

```
项目根目录/
├── data/                    # 持久化数据目录
│   ├── prompts/            # prompt模板文件 (映射到容器 /app/src/prompts)
│   │   ├── coder.md
│   │   ├── coordinator.md
│   │   ├── planner.md
│   │   ├── reporter.md
│   │   └── researcher.md
│   └── backups/            # 备份文件 (映射到容器 /app/data/backups)
│       ├── coder.md.1757330838.bak
│       └── ...
└── docker-compose.yml
```

### 3. 自动备份和立即生效机制

#### 自动备份 (备份到独立目录)
```python
# 创建备份文件到专门的备份目录
backup_filename = f"{request.filename}.{int(datetime.now().timestamp())}.bak"
backup_path = backups_dir / backup_filename
shutil.copy2(file_path, backup_path)
```

#### 立即生效
```python
# 直接写入到数据卷映射的目录
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(request.content)
```

## 部署步骤

### 1. 初始化数据目录
```bash
# 运行初始化脚本
./init-docker-data.sh
```

### 2. 启动容器
```bash
docker-compose up -d
```

### 3. 验证功能
- 访问前端设置页面的"Prompt"标签页
- 上传新的prompt文件
- 检查`data/prompts/`目录中的文件是否更新
- 检查`data/backups/`目录中是否生成了备份文件

## 工作原理

1. **持久化**: 通过Docker数据卷，`data/prompts/`目录映射到容器内的`/app/src/prompts/`
2. **备份**: 文件更新前，自动复制到`data/backups/`目录
3. **立即生效**: Python应用程序直接读取映射的目录，无需重启容器
4. **数据安全**: 即使容器重启或更新，数据都保存在宿主机的`data/`目录中

## 注意事项

- 确保`data/`目录有正确的读写权限
- 备份文件会累积，建议定期清理旧备份
- 第一次部署前务必运行`init-docker-data.sh`脚本