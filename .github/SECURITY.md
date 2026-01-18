# Security Policy

## Reporting Security Vulnerabilities

We take the security of this project seriously. If you discover a security vulnerability, please follow these steps:

### For Documentation Repository

Currently, this repository contains only documentation (research paper and metadata). However, if you discover any security concerns such as:

- Malicious content in files
- Compromised checksums
- Repository access issues
- Concerns about file integrity

### How to Report

**Please do NOT create a public GitHub issue for security vulnerabilities.**

Instead, please report security vulnerabilities by:

1. **Preferred:** Use GitHub's Security Advisory feature:
   - Go to the "Security" tab
   - Click "Report a vulnerability"
   - Fill out the form with details

2. **Alternative:** Email the repository maintainer directly:
   - Contact information can be found in `CITATION.cff` or commit history

### What to Include

Please include the following information in your report:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Any suggested fixes or mitigations
- Your contact information for follow-up

### Response Timeline

- We aim to acknowledge receipt of vulnerability reports within **48 hours**
- We will provide an initial assessment within **5 business days**
- We will work with you to understand and resolve the issue promptly

### Disclosure Policy

- We follow responsible disclosure practices
- We request that you do not publicly disclose the vulnerability until we have had a chance to address it
- We will credit you for the discovery (unless you prefer to remain anonymous)

## Security Best Practices

### For Users

When using materials from this repository:

1. **Verify File Integrity:**
   ```bash
   sha256sum "Cascading Agent Architecture for Memory Retrieval.pdf"
   # Compare with checksums in checksums_with_frontmatter.json
   ```

2. **Clone from Official Sources:**
   - Always clone from the official GitHub repository
   - Verify the repository URL and owner

3. **Check Commit Signatures:**
   ```bash
   git log --show-signature
   ```

### For Future Code Contributions

If implementation code is added to this repository:

- All dependencies must be audited before inclusion
- Security scanning must pass before merging
- Dependencies must be pinned to specific versions
- Regular security updates via Dependabot

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Security Updates

Security-related updates will be:

- Documented in `CHANGELOG.md`
- Tagged with appropriate version numbers
- Announced in GitHub Releases
- Highlighted in the repository README

## Attribution

We appreciate responsible disclosure and will acknowledge security researchers who help improve the project's security (with their permission).

Thank you for helping keep this project and its users safe!
