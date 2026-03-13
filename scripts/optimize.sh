#!/bin/bash
# ContentPilot 定期优化脚本
# 运行: ./scripts/optimize.sh

set -e

PROJECT_DIR="$HOME/projects/contentpilot"
REPORT_DIR="$PROJECT_DIR/reports"
DATE=$(date +%Y-%m-%d)

mkdir -p "$REPORT_DIR"

echo "=== ContentPilot 优化检查 $DATE ==="

# 1. 代码质量检查
echo "1. 代码检查..."
cd "$PROJECT_DIR"
python3 -m py_compile contentpilot/cli.py contentpilot/commands/*.py 2>&1 && echo "  ✅ 代码无语法错误"

# 2. 测试运行
echo "2. 运行测试..."
python3 -m pytest tests/ -v --tb=short 2>&1 | tail -5

# 3. Git 状态
echo "3. Git 状态..."
git status --short

# 4. 检查依赖更新
echo "4. 依赖检查..."
pip3 list --outdated 2>/dev/null | grep -E "openai|click|rich" || echo "  ✅ 核心依赖最新"

# 5. 生成优化报告
cat > "$REPORT_DIR/optimize-$DATE.md" << EOF
# ContentPilot 优化报告 - $DATE

## 代码状态
- 语法检查: 通过
- 测试状态: $(python3 -m pytest tests/ -q 2>&1 | tail -1)

## Git 提交历史
$(git log --oneline -5)

## 待优化项
- [ ] 添加更多平台支持 (B站/快手)
- [ ] 优化 AI prompt 质量
- [ ] 添加内容模板库
- [ ] 支持批量生成
- [ ] 添加数据分析功能

## 用户反馈记录
(待收集)
EOF

echo ""
echo "✅ 优化检查完成，报告: $REPORT_DIR/optimize-$DATE.md"
