#!/bin/bash
# ContentPilot 推送脚本 (带自动重试)
# 解决网络不稳定导致的 GnuTLS 错误
# Token 从环境变量读取，不硬编码

cd ~/projects/contentpilot

if [ -z "$GITHUB_TOKEN" ]; then
    echo "❌ 请设置环境变量: export GITHUB_TOKEN=你的token"
    exit 1
fi

# 设置 remote
git remote set-url origin https://xiaoxia008:${GITHUB_TOKEN}@github.com/xiaoxia008/contentpilot.git

# 重试推送
for i in 1 2 3 4 5; do
    echo "推送尝试 $i/5..."
    if git push 2>&1; then
        echo "✅ 推送成功"
        break
    fi
    sleep 2
done

# 恢复 clean URL
git remote set-url origin https://github.com/xiaoxia008/contentpilot.git
