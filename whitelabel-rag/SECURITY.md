# WhiteLabelRAG Security Guide

## 🔐 Secret Key Management

### What is a Secret Key?

The SECRET_KEY is a cryptographically secure random string used by Flask for:
- Session encryption and signing
- CSRF protection
- Secure cookie generation
- Password reset tokens
- Other security-sensitive operations

### 🔑 Generating a Secure Secret Key

#### Method 1: Using Python (Recommended)
```python
import secrets
secret_key = secrets.token_urlsafe(32)
print(f"SECRET_KEY={secret_key}")
```

#### Method 2: Using the Provided Script
```bash
python scripts/generate-secret-key.py
```

#### Method 3: Command Line
```bash
# Generate and display
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# Generate multiple options
python -c "import secrets; [print(f'Option {i+1}: {secrets.token_urlsafe(32)}') for i in range(3)]"
```

### 📝 Example Generated Keys

Here are some example secure keys (DO NOT use these in production):

```bash
# Example keys (generate your own!)
SECRET_KEY=_5AT1Hg2uQJ40CP4Bsg4YcUY3HSzGAJm7Ri-Z5zCyHU
SECRET_KEY=Ub-zZr3_Yl9AY__Vg9-V9pxi6PS_nTbhdeD8kNm_YcA
SECRET_KEY=OJk3nd2Z_vFkX1UNKKFBgIp4wkMEDdj398TabxaKfKs
```

### ⚙️ Setting the Secret Key

#### Option 1: Environment Variable (Recommended for Production)
```bash
# Windows
set SECRET_KEY=your_generated_secret_key_here

# Linux/Mac
export SECRET_KEY=your_generated_secret_key_here
```

#### Option 2: .env File (Good for Development)
```bash
# Create .env file
cp .env.example .env

# Edit .env file and add:
SECRET_KEY=your_generated_secret_key_here
```

#### Option 3: Docker Environment
```yaml
# docker-compose.yml
environment:
  - SECRET_KEY=your_generated_secret_key_here
```

### 🔒 Security Best Practices

#### 1. Key Requirements
- **Minimum 32 characters** (256 bits of entropy)
- **Cryptographically random** (use `secrets` module, not `random`)
- **URL-safe characters** (base64 encoded)
- **Unique per environment** (different keys for dev/staging/prod)

#### 2. Key Storage
- ✅ **Environment variables** (recommended for production)
- ✅ **Secure key management services** (AWS Secrets Manager, Azure Key Vault)
- ✅ **Encrypted configuration files**
- ❌ **Never commit to version control**
- ❌ **Never hardcode in source code**
- ❌ **Never share in plain text**

#### 3. Key Rotation
- **Rotate keys periodically** (every 90-180 days)
- **Rotate immediately** if compromised
- **Use different keys** for different environments
- **Keep backup of old keys** during transition period

### 🛡️ Additional Security Measures

#### 1. Environment Variables Security
```bash
# Check if SECRET_KEY is set
python -c "import os; print('SECRET_KEY set:', bool(os.environ.get('SECRET_KEY')))"

# Verify key length
python -c "import os; key=os.environ.get('SECRET_KEY', ''); print(f'Key length: {len(key)} characters')"
```

#### 2. .env File Security
```bash
# Set proper permissions (Unix/Linux)
chmod 600 .env

# Add to .gitignore
echo ".env" >> .gitignore
```

#### 3. Docker Security
```dockerfile
# Use build-time arguments for secrets
ARG SECRET_KEY
ENV SECRET_KEY=${SECRET_KEY}

# Or use Docker secrets (Swarm mode)
# docker secret create secret_key secret_key.txt
```

### 🚨 Security Checklist

#### Development Environment
- [ ] SECRET_KEY is set (environment variable or .env file)
- [ ] SECRET_KEY is at least 32 characters long
- [ ] SECRET_KEY is cryptographically random
- [ ] .env file is in .gitignore
- [ ] .env file has restricted permissions (600)

#### Production Environment
- [ ] SECRET_KEY is set as environment variable
- [ ] SECRET_KEY is different from development
- [ ] SECRET_KEY is stored securely (not in code)
- [ ] SECRET_KEY is backed up securely
- [ ] Key rotation schedule is established

#### Security Monitoring
- [ ] Monitor for SECRET_KEY exposure in logs
- [ ] Regular security audits
- [ ] Automated secret scanning in CI/CD
- [ ] Incident response plan for key compromise

### 🔧 Troubleshooting

#### Common Issues

**1. "SECRET_KEY not set" Error**
```bash
# Check if set
echo $SECRET_KEY  # Linux/Mac
echo %SECRET_KEY% # Windows

# Set temporarily
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")
```

**2. "Weak SECRET_KEY" Warning**
```python
# Check key strength
import os
key = os.environ.get('SECRET_KEY', '')
if len(key) < 32:
    print("⚠️ SECRET_KEY too short, should be at least 32 characters")
else:
    print("✅ SECRET_KEY length is adequate")
```

**3. Key Not Loading from .env**
```python
# Debug .env loading
from dotenv import load_dotenv
import os

print("Before loading .env:", bool(os.environ.get('SECRET_KEY')))
load_dotenv()
print("After loading .env:", bool(os.environ.get('SECRET_KEY')))
```

### 📚 Additional Resources

#### Flask Security Documentation
- [Flask Security Considerations](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Session Security](https://flask.palletsprojects.com/en/2.3.x/quickstart/#sessions)

#### Cryptographic Best Practices
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [Python secrets module documentation](https://docs.python.org/3/library/secrets.html)

#### Key Management Services
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/)
- [Azure Key Vault](https://azure.microsoft.com/en-us/services/key-vault/)
- [Google Secret Manager](https://cloud.google.com/secret-manager)
- [HashiCorp Vault](https://www.vaultproject.io/)

---

## 🔐 Quick Secret Key Generation

**For immediate use, run this command:**

```bash
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
```

**Copy the output and add it to your .env file or set as environment variable.**

---

**Remember: Keep your secret keys secret! 🤫**