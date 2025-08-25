# Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in Stash-Filter, please report it responsibly:

### Preferred Method
- **Email**: alienbygg@gmail.com
- **GitHub Security Advisories**: Use GitHub's private vulnerability reporting feature
- **PGP Key**: Available on request for sensitive disclosures

### Please DO NOT:
- Report security vulnerabilities through public GitHub issues
- Discuss vulnerabilities in public forums or discussions
- Test vulnerabilities against production instances you don't own

## Response Process

1. **Acknowledgment**: We'll acknowledge your report within 48 hours
2. **Investigation**: We'll investigate and validate the vulnerability
3. **Fix Development**: We'll develop and test a fix
4. **Disclosure**: We'll coordinate responsible disclosure with you
5. **Credit**: We'll credit you in the security advisory (if desired)

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | ✅ Yes             |
| 0.x.x   | ❌ No (EOL)        |

Only the latest major version receives security updates. Please upgrade to the latest version before reporting vulnerabilities in older versions.

## Security Considerations

### Application Security

**Data Storage:**
- All sensitive data (API keys) should be stored in environment variables
- Database contains no personally identifiable information beyond user preferences
- Local SQLite database with no remote access

**Network Security:**
- Application designed for local network deployment
- No authentication required (assumes trusted network)
- HTTPS recommended with reverse proxy for external access
- All external API calls use HTTPS

**Container Security:**
- Runs as non-root user inside container
- No privileged access required
- Minimal base image to reduce attack surface
- No unnecessary network ports exposed

### Deployment Security

**Environment Variables:**
```env
# Never commit real values to version control
SECRET_KEY=generate-unique-key-for-production
STASH_API_KEY=your-actual-api-key
WHISPARR_API_KEY=your-actual-api-key
```

**Docker Security:**
```yaml
# Example secure deployment
services:
  stash-filter:
    user: "1000:1000"  # Non-root user
    read_only: true     # Read-only filesystem
    cap_drop:
      - ALL             # Drop all capabilities
    security_opt:
      - no-new-privileges:true
```

**Network Security:**
```yaml
# Restrict network access
services:
  stash-filter:
    ports:
      - "127.0.0.1:5000:5000"  # Localhost only
    networks:
      - internal               # Internal network only
```

### API Security

**Authentication:**
- Currently no authentication (trusted network assumption)
- Consider adding API key authentication for public deployments
- Rate limiting not implemented (consider adding for public instances)

**Input Validation:**
- All user inputs are validated and sanitized
- SQL injection protection through SQLAlchemy ORM
- XSS protection through template escaping

**External API Calls:**
- All external APIs called over HTTPS
- API keys transmitted securely
- Request timeout limits prevent DoS
- Rate limiting respected for external services

## Best Practices for Users

### Secret Management
```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Never share your API keys
# Rotate API keys regularly
# Use environment variables, not config files
```

### Network Security
```yaml
# Use reverse proxy with SSL
services:
  nginx:
    image: nginx
    ports:
      - "443:443"
    volumes:
      - ./ssl:/etc/ssl
      - ./nginx.conf:/etc/nginx/nginx.conf
```

### File Permissions
```bash
# Secure file permissions
chmod 600 .env
chmod 700 data/
chown -R 1000:1000 data/ logs/
```

### Regular Maintenance
- Update to latest versions promptly
- Monitor security advisories
- Regular backup of configuration and data
- Review logs for suspicious activity

## Known Security Limitations

### Current Limitations
1. **No Authentication**: Assumes trusted network deployment
2. **No Rate Limiting**: Could be abused if exposed publicly
3. **No Input Sanitization**: In some API endpoints
4. **Local Storage Only**: API keys stored in environment/config files

### Mitigation Recommendations
1. **Deploy on trusted networks only**
2. **Use reverse proxy with authentication for remote access**
3. **Implement network-level rate limiting**
4. **Regular security updates**
5. **Monitor access logs**

## Security Roadmap

### Planned Security Enhancements
- [ ] Optional API key authentication
- [ ] Rate limiting implementation
- [ ] Enhanced input validation
- [ ] Security headers implementation
- [ ] Audit logging
- [ ] Secret management integration

### Future Considerations
- [ ] OAuth2/OIDC integration
- [ ] Multi-tenancy support
- [ ] Encrypted data storage
- [ ] Security scanning integration
- [ ] Vulnerability management

## Dependencies

### Security Scanning
We regularly scan dependencies for known vulnerabilities:

```bash
# Check for vulnerabilities
pip-audit
safety check

# Docker image scanning
trivy image stash-filter:latest
```

### Dependency Updates
- Automated dependency updates via Dependabot
- Security patches applied promptly
- Breaking changes evaluated carefully

## Incident Response

### In Case of Security Incident

1. **Immediate Actions:**
   - Stop affected services
   - Preserve logs and evidence
   - Assess scope of compromise

2. **Investigation:**
   - Identify root cause
   - Determine affected data/systems
   - Document timeline and impact

3. **Remediation:**
   - Apply security patches
   - Update compromised credentials
   - Implement additional safeguards

4. **Communication:**
   - Notify affected users
   - Publish security advisory
   - Share lessons learned

## Contact Information

For security-related inquiries:
- **Security Email**: alienbygg@gmail.com
- **GitHub Security**: Use GitHub's private vulnerability reporting
- **Response Time**: 48 hours for initial acknowledgment

## Acknowledgments

We thank the security researchers and community members who help keep Stash-Filter secure:
- [Future security contributors will be listed here]

---

*This security policy is reviewed quarterly and updated as needed. Last updated: January 2025*
