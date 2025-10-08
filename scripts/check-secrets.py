#!/usr/bin/env python3
"""
Pre-commit security check script.
Scans for accidentally staged .env files or secrets.
"""
import subprocess
import sys
import re

# Dangerous patterns that should never be committed
SECRET_PATTERNS = [
    (r'OPENROUTER_API_KEY\s*=\s*["\']?sk-or-v1-[a-zA-Z0-9]+', 'OpenRouter API Key'),
    (r'LANGSMITH_API_KEY\s*=\s*["\']?ls__[a-zA-Z0-9]+', 'LangSmith API Key'),
    (r'SUPABASE_KEY\s*=\s*["\']?eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+', 'Supabase API Key'),
    (r'SUPABASE_JWT_SECRET\s*=\s*["\']?[a-zA-Z0-9+/]{40,}', 'Supabase JWT Secret'),
    (r'password\s*=\s*["\'][^"\']+["\']', 'Password'),
    (r'(aws_access_key_id|aws_secret_access_key)\s*=', 'AWS Credentials'),
]

# Files that should NEVER be committed
FORBIDDEN_FILES = [
    '.env',
    '.env.local',
    '.env.production',
    'backend/.env',
    'frontend/.env',
]

def check_staged_files():
    """Check if any forbidden files are staged."""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only'],
        capture_output=True,
        text=True
    )
    
    staged_files = result.stdout.strip().split('\n')
    forbidden_found = []
    
    for file in staged_files:
        for forbidden in FORBIDDEN_FILES:
            if file.endswith(forbidden):
                forbidden_found.append(file)
    
    return forbidden_found

def scan_staged_content():
    """Scan staged content for secret patterns."""
    result = subprocess.run(
        ['git', 'diff', '--cached'],
        capture_output=True,
        text=True
    )
    
    content = result.stdout
    secrets_found = []
    
    for pattern, name in SECRET_PATTERNS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            secrets_found.append((name, matches))
    
    return secrets_found

def main():
    print("🔐 Running security checks...")
    
    # Check for forbidden files
    forbidden = check_staged_files()
    if forbidden:
        print("\n❌ ERROR: Forbidden files are staged!")
        print("The following files should NEVER be committed:")
        for file in forbidden:
            print(f"  - {file}")
        print("\nTo fix:")
        print("  git reset HEAD <file>")
        print("  Verify .gitignore includes these files")
        return 1
    
    # Check for secrets in content
    secrets = scan_staged_content()
    if secrets:
        print("\n❌ ERROR: Potential secrets detected!")
        print("The following secrets were found in staged changes:")
        for name, matches in secrets:
            print(f"  - {name}: {len(matches)} occurrence(s)")
        print("\nTo fix:")
        print("  1. Remove the secrets from your code")
        print("  2. Use .env files (which are gitignored)")
        print("  3. Stage the corrected files")
        return 1
    
    print("✅ No security issues detected!")
    return 0

if __name__ == '__main__':
    sys.exit(main())
