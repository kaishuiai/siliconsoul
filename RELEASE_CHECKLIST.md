# 📋 发布检查清单 - SiliconSoul MOE

## 🎯 每次推送到GitHub前必须检查

### 1️⃣ **代码质量检查**

```bash
# 运行所有测试
pytest tests/ -v

# 确保所有测试通过
# 覆盖率不低于80%
```

**检查清单：**
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 代码覆盖率 ≥ 80%
- [ ] 无任何测试警告

---

### 2️⃣ **安全检查**

```bash
# 运行安全检查脚本
bash scripts/security_check.sh
```

**必须全部通过：**
- [ ] ✅ 没有私钥 (.pem, .key)
- [ ] ✅ 没有GitHub Token
- [ ] ✅ 没有数据库密码
- [ ] ✅ 没有API密钥
- [ ] ✅ 没有.env文件
- [ ] ✅ 没有已追踪的敏感文件
- [ ] ✅ .gitignore配置完整

---

### 3️⃣ **版本号检查**

```bash
# 检查当前版本号
cat VERSION

# 编辑版本号（如果需要）
echo "1.0.1" > VERSION
```

**检查清单：**
- [ ] 版本号已更新（如需要）
- [ ] README.md中的版本号已同步
- [ ] CHANGELOG已更新（如需要）
- [ ] 遵循语义化版本 (MAJOR.MINOR.PATCH)

---

### 4️⃣ **代码审查**

**检查清单：**
- [ ] 代码风格一致
- [ ] 有适当的代码注释
- [ ] 没有无用代码
- [ ] Docstring完整
- [ ] 类型注解完整
- [ ] 没有硬编码的配置

---

### 5️⃣ **文档检查**

**检查清单：**
- [ ] README.md已更新
- [ ] API文档已更新
- [ ] CHANGELOG已记录
- [ ] 代码注释清晰
- [ ] 示例代码可运行

---

### 6️⃣ **Git检查**

```bash
# 查看待提交的改动
git status

# 查看提交历史
git log --oneline -n 5

# 确保分支是最新的
git pull origin main
```

**检查清单：**
- [ ] 所有改动都已暂存
- [ ] 提交信息清晰描述改动
- [ ] 本地分支与远程同步
- [ ] 没有未提交的重要改动

---

## 📝 完整发布流程

### **场景1: 小的Bug修复 (PATCH版本)**

```bash
# 1. 修改代码和修复Bug
# 修改相关文件...

# 2. 本地测试
pytest tests/ -v

# 3. 版本号更新（如1.0.0 → 1.0.1）
echo "1.0.1" > VERSION

# 4. 安全检查
bash scripts/security_check.sh

# 5. 更新文档
# 编辑 README.md 和 CHANGELOG.md

# 6. 提交
git add .
git commit -m "fix: Bug修复描述

- 修复的具体问题
- 影响范围"

# 7. 推送
git push origin main

# 8. 创建标签
git tag v1.0.1
git push origin --tags
```

---

### **场景2: 新功能 (MINOR版本)**

```bash
# 1. 开发新功能
# 编写代码、测试...

# 2. 所有测试通过
pytest tests/ -v

# 3. 版本号更新（1.0.0 → 1.1.0）
echo "1.1.0" > VERSION

# 4. 安全检查
bash scripts/security_check.sh

# 5. 更新文档和CHANGELOG
# 编辑所有文档文件

# 6. 提交
git add .
git commit -m "feat: 新功能名称

- 新增的功能描述
- 使用示例
- 相关文档更新"

# 7. 推送和标签
git push origin main
git tag v1.1.0
git push origin --tags
```

---

### **场景3: 重大更新 (MAJOR版本)**

```bash
# 1. 完成所有重大改动
# 架构变更、API重构等

# 2. 充分测试
pytest tests/ -v --cov=src

# 3. 版本号更新（1.0.0 → 2.0.0）
echo "2.0.0" > VERSION

# 4. 安全检查
bash scripts/security_check.sh

# 5. 完整的文档更新
# README、API文档、迁移指南等

# 6. 提交
git add .
git commit -m "feat!: 重大版本更新

BREAKING CHANGE: 
- API改动的详细说明
- 迁移指南

新增功能:
- 功能1
- 功能2"

# 7. 推送和标签
git push origin main
git tag v2.0.0
git push origin --tags
```

---

## 🔄 发布前清单模板

```markdown
## v{VERSION} 发布清单

### 代码质量
- [ ] 所有测试通过
- [ ] 覆盖率 ≥ 80%
- [ ] 代码审查完成

### 安全
- [ ] 安全检查通过 (`bash scripts/security_check.sh`)
- [ ] 没有敏感信息
- [ ] .gitignore已更新

### 版本管理
- [ ] 版本号已更新到 v{VERSION}
- [ ] README已同步
- [ ] CHANGELOG已更新

### 文档
- [ ] API文档已更新
- [ ] 示例代码可运行
- [ ] 注释完整

### Git
- [ ] 代码已提交
- [ ] 已推送到GitHub
- [ ] 标签已创建

### 验证
- [ ] GitHub上的版本正确
- [ ] Release notes已发布
```

---

## ⚠️ 常见错误

### ❌ 错误1: 推送前没运行安全检查
```bash
# 后果: Token或密钥可能泄露
# 解决: 必须运行 bash scripts/security_check.sh
```

### ❌ 错误2: 版本号不一致
```bash
# 后果: 版本混乱，难以追踪
# 解决: 更新VERSION、README、setup.py中的版本号
```

### ❌ 错误3: 没有记录变更
```bash
# 后果: 无法追踪改动历史
# 解决: 更新CHANGELOG.md和提交信息
```

### ❌ 错误4: 直接推送到main（未测试）
```bash
# 后果: 生产环境出现Bug
# 解决: 先本地测试，再推送
```

---

## 🎯 快速发布命令

```bash
# 一键检查 + 提交 + 推送（适合小改动）
bash scripts/security_check.sh && \
pytest tests/ -v && \
git add . && \
git commit -m "Minor updates" && \
git push origin main
```

---

## 📚 参考链接

- [VERSIONING.md](./VERSIONING.md) - 详细的版本管理规范
- [README.md](./README.md) - 项目信息
- GitHub: https://github.com/kaishuiai/siliconsoul

---

**最后更新**: 2026-04-06  
**负责人**: CC  
**下次审查**: 2026-04-13
