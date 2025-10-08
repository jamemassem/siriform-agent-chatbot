# Security Scripts

This directory contains scripts to help maintain security in the repository.

## 🔐 check-secrets.py

Scans staged git changes for:
- Accidentally staged `.env` files
- Hard-coded API keys and secrets
- Passwords and credentials

### Manual Usage

```bash
# Check current staged changes
python scripts/check-secrets.py
```

## 🪝 pre-commit Hook

Automatically runs security checks before each commit.

### Installation

#### Option 1: Automatic (Recommended)

```bash
# Make scripts executable
chmod +x scripts/check-secrets.py scripts/pre-commit

# Copy hook to git directory
cp scripts/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

#### Option 2: Manual (Windows)

```powershell
# Copy the hook
Copy-Item scripts\pre-commit .git\hooks\pre-commit
```

### Verification

```bash
# Test the hook
git add some-file.txt
git commit -m "test"

# You should see:
# 🔐 Running pre-commit security checks...
# ✅ Security checks passed. Proceeding with commit...
```

### Bypassing (Emergency Only!)

```bash
# Skip pre-commit hooks (USE CAREFULLY!)
git commit --no-verify -m "emergency fix"
```

## 🛡️ What Gets Detected

### Forbidden Files
- `.env`
- `.env.local`
- `.env.production`
- `backend/.env`
- `frontend/.env`

### Secret Patterns
- OpenRouter API keys (`sk-or-v1-...`)
- LangSmith API keys (`ls__...`)
- Supabase keys (`eyJ...`)
- JWT secrets
- AWS credentials
- Hardcoded passwords

## 🚨 If Secrets Are Detected

1. **Remove the secrets immediately**
   ```bash
   git reset HEAD <file>
   ```

2. **Move secrets to .env file**
   ```bash
   # Add to backend/.env (NOT backend/.env.example)
   echo "API_KEY=your-secret-here" >> backend/.env
   ```

3. **Verify .env is ignored**
   ```bash
   git check-ignore backend/.env
   # Should output: backend/.env
   ```

4. **Re-stage corrected files**
   ```bash
   git add <fixed-file>
   git commit -m "fix: remove hardcoded secrets"
   ```

## 🔄 Rotating Compromised Keys

If you accidentally commit secrets:

1. **Immediately rotate all exposed credentials**
   - Generate new API keys
   - Update `.env` file
   - Revoke old keys

2. **Remove from git history** (if already pushed)
   ```bash
   # Use git filter-branch or BFG Repo-Cleaner
   # See SECURITY.md for detailed instructions
   ```

3. **Force push** (if necessary)
   ```bash
   git push origin --force
   ```

## 📚 Additional Tools

Consider using these tools for enhanced security:

- [gitleaks](https://github.com/gitleaks/gitleaks) - Comprehensive secret scanning
- [truffleHog](https://github.com/trufflesecurity/truffleHog) - Find secrets in git history
- [git-secrets](https://github.com/awslabs/git-secrets) - AWS secret prevention

Example:
```bash
# Install gitleaks
brew install gitleaks  # macOS
# or download from GitHub releases for Windows

# Scan repository
gitleaks detect --source . --verbose
```

---

**Remember: Prevention is better than remediation! 🔒**
