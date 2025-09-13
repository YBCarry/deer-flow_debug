#!/bin/bash

# 初始化Docker数据目录的脚本
# Initialize Docker data directories

echo "初始化Docker数据目录..."

# 创建数据目录
mkdir -p data/prompts
mkdir -p data/backups

# 检查data/prompts是否为空，如果为空则复制原始文件
if [ ! "$(ls -A data/prompts 2>/dev/null)" ]; then
    # data/prompts目录为空，复制原始prompt文件
    if [ -d "src/prompts" ]; then
        echo "复制原始prompt文件到data/prompts/..."
        cp src/prompts/*.md data/prompts/ 2>/dev/null || true
        cp src/prompts/*.py data/prompts/ 2>/dev/null || true
        echo "已复制 $(ls data/prompts/*.md data/prompts/*.py 2>/dev/null | wc -l) 个文件"
    else
        echo "警告: 未找到原始prompt文件目录 src/prompts"
        echo "请确保在项目根目录下运行此脚本"
    fi
else
    echo "data/prompts目录已有文件，跳过复制"
    echo "现有文件: $(ls data/prompts/*.md data/prompts/*.py 2>/dev/null | wc -l) 个"
fi

# 确保目录权限正确 (Docker用户可写)
# 使用更宽松的权限确保Docker容器内可以写入
chmod -R 777 data/

echo ""
echo "✅ 初始化完成！"
echo ""
echo "数据目录结构："
echo "  data/"
echo "    ├── prompts/     # prompt模板文件 (持久化)"
echo "    └── backups/     # 备份文件 (持久化)"
echo ""
echo "当前data/prompts中的文件:"
ls -la data/prompts/ 2>/dev/null || echo "  (目录为空)"
echo ""
echo "现在可以运行: docker-compose up -d"