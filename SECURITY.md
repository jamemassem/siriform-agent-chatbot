# 🔐 Security Guidelines

## Environment Variables

### ⚠️ CRITICAL: Never Commit Secrets!

**DO NOT** commit any of these files to git:
- `.env`
- `.env.local`
- `.env.production`
- Any file containing API keys, passwords, or secrets

### ✅ Proper Setup

1. **Copy the example file:**
   ```bash
   # Backend
   cd backend
   cp .env.example .env
   
   # Frontend (if needed)
   cd frontend
   cp .env.example .env
   ```

2. **Edit `.env` with your actual credentials:**
   - Never share these files
   - Never commit them to git
   - Keep them local only

3. **Verify `.gitignore` is protecting you:**
   ```bash
   git status
   # .env should NOT appear in the list
   ```

### 📝 `.env.example` vs `.env`

| File | Purpose | Git |
|------|---------|-----|
| `.env.example` | Template with placeholder values | ✅ Committed |
| `.env` | Actual secrets and API keys | ❌ NEVER commit |

### 🔑 Required API Keys

Get your API keys from:
- **OpenRouter**: https://openrouter.ai/keys
- **LangSmith**: https://smith.langchain.com/settings
- **Supabase**: https://app.supabase.com/project/_/settings/api

### 🚨 What to Do If You Accidentally Commit Secrets

1. **Immediately rotate all exposed credentials**
2. **Remove from git history:**
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch backend/.env" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push (if necessary):**
   ```bash
   git push origin --force --all
   ```

### 🛡️ Best Practices

- ✅ Use `.env.example` as a template
- ✅ Add all `.env*` files to `.gitignore` (except `.env.example`)
- ✅ Rotate API keys regularly
- ✅ Use different keys for development and production
- ✅ Store production secrets in secure vaults (Azure Key Vault, AWS Secrets Manager)
- ❌ Never hardcode secrets in source code
- ❌ Never share `.env` files via Slack, email, etc.
- ❌ Never screenshot or paste secrets in public channels

### 📦 Production Deployment

For production environments:
- Use environment variables provided by your hosting platform
- Use secret management services (Azure Key Vault, AWS Secrets Manager, etc.)
- Enable secret scanning in your CI/CD pipeline
- Implement least-privilege access controls

### 🔍 Checking for Leaked Secrets

Use tools to scan for accidentally committed secrets:
- [git-secrets](https://github.com/awslabs/git-secrets)
- [truffleHog](https://github.com/trufflesecurity/truffleHog)
- [gitleaks](https://github.com/gitleaks/gitleaks)

Example with gitleaks:
```bash
# Install
brew install gitleaks

# Scan repository
gitleaks detect --source . --verbose
```

---

**Remember: Security is everyone's responsibility! 🔒**
