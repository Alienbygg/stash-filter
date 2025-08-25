# Contributing to Stash-Filter

Thank you for your interest in contributing to Stash-Filter! This document provides guidelines and information for contributors.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### 1. Fork the Repository
```bash
git clone https://github.com/your-username/stash-filter.git
cd stash-filter
```

### 2. Set Up Development Environment
See [DEVELOPMENT.md](DEVELOPMENT.md) for detailed setup instructions.

### 3. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 4. Make Your Changes
- Follow the existing code style
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 5. Commit Your Changes
Use conventional commit messages:
```bash
git commit -m "feat: add new scene filtering options"
git commit -m "fix: resolve API connection timeout issue"
git commit -m "docs: update installation instructions"
```

### 6. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```
Then create a pull request on GitHub.

## Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions small and focused
- Use type hints where possible

### Example Code Style
```python
def calculate_scene_score(scene: Dict[str, Any], preferences: UserPreferences) -> float:
    """
    Calculate relevance score for a scene based on user preferences.
    
    Args:
        scene: Dictionary containing scene metadata
        preferences: User preference configuration
        
    Returns:
        float: Relevance score between 0.0 and 1.0
        
    Raises:
        ValueError: If scene data is invalid
    """
    if not scene.get('title'):
        raise ValueError("Scene must have a title")
        
    score = 0.0
    # Implementation here...
    return score
```

### Testing
- Write unit tests for all new functions
- Add integration tests for API endpoints
- Maintain test coverage above 80%
- Use descriptive test names

```python
def test_scene_filtering_excludes_unwanted_categories():
    """Test that scenes with unwanted categories are filtered out."""
    # Arrange
    scene = {"categories": ["unwanted_category"]}
    config = {"unwanted_categories": ["unwanted_category"]}
    
    # Act
    result = should_filter_scene(scene, config)
    
    # Assert
    assert result is True
```

### Documentation
- Update README.md for user-facing changes
- Update API.md for API changes
- Add inline code comments for complex logic
- Include examples in docstrings

## Types of Contributions

### Bug Fixes
- Check existing issues first
- Include steps to reproduce
- Add tests that verify the fix
- Reference the issue in your PR

### New Features
- Discuss major features in an issue first
- Follow the existing architecture patterns
- Include comprehensive tests
- Update documentation

### Documentation
- Fix typos and improve clarity
- Add examples and use cases
- Update outdated information
- Improve installation/setup guides

### Performance Improvements
- Profile code to identify bottlenecks
- Include benchmarks in PR description
- Ensure changes don't break existing functionality

## Project Structure Guidelines

### Adding New API Endpoints
1. Add route to `app/routes/api.py`
2. Implement business logic in `app/services/`
3. Add database models if needed in `app/models/`
4. Update `API.md` documentation
5. Add tests in `tests/api/`

### Adding New Web Pages
1. Create template in `templates/`
2. Add route to `app/routes/main.py`
3. Add static assets to `static/`
4. Update navigation if needed
5. Add tests for the new functionality

### Database Changes
1. Modify models in `app/models/`
2. Test with fresh database
3. Document migration steps if needed
4. Update example data/fixtures

## Pull Request Guidelines

### Before Submitting
- [ ] Code follows project style guidelines
- [ ] All tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] No sensitive data (API keys, IPs) in commits
- [ ] Commit messages follow conventional format

### Pull Request Description
Include:
- Clear description of changes
- Link to related issues
- Screenshots for UI changes
- Breaking change notes if applicable
- Testing instructions

### Example PR Description
```markdown
## Description
Add support for custom scene rating thresholds in the filtering system.

## Related Issues
Fixes #123

## Changes Made
- Added `min_rating` field to Config model
- Updated scene filtering logic to respect rating threshold
- Added settings UI for rating configuration
- Added unit tests for new filtering behavior

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing with various rating configurations
- [ ] Existing scenes still filter correctly

## Screenshots
[Include screenshots for UI changes]

## Breaking Changes
None

## Migration Steps
Database will auto-upgrade with new `min_rating` column.
```

## Review Process

### What We Look For
- Code quality and readability
- Test coverage and quality
- Documentation completeness
- Performance considerations
- Security implications

### Review Feedback
- Address all reviewer comments
- Ask questions if feedback is unclear
- Make requested changes promptly
- Update PR description if scope changes

## Getting Help

### Questions and Discussions
- Use GitHub Discussions for general questions
- Join issue discussions for specific problems
- Check existing documentation first

### Reporting Issues
Include:
- Clear reproduction steps
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant log snippets (remove sensitive data)

### Feature Requests
- Check existing issues/discussions first
- Explain the use case clearly
- Consider implementation complexity
- Be open to alternative solutions

## Release Process

### Version Management
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Document changes in CHANGELOG.md
- Tag releases with git tags
- Update version in `app/__init__.py`

### Release Types
- **Major**: Breaking changes, major features
- **Minor**: New features, significant improvements
- **Patch**: Bug fixes, small improvements

## Recognition

Contributors will be acknowledged in:
- README.md contributors section
- GitHub contributors page
- Release notes for significant contributions

## Resources

- [DEVELOPMENT.md](DEVELOPMENT.md) - Development setup
- [API.md](API.md) - API documentation
- [GitHub Issues](https://github.com/your-username/stash-filter/issues) - Bug reports and feature requests
- [GitHub Discussions](https://github.com/your-username/stash-filter/discussions) - Community discussions

## License

By contributing to this project, you agree that your contributions will be licensed under the same license as the project (MIT License).
