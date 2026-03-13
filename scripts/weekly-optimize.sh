#!/bin/bash
# ContentPilot 定期优化脚本
# 每周一运行一次，优化代码质量和 prompt

set -e

PROJECT_DIR="$HOME/projects/contentpilot"
REPORT_DIR="$PROJECT_DIR/reports"
DATE=$(date +%Y-%m-%d)
DAY_OF_WEEK=$(date +%u)

mkdir -p "$REPORT_DIR"

echo "=== ContentPilot 周度优化 $DATE ==="

cd "$PROJECT_DIR"

# 1. 测试
echo "1. 运行测试..."
TEST_RESULT=$(python3 -m pytest tests/ -q 2>&1 | tail -1)
echo "  $TEST_RESULT"

# 2. 代码统计
echo "2. 代码统计..."
PY_FILES=$(find contentpilot -name "*.py" | wc -l)
LINES=$(find contentpilot -name "*.py" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}')
echo "  Python文件: $PY_FILES, 总行数: $LINES"

# 3. Git 统计
echo "3. Git 统计..."
COMMITS=$(git rev-list --count HEAD)
LAST_COMMIT=$(git log -1 --format="%h %s")
echo "  总提交: $COMMITS"
echo "  最近: $LAST_COMMIT"

# 4. 生成周报
cat > "$REPORT_DIR/weekly-$DATE.md" << EOF
# ContentPilot 周报 - $DATE

## 代码状态
- 测试: $TEST_RESULT
- Python文件: $PY_FILES
- 代码行数: $LINES
- Git提交数: $COMMITS
- 最近提交: $LAST_COMMIT

## 本周优化项
$(if [ "$DAY_OF_WEEK" = "1" ]; then echo "- [ ] 检查并优化 AI prompt 质量"; echo "- [ ] 评估新增平台需求"; echo "- [ ] 检查竞品动态"; fi)

## 功能清单
$(python3 -m contentpilot.cli --help 2>&1 | grep -A 20 "Commands:")

## 待办
- [ ] 添加内容模板库
- [ ] 支持定时发布
- [ ] 添加数据分析看板
- [ ] 优化 prompt 减少 token 消耗
- [ ] 添加 A/B 测试功能
EOF

echo ""
echo "✅ 周报已生成: $REPORT_DIR/weekly-$DATE.md"
