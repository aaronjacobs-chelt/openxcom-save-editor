# Contributing to OpenXCom Save Editor

Thank you for your interest in contributing to the OpenXCom Save Editor! This document provides guidelines for contributing to the project.

## Getting Started

### Development Setup

1. **Fork and clone the repository**
```bash
git clone https://github.com/yourusername/openxcom-save-editor.git
cd openxcom-save-editor
```

2. **Set up development environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Run tests to ensure everything works**
```bash
pytest tests/ -v
```

### Project Structure

```
openxcomeditor/
├── src/xcom_save_editor/          # Main package
│   ├── game_editors/              # Feature-specific managers
│   ├── utils/                     # Core utilities
│   ├── cli.py                     # Interactive CLI
│   └── editor.py                  # Main controller
├── tests/                         # Test suite
├── README.md                      # Documentation
└── requirements.txt               # Dependencies
```

## How to Contribute

### Reporting Issues

When reporting issues, please include:

- **OpenXCom Extended version** and mod information
- **Save file details** (mod, game version, etc.)
- **Error messages** or unexpected behavior
- **Steps to reproduce** the issue
- **Expected vs actual behavior**

### Feature Requests

Before requesting features:

1. Check existing issues and discussions
2. Describe the use case and why it would be helpful
3. Consider if it fits the project's scope (X-Com Files mod support)

### Code Contributions

#### Before You Start

1. **Check existing issues** - someone might already be working on it
2. **Create an issue** to discuss major changes before implementing
3. **Keep changes focused** - one feature/fix per pull request

#### Development Guidelines

1. **Code Style**
   - Follow PEP 8 Python style guide
   - Use type hints where appropriate
   - Write docstrings for public methods
   - Keep functions focused and small

2. **Safety First**
   - Always validate input data
   - Maintain backup functionality
   - Test with real save files
   - Never skip validation checks

3. **Testing**
   - Write tests for new features
   - Ensure existing tests still pass
   - Test with different save file scenarios
   - Include edge cases in testing

4. **Documentation**
   - Update README.md for new features
   - Add docstrings to new methods
   - Comment complex logic
   - Update CLI help text if needed

#### Pull Request Process

1. **Fork the repository** and create a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the guidelines above

3. **Test thoroughly**
   ```bash
   pytest tests/ -v
   ```

4. **Update documentation** as needed

5. **Commit with clear messages**
   ```bash
   git commit -m "Add feature: brief description"
   ```

6. **Push to your fork and create a pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Fill out the pull request template** with:
   - Description of changes
   - Testing performed
   - Screenshots if UI changes
   - Breaking changes if any

### Types of Contributions Welcome

#### 🐛 **Bug Fixes**
- Save file corruption issues
- CLI interface problems
- Data validation errors
- Cross-platform compatibility

#### ✨ **New Features**
- Support for additional OpenXCom Extended mods
- New editing capabilities
- UI/UX improvements
- Performance optimizations

#### 📚 **Documentation**
- Improved README sections
- Code documentation
- Usage examples
- Troubleshooting guides

#### 🧪 **Testing**
- Additional test cases
- Edge case testing
- Different save file formats
- Cross-platform testing

### Mod Compatibility

When adding support for new mods:

1. **Focus on major, stable mods** first
2. **Maintain backward compatibility** with X-Com Files
3. **Test thoroughly** with actual save files
4. **Document mod-specific features** clearly

### Code Review Process

All submissions require review before merging:

1. **Automated checks** must pass (tests, linting)
2. **Manual review** by maintainers
3. **Testing** with various save files
4. **Documentation review** for clarity

Reviews focus on:
- Code quality and maintainability
- Safety and data integrity
- User experience
- Test coverage
- Documentation completeness

## Development Tips

### Working with Save Files

- **Always work with backup copies** during development
- **Test with multiple save file versions**
- **Validate YAML structure** after modifications
- **Use the validator module** for integrity checks

### Debugging

- Use the built-in logging throughout the codebase
- Test CLI flows manually with various inputs
- Validate changes against original save file data
- Check backup/restore functionality regularly

### Common Pitfalls

- **Don't modify save structure** without understanding implications
- **Always preserve header document** in multi-document YAML
- **Validate data types** before assigning values
- **Handle missing data gracefully** (not all saves have all fields)

## Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Comments**: Check existing code for implementation patterns

## Recognition

Contributors will be recognized in the project documentation and releases. Thank you for helping make this tool better for the OpenXCom community!

---

*By contributing, you agree that your contributions will be licensed under the MIT License.*