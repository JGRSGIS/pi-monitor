# Security Policy

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security issue in Pi Monitor, please report it responsibly.

### How to Report

**For security vulnerabilities, please DO NOT open a public GitHub issue.**

Instead, report vulnerabilities via one of these methods:

1. **GitHub Security Advisories** (Preferred)
   - Navigate to the [Security Advisories](https://github.com/JGRSGIS/pi-monitor/security/advisories/new) page
   - Click "Report a vulnerability"
   - Fill out the form with details about the vulnerability

2. **Email**
   - Send details to the repository maintainers via GitHub's private messaging
   - Include "SECURITY" in the subject line

### What to Include in Your Report

Please provide as much information as possible:

- **Description**: A clear description of the vulnerability
- **Affected Component**: Which file(s) or function(s) are affected
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Impact Assessment**: What an attacker could achieve by exploiting this vulnerability
- **Proof of Concept**: If available, include code or commands that demonstrate the issue
- **Suggested Fix**: If you have ideas for remediation

### Response Timeline

- **Acknowledgment**: Within 48 hours of report submission
- **Initial Assessment**: Within 7 days
- **Resolution Target**: Critical issues within 30 days, others within 90 days
- **Disclosure**: Coordinated disclosure after fix is released

### Recognition

We appreciate security researchers who help improve Pi Monitor. Contributors who responsibly disclose vulnerabilities will be:

- Credited in the release notes (unless they prefer anonymity)
- Added to our security acknowledgments

---

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |
| < 1.0   | :x:                |

---

## Security Audit Report

**Project:** Pi Monitor
**Audit Date:** 2025-12-31
**Auditor:** Security Analysis

### Executive Summary

Pi Monitor is a **zero-dependency** Python application that uses only the Python standard library. This significantly reduces the attack surface compared to projects with external dependencies.

**Overall Risk Level: LOW**

The project has minimal security concerns due to its intentional simplicity and zero external dependencies.

---

### Audit Checklist

| Category | Status | Notes |
|----------|--------|-------|
| Hardcoded Secrets | :white_check_mark: Pass | No credentials, API keys, or secrets in code |
| SQL Injection | :white_check_mark: N/A | No database usage |
| Command Injection | :white_check_mark: Pass | No eval/exec/subprocess/os.system usage |
| Insecure Dependencies | :white_check_mark: Pass | Zero runtime dependencies |
| Input Validation | :white_check_mark: Pass | Proper path matching, XSS escaping |
| Path Traversal | :white_check_mark: Pass | All file paths are hardcoded |
| Authentication | :warning: Advisory | No auth (intentional for LAN use) |
| CORS Configuration | :warning: Advisory | Wildcard CORS (intentional for LAN use) |
| HTTPS/TLS | :warning: Advisory | HTTP only (intentional for LAN use) |

---

### Detailed Findings

#### 1. No Hardcoded Secrets

**Status:** :white_check_mark: Pass

No hardcoded passwords, API keys, tokens, certificates, or credentials were found in the codebase.

#### 2. SQL Injection

**Status:** :white_check_mark: Not Applicable

This project does not use any database. No SQL, SQLite, MySQL, PostgreSQL, or ORM code is present.

#### 3. Command Injection

**Status:** :white_check_mark: Pass

No dangerous functions found:
- No `eval()` or `exec()`
- No `subprocess` calls
- No `os.system()` or `os.popen()`
- No `shell=True` patterns

#### 4. Insecure Dependencies

**Status:** :white_check_mark: Pass

| Category | Count | Notes |
|----------|-------|-------|
| Runtime Dependencies | 0 | Uses only Python standard library |
| Known Vulnerabilities | 0 | N/A |
| Supply Chain Risk | Minimal | No third-party packages |

**Standard Library Modules Used:**

**Agent:**
- `json` - JSON encoding/decoding
- `socket` - Network operations
- `os` - OS-level calls (limited to `statvfs`)
- `time` - Timing functions
- `http.server` - HTTP server
- `datetime` - Date/time handling

**Dashboard:**
- `json` - JSON handling
- `socket` - Network operations
- `threading` - Multi-threading
- `time` - Timing functions
- `http.server` - HTTP server
- `urllib.request` - HTTP client
- `datetime` - Date/time handling

#### 5. Input Validation

**Status:** :white_check_mark: Pass

**HTTP Path Handling:**
- Agent: Uses exact match `if self.path in ("/", "/metrics")`
- Dashboard: Uses exact match `if self.path == "/"`
- No path parsing or traversal possible

**XSS Protection:**
- Dashboard properly implements HTML escaping via `escapeHtml()`:

```javascript
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
```

**Unsafe Deserialization:**
- No `pickle`, `marshal`, or `yaml.load` usage
- Only `json.loads()` which is safe

#### 6. Path Traversal

**Status:** :white_check_mark: Pass

All file system access uses hardcoded paths:
- `/sys/class/thermal/thermal_zone0/temp`
- `/proc/stat`
- `/proc/meminfo`
- `/proc/uptime`
- `/proc/loadavg`
- `/proc/device-tree/model`

No user input affects file paths.

#### 7. Authentication/Authorization

**Status:** :warning: Advisory

**Issue:** No authentication required to access metrics or dashboard.

**Location:** All HTTP endpoints in agent and dashboard.

**Impact:** Anyone on the same network can view system metrics.

**Context:** This is intentional for a LAN-only monitoring tool.

**Recommendation:**
- Acceptable for trusted home/internal networks
- For sensitive environments, implement:
  - Reverse proxy with authentication (nginx, Caddy)
  - Firewall rules to restrict access

#### 8. CORS Configuration

**Status:** :warning: Advisory

**Issue:** `Access-Control-Allow-Origin: *` allows any origin.

**Location:** `agent/pi_monitor_agent.py:205`

**Impact:** Any website could query the agent's metrics endpoint.

**Context:** This is intentional to allow flexible dashboard deployments.

**Recommendation:**
- Acceptable for local LAN use
- For stricter security, use a reverse proxy to restrict origins

#### 9. HTTP/HTTPS

**Status:** :warning: Advisory

**Issue:** HTTP servers use plain HTTP without encryption.

**Location:** `agent/pi_monitor_agent.py:235`, `dashboard/pi_monitor_dashboard.py:482`

**Impact:** Metrics data transmitted in plaintext.

**Context:** Acceptable for trusted LAN networks.

**Recommendation:**
- For LAN-only use: Current implementation is acceptable
- For internet exposure: Use a reverse proxy with TLS termination
- Never expose ports 5555/8080 directly to the internet

---

### Systemd Security Hardening

The included service files implement good security practices:

```ini
# Security hardening options
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
```

**Status:** Well-configured security hardening.

---

### Python Version Security

| Python Version | Security Status | Recommendation |
|----------------|-----------------|----------------|
| Python 3.7 | End of Life | Upgrade |
| Python 3.8 | End of Life | Upgrade |
| Python 3.9 | Security fixes until Oct 2025 | Acceptable |
| Python 3.10 | Security fixes until Oct 2026 | Good |
| Python 3.11 | Security fixes until Oct 2027 | Recommended |
| Python 3.12+ | Active support | Recommended |

**Recommendation:** Deploy on Python 3.11+ for active security support.

---

### Security Best Practices for Deployment

1. **Network Security**
   - Keep Pi Monitor on a trusted LAN only
   - Use firewall rules to restrict access to ports 5555 and 8080
   - Never expose directly to the internet

2. **TLS/HTTPS** (if needed)
   - Use a reverse proxy (nginx, Caddy) for TLS termination
   - Example nginx configuration:
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /path/to/cert.pem;
       ssl_certificate_key /path/to/key.pem;

       location / {
           proxy_pass http://localhost:8080;
       }
   }
   ```

3. **Authentication** (if needed)
   - Configure basic auth in your reverse proxy
   - Or use VPN for network-level access control

4. **Keep Updated**
   - Run on Python 3.11+ for security patches
   - Monitor this repository for security advisories
   - Subscribe to release notifications

---

### Development Security

For contributors:

1. **Pre-commit Hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Security Scanning**
   ```bash
   pip install bandit safety pip-audit
   bandit -r agent/ dashboard/
   safety check
   pip-audit
   ```

3. **Code Review**
   - All PRs should be reviewed for security implications
   - Use the security checklist in pull request templates

---

### Conclusion

Pi Monitor has a **strong security posture** due to its zero-dependency design and careful implementation. The advisory items (HTTP-only, no auth, wildcard CORS) are appropriate for its intended use case as a LAN-only monitoring tool.

For internet-facing deployments, use a reverse proxy with TLS and authentication.
