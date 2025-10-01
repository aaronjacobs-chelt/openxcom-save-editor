# Security Policy

## Supported Versions

We take security seriously and provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.x.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in the OpenXCom Save Editor, please help us maintain the security of our users by reporting it responsibly.

### Where to Report

Please **DO NOT** create a public GitHub issue for security vulnerabilities.

Instead, please report security issues by:

1. **Email**: Send details to the maintainer via GitHub's contact features
2. **Private Issue**: Use GitHub's private vulnerability reporting feature (if available)
3. **Direct Message**: Contact maintainers through available channels

### What to Include

When reporting a security vulnerability, please include:

- **Description**: A clear description of the vulnerability
- **Impact**: What could an attacker accomplish?
- **Reproduction**: Step-by-step instructions to reproduce the issue
- **Affected Versions**: Which versions are affected?
- **Environment**: Operating system, Python version, etc.
- **Proof of Concept**: If applicable, include a minimal example

### Response Timeline

We aim to respond to security reports within:

- **Initial Response**: 48 hours
- **Confirmation**: 1 week 
- **Fix Release**: 2-4 weeks (depending on complexity)

### Security Considerations

The OpenXCom Save Editor handles sensitive data (save files) and should be used with caution:

#### Potential Security Concerns

1. **Save File Corruption**: Malformed saves could potentially cause issues
2. **File System Access**: The tool reads/writes files on the user's system
3. **YAML Parsing**: Malicious YAML could theoretically cause issues
4. **Backup Management**: Sensitive save data is stored in backups

#### Security Best Practices for Users

- **Only edit your own save files** - Don't run the tool on untrusted saves
- **Keep backups secure** - Save files may contain personal gaming data
- **Use in isolated environment** - Consider using a virtual machine for untrusted saves
- **Keep tool updated** - Use the latest version for security fixes

#### For Developers

- **Input Validation**: Always validate save file data before processing
- **Safe YAML Loading**: Use safe YAML loading methods
- **File Path Validation**: Validate file paths to prevent directory traversal
- **Error Handling**: Don't expose sensitive information in error messages

### Scope

This security policy covers:

- The main application code (`src/xcom_save_editor/`)
- Dependencies and their known vulnerabilities
- File handling and backup procedures
- Input validation and data processing

### Out of Scope

The following are generally outside our security scope:

- Issues with OpenXCom Extended itself
- Vulnerabilities in Python or OS-level components
- Issues with third-party mods or save files
- Denial of service through resource exhaustion
- Issues requiring physical access to the machine

## Acknowledgments

We appreciate security researchers who:

- Follow responsible disclosure practices
- Provide clear and detailed reports
- Allow reasonable time for fixes
- Work with us to verify fixes

Contributors who report valid security issues will be acknowledged in our security advisories (unless they prefer to remain anonymous).

## Additional Resources

- [OWASP Secure Coding Practices](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)
- [Python Security Guidelines](https://python.org/dev/security/)
- [YAML Security Considerations](https://pyyaml.org/wiki/PyYAMLDocumentation)

Thank you for helping keep the OpenXCom Save Editor and its users safe!