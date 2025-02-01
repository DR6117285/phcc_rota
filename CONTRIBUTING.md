# Contributing to Medical Rota System

First off, thank you for considering contributing to Medical Rota System! It's people like you that make this project such a great tool for medical professionals.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the [issue list](https://github.com/your-org/medical-rota-system/issues) as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* Use a clear and descriptive title
* Describe the exact steps which reproduce the problem
* Provide specific examples to demonstrate the steps
* Describe the behavior you observed after following the steps
* Explain which behavior you expected to see instead and why
* Include screenshots if possible
* Include error messages and stack traces

### Suggesting Enhancements

Enhancement suggestions are tracked as [GitHub issues](https://github.com/your-org/medical-rota-system/issues). When creating an enhancement suggestion, please provide:

* Use a clear and descriptive title
* Provide a step-by-step description of the suggested enhancement
* Provide specific examples to demonstrate the steps
* Describe the current behavior and explain which behavior you expected to see instead
* Explain why this enhancement would be useful
* List some other applications where this enhancement exists, if applicable

### Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. If you've changed APIs, update the documentation
4. Ensure the test suite passes
5. Make sure your code lints
6. Issue that pull request!

## Development Process

1. Clone the repository
```bash
git clone https://github.com/your-org/medical-rota-system.git
cd medical-rota-system
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install development dependencies
```bash
pip install -r requirements-dev.txt
```

4. Set up pre-commit hooks
```bash
pre-commit install
```

### Coding Style

* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
* Use type hints for all function parameters and return values
* Write docstrings for all public methods and classes
* Keep functions focused and small
* Use meaningful variable names
* Comment complex algorithms and business logic

### Testing

* Write unit tests for all new functionality
* Ensure all tests pass before submitting PR
* Maintain or improve code coverage
* Include both positive and negative test cases

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=medical_rota tests/

# Run specific test file
pytest tests/test_optimization.py
```

### Documentation

* Update documentation for all new features and changes
* Follow the existing documentation style
* Include code examples where appropriate
* Update the changelog

## Project Structure

```
medical_rota/
├── core/           # Core functionality
├── models/         # Data models
├── strategies/     # Optimization strategies
├── utils/          # Utility functions
├── tests/          # Test suite
└── docs/           # Documentation
```

### Core Components

1. **RotationEngine**: Schedule generation and management
2. **Optimizer**: Schedule optimization
3. **ConflictResolver**: Conflict detection and resolution
4. **DataModels**: Schedule, Shift, Staff representations

## Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* Consider starting the commit message with an applicable emoji:
    * 🎨 `:art:` when improving the format/structure of the code
    * 🐎 `:racehorse:` when improving performance
    * 🚱 `:non-potable_water:` when plugging memory leaks
    * 📝 `:memo:` when writing docs
    * 🐛 `:bug:` when fixing a bug
    * 🔥 `:fire:` when removing code or files
    * 💚 `:green_heart:` when fixing the CI build
    * ✅ `:white_check_mark:` when adding tests
    * 🔒 `:lock:` when dealing with security
    * ⬆️ `:arrow_up:` when upgrading dependencies
    * ⬇️ `:arrow_down:` when downgrading dependencies

## Pull Request Process

1. Update the README.md with details of changes to the interface
2. Update the documentation with details of any new functionality
3. Update the CHANGELOG.md with a note describing your changes
4. The PR must be approved by at least one maintainer
5. PR title should follow conventional commits format

### PR Review Process

* Maintainers will review PRs regularly
* Feedback must be addressed before merging
* CI checks must pass
* Documentation must be updated
* Tests must pass and coverage maintained

## Release Process

1. Update version number in `__init__.py`
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. Tag the release with version number
5. Update PyPI package

## Additional Notes

### Issue and Pull Request Labels

* `bug` - Confirmed bugs or reports likely to be bugs
* `enhancement` - New feature or request
* `documentation` - Documentation only changes
* `duplicate` - This issue or pull request already exists
* `good first issue` - Good for newcomers
* `help wanted` - Extra attention is needed
* `invalid` - This doesn't seem right
* `question` - Further information is requested
* `wontfix` - This will not be worked on

## Recognition

Contributors will be recognized in:

* CONTRIBUTORS.md file
* Release notes
* Project documentation

## Questions?

* Feel free to open an issue
* Contact the maintainers
* Join our community chat

Thank you for contributing to Medical Rota System! 🎉 