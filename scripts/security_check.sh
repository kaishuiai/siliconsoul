#!/bin/bash

# SiliconSoul Security Check Script
# 在推送到GitHub前运行此脚本检查是否包含敏感信息

echo "=========================================="
echo "🔒 SiliconSoul 安全审查"
echo "=========================================="
echo ""

ISSUES_FOUND=0

# 检查函数 - 排除文档和脚本目录
check_pattern() {
    local pattern=$1
    local description=$2
    
    echo -n "检查 $description ... "
    
    if grep -r "$pattern" src/ tests/ config/ --exclude-dir=.git --exclude-dir=__pycache__ --exclude="*.pyc" 2>/dev/null | grep -q .; then
        echo "❌ 发现敏感信息！"
        grep -r "$pattern" src/ tests/ config/ --exclude-dir=.git --exclude-dir=__pycache__ --exclude="*.pyc" 2>/dev/null | head -5
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
        echo ""
    else
        echo "✅ 通过"
    fi
}

# 1. 检查私钥
echo "1️⃣  检查私钥文件..."
check_pattern "-----BEGIN.*PRIVATE KEY-----" "私钥"
check_pattern "-----BEGIN RSA PRIVATE KEY-----" "RSA私钥"

# 2. 检查GitHub Token
echo ""
echo "2️⃣  检查GitHub Token..."
check_pattern "ghp_[a-zA-Z0-9]\{36,\}" "GitHub Token"

# 3. 检查数据库密码
echo ""
echo "3️⃣  检查数据库连接字符串..."
check_pattern "mysql://.*:.*@" "MySQL连接"
check_pattern "postgresql://.*:.*@" "PostgreSQL连接"

# 4. 检查.env文件
echo ""
echo "4️⃣  检查.env文件..."
if [ -f ".env" ] || [ -f ".env.local" ]; then
    echo "❌ 发现.env文件！"
    ls -la .env* 2>/dev/null
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
    echo ""
else
    echo "✅ 没有.env文件"
fi

# 5. 检查配置文件中的密钥
echo ""
echo "5️⃣  检查配置文件中的密钥..."
check_pattern "password[\"']?[[:space:]]*[:=]" "密码字段"
check_pattern "api[_-]?key[\"']?[[:space:]]*[:=]" "API密钥"
check_pattern "secret[\"']?[[:space:]]*[:=]" "密钥字段"
check_pattern "token[\"']?[[:space:]]*[:=]" "令牌字段"

# 6. 检查tracked敏感文件
echo ""
echo "6️⃣  检查已追踪的敏感文件..."
tracked_secrets=$(git ls-files 2>/dev/null | grep -E "\.pem|\.key|\.env" | wc -l)
if [ $tracked_secrets -gt 0 ]; then
    echo "❌ 发现已追踪的敏感文件！"
    git ls-files 2>/dev/null | grep -E "\.pem|\.key|\.env"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
    echo ""
else
    echo "✅ 没有已追踪的敏感文件"
fi

# 7. 检查.gitignore
echo ""
echo "7️⃣  检查.gitignore配置..."
gitignore_ok=true

if ! grep -q "\.env" .gitignore 2>/dev/null; then
    echo "⚠️  .env未在.gitignore中"
    gitignore_ok=false
fi

if ! grep -q "secrets" .gitignore 2>/dev/null; then
    echo "⚠️  secrets未在.gitignore中"
    gitignore_ok=false
fi

if ! grep -q "credentials" .gitignore 2>/dev/null; then
    echo "⚠️  credentials未在.gitignore中"
    gitignore_ok=false
fi

if [ "$gitignore_ok" = true ]; then
    echo "✅ .gitignore配置完整"
fi

# 总结
echo ""
echo "=========================================="
if [ $ISSUES_FOUND -eq 0 ]; then
    echo "✅ 安全检查通过！可以安全推送到GitHub"
    echo "=========================================="
    exit 0
else
    echo "❌ 发现 $ISSUES_FOUND 个问题！请修复后再推送"
    echo "=========================================="
    exit 1
fi
