# 版本管理规范 - SiliconSoul MOE

## 📋 版本号管理

### 版本号格式
```
MAJOR.MINOR.PATCH[-PRERELEASE]

例如:
1.0.0        - 正式版
1.1.0        - 小版本更新
1.0.1        - Bug修复
1.0.0-beta   - 预发布版
```

### 版本号含义

- **MAJOR**: 主版本号
  - 重大功能变更
  - 不向后兼容的改动
  - 架构升级
  - 例: 1.0.0 → 2.0.0

- **MINOR**: 次版本号
  - 新增功能
  - 向后兼容的改进
  - 性能优化
  - 例: 1.0.0 → 1.1.0

- **PATCH**: 补丁版本号
  - Bug修复
  - 小的改进
  - 文档更新
  - 例: 1.0.0 → 1.0.1

---

## 📝 版本更新流程

### Step 1: 在本地开发（A环境）
```bash
# 在本地进行开发修改
# 运行所有测试确保通过
pytest tests/ -v
```

### Step 2: 安全审查（发布前必检）
```bash
# 检查是否包含敏感信息
bash scripts/security_check.sh

# 检查清单:
✅ 不包含私钥 (.pem, .key)
✅ 不包含Token (API_KEY, TOKEN)
✅ 不包含密码 (password, passwd)
✅ 不包含个人信息 (电话, 邮箱, IP)
✅ 不包含配置文件中的秘密 (.env, config.yml)
```

### Step 3: 更新版本号
```bash
# 编辑 VERSION 文件
echo "1.0.1" > VERSION

# 编辑 README.md 中的版本信息
# 编辑 setup.py 中的版本号
```

### Step 4: 提交到本地Git
```bash
git add .
git commit -m "Release v1.0.1: Bug fixes and improvements"
```

### Step 5: 推送到GitHub（B环境）
```bash
git tag v1.0.1
git push origin main
git push origin --tags
```

### Step 6: 在部署环境同步（C环境）
```bash
cd /deployment/path
git pull origin main
git checkout v1.0.1
# 重新部署
```

---

## 🔒 安全审查清单

### 必检项目

#### 1. 隐私密钥文件
```bash
# 检查是否有
grep -r "-----BEGIN.*PRIVATE KEY-----" src/ tests/
grep -r "-----BEGIN RSA PRIVATE KEY-----" src/ tests/
# 如果有任何匹配 → 立即删除！
```

#### 2. API Token和密钥
```bash
# 检查环境变量和配置
grep -r "ghp_" . --exclude-dir=.git
grep -r "sk_live_" . --exclude-dir=.git
grep -r "api_key" . --exclude-dir=.git
grep -r "API_TOKEN" . --exclude-dir=.git
# 如果有任何匹配 → 立即删除！
```

#### 3. 数据库密码
```bash
# 检查配置文件
grep -r "password" config/ --exclude-dir=.git
grep -r "passwd" config/ --exclude-dir=.git
grep -r "mysql://" . --exclude-dir=.git
grep -r "postgresql://" . --exclude-dir=.git
# 如果有任何匹配 → 立即删除！
```

#### 4. 个人信息
```bash
# 检查代码注释和文档
grep -r "jinqingwork" . --exclude-dir=.git
grep -r "@gmail.com" . --exclude-dir=.git
grep -r "phone:" . --exclude-dir=.git
# 如果有任何匹配 → 考虑删除！
```

#### 5. .env文件和本地配置
```bash
# 确保这些文件在.gitignore中
.env
.env.local
config.local.yml
secrets/
keys/
credentials/

# 检查是否被追踪
git ls-files | grep -E "\.env|secrets|credentials"
# 如果有任何结果 → 立即删除！
```

---

## 📦 .gitignore 完整清单

```
# 环境和配置
.env
.env.local
.env.*.local
config.local.yml
config.local.yaml
settings.local.py

# 密钥和凭证
*.pem
*.key
*.pub
*.ppk
secrets/
credentials/
keys/
.ssh/

# Token和API密钥
.tokens
token.txt
api_keys.yml

# IDE和系统
.vscode/
.idea/
*.swp
*.swo
.DS_Store
Thumbs.db

# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.pytest_cache/
.coverage
htmlcov/

# 部署
venv/
env/
.venv/
node_modules/

# 日志
*.log
logs/
```

---

## 🔐 敏感信息处理规范

### 如果不小心提交了敏感信息

```bash
# 1. 立即从Git历史删除（如果已推送到GitHub）
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch <sensitive-file>' \
  --prune-empty --tag-name-filter cat -- --all

# 2. 推送强制更新
git push origin --force --all

# 3. 删除GitHub上的缓存
# 访问: https://github.com/kaishuiai/siliconsoul/settings
# 清除缓存

# 4. 在GitHub上撤销Token访问
# 访问: https://github.com/settings/tokens
# 删除有问题的Token

# 5. 生成新的Token（如果需要）
```

---

## 📊 版本记录示例

```
v1.0.0 (2026-04-06)
├─ 初始版本发布
├─ MOE框架实现
├─ 9个Expert完成
├─ 174个测试通过
├─ 91.19%代码覆盖
└─ GitHub发布: https://github.com/kaishuiai/siliconsoul

v1.0.1 (2026-04-07)
├─ Bug修复
├─ 性能优化
└─ 文档更新

v1.1.0 (计划)
├─ 新增Expert
├─ API增强
└─ 缓存实现
```

---

## 🤖 自动化安全检查脚本

```python
# scripts/security_check.py
import os
import re

FORBIDDEN_PATTERNS = [
    r'-----BEGIN.*PRIVATE KEY-----',
    r'ghp_[a-zA-Z0-9]{36}',  # GitHub Token
    r'sk_live_[a-zA-Z0-9]+',  # Stripe Token
    r'api[_-]?key["\']?\s*[:=]',  # API Key
    r'password["\']?\s*[:=]',  # Password
    r'token["\']?\s*[:=]',  # Token
]

def check_file(filepath):
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            for pattern in FORBIDDEN_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    return False, f"Found forbidden pattern in {filepath}"
    except:
        pass
    return True, "OK"

# 扫描所有Python和配置文件
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith(('.py', '.yml', '.yaml', '.json', '.env')):
            filepath = os.path.join(root, file)
            ok, msg = check_file(filepath)
            print(f"{filepath}: {msg}")
```

---

## ✅ 发布检查清单

在每次推送到GitHub前，必须完成：

- [ ] 所有测试通过 (`pytest tests/ -v`)
- [ ] 代码覆盖率 ≥ 80%
- [ ] 没有敏感信息泄露
- [ ] 版本号已更新
- [ ] CHANGELOG已记录
- [ ] README已同步
- [ ] 代码审查完成
- [ ] 文档已更新

---

**规范制定日期**: 2026-04-06  
**负责人**: CC (SiliconSoul Developer)  
**最后更新**: 2026-04-06
