# Contributing to Cascading Agent Architecture for Memory Retrieval

Thank you for your interest in contributing to this project! This document provides guidelines for different types of contributions.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Contribution Workflow](#contribution-workflow)
- [Style Guidelines](#style-guidelines)
- [Community](#community)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## How Can I Contribute?

### Reporting Issues

Found a problem with the paper or repository? Please help us improve by:

1. **Search existing issues** to avoid duplicates
2. **Create a new issue** using the appropriate template:
   - Bug reports for errors or inaccuracies in the paper
   - Feature requests for documentation improvements
   - General questions for discussions

### Suggesting Improvements

We welcome suggestions for:

- Clarifications in the paper's explanations
- Additional examples or use cases
- Corrections to errors or typos
- Enhanced documentation
- Reference implementations of the architecture

### Contributing Code

If you'd like to contribute a reference implementation:

1. **Open an issue first** to discuss your proposed implementation
2. **Wait for approval** before starting significant work
3. **Follow the code standards** outlined below
4. **Include tests** for any code contributions
5. **Update documentation** as needed

## Getting Started

### For Documentation Contributions

1. **Fork the repository**
   ```bash
   gh repo fork theodddoctorr/Cascading-Agent-Architecture-for-Memory-Retrieval
   ```

2. **Create a branch**
   ```bash
   git checkout -b fix/typo-in-section-3
   ```

3. **Make your changes**
   - Edit documentation files
   - Ensure proper formatting

4. **Verify changes**
   - Check spelling and grammar
   - Verify markdown rendering
   - Update checksums if needed

### For Code Contributions

1. **Fork and clone**
   ```bash
   gh repo fork theodddoctorr/Cascading-Agent-Architecture-for-Memory-Retrieval
   git clone https://github.com/YOUR-USERNAME/Cascading-Agent-Architecture-for-Memory-Retrieval
   cd Cascading-Agent-Architecture-for-Memory-Retrieval
   ```

2. **Set up development environment**
   - Install required dependencies
   - Set up linters and formatters
   - Configure pre-commit hooks

3. **Create a feature branch**
   ```bash
   git checkout -b feature/python-implementation
   ```

## Contribution Workflow

### 1. Before You Start

- Check the [issue tracker](../../issues) for existing work
- Open an issue to discuss significant changes
- Get feedback from maintainers before investing time

### 2. Making Changes

- **Write clear commit messages** following [Conventional Commits](https://www.conventionalcommits.org/)
  ```
  feat: Add Python reference implementation
  fix: Correct typo in Section 3.2
  docs: Update README with usage examples
  ```

- **Keep commits focused** - one logical change per commit
- **Update relevant documentation** in the same commit

### 3. Testing Your Changes

For documentation:
- [ ] Spell check all changes
- [ ] Verify markdown renders correctly
- [ ] Check all links work
- [ ] Update checksums if files changed

For code:
- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] No security vulnerabilities introduced
- [ ] Documentation updated

### 4. Submitting Changes

1. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request**
   - Use a clear, descriptive title
   - Fill out the PR template completely
   - Reference any related issues
   - Explain the motivation for changes

3. **Respond to feedback**
   - Be responsive to review comments
   - Make requested changes promptly
   - Keep the conversation professional

## Style Guidelines

### Documentation

- Use clear, concise language
- Follow existing formatting conventions
- Use proper markdown syntax
- Include code examples where helpful
- Keep line length under 100 characters for readability

### Code (if contributing implementations)

#### Python
- Follow [PEP 8](https://pep8.org/)
- Use type hints
- Maximum line length: 100 characters
- Use `black` for formatting
- Use `ruff` for linting

#### JavaScript/TypeScript
- Follow the existing code style
- Use ESLint and Prettier
- Prefer TypeScript over JavaScript
- Include JSDoc comments for public APIs

#### General
- Write self-documenting code
- Add comments only when necessary
- Include docstrings for all public functions
- Write unit tests for all new functionality

### Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
docs: Fix typo in architecture diagram caption

fix: Correct citation year in CITATION.cff

feat: Add Python implementation of cascading retrieval

This implementation demonstrates the core concepts outlined
in Section 4 of the paper, including memory tier management
and query optimization.

Closes #23
```

## Review Process

1. **Automated Checks**
   - All CI/CD checks must pass
   - Code must pass linting
   - Tests must pass

2. **Peer Review**
   - At least one maintainer must review
   - All comments must be addressed
   - Changes may be requested

3. **Merge**
   - Approved PRs will be merged by maintainers
   - Squash merging preferred for cleaner history

## Recognition

Contributors will be:

- Listed in commit history
- Mentioned in release notes (for significant contributions)
- Added to a CONTRIBUTORS.md file (if created)

## Questions?

- **General questions:** Open a [Discussion](../../discussions)
- **Bug reports:** Create an [Issue](../../issues/new/choose)
- **Security concerns:** See [SECURITY.md](SECURITY.md)

## License

By contributing, you agree that your contributions will be licensed under:

- **Documentation/Paper:** CC BY 4.0
- **Code:** Apache-2.0

Thank you for contributing to the advancement of AI agent architectures! 🚀
