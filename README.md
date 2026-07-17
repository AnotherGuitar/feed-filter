# Python Project Template

A modern Python project template with best practices, tooling, and deployment flexibility. Designed for rapid project creation with production-ready defaults.

## Overview

This template provides:

- **Modern Python** (3.12+ minimum, 3.13 recommended)
- **Dependency Management** with [uv](https://github.com/astral-sh/uv) (fast, reliable)
- **Type-Safe Configuration** with pydantic-settings
- **Structured Logging** with structlog
- **Testing** with pytest, pytest-cov, pytest-asyncio, pytest-mock
- **Code Quality** with ruff (linting + formatting) and mypy (type checking)
- **Pre-commit Hooks** for automated checks
- **Docker Support** for local development and deployment
- **CI/CD** with GitHub Actions
- **Flexible Deployment** (AWS, local NAS, cloud VMs, etc.)

## Quick Start

### 1. Copy This Template

```bash
# Copy template to new project
cp -r python-project-template your-new-project
cd your-new-project

# Rename the package
mv src/feed_filter src/your_actual_name
find . -type f -exec sed -i '' 's/feed-filter/your-actual-name/g' {} +
find . -type f -exec sed -i '' 's/feed_filter/your_actual_name/g' {} +
```

### 2. Initial Setup

```bash
# Copy environment variables template
cp .env.sample .env

# Edit .env with your settings
# (open .env in your editor and customize)

# Run complete setup (installs dependencies + pre-commit hooks)
make setup
```

### 3. Start Developing

```bash
# IMPORTANT: Always activate virtual environment before working
source .venv/bin/activate

# Run the application
python -m feed_filter.main

# Or use make
make run  # if you've defined a run target
```

**Note for AI Assistants**: Always activate the virtual environment (`source .venv/bin/activate`) before installing dependencies or running Python commands in this project. This ensures all packages are installed in the project's isolated environment.

## Available Commands

Run `make help` to see all available commands:

```bash
make help              # Show all available commands
make install           # Install production dependencies
make install-dev       # Install all dependencies (including dev tools)
make test              # Run tests
make test-cov          # Run tests with coverage report
make lint              # Run linting checks
make format            # Format code
make type-check        # Run type checking
make pre-commit        # Run all pre-commit hooks
make docker-build      # Build Docker image
make docker-up         # Start Docker containers
make docker-down       # Stop Docker containers
make clean             # Clean up generated files
```

## Project Structure

```
.
├── .github/
│   └── workflows/
│       └── ci.yml                    # GitHub Actions CI/CD
├── src/
│   └── feed_filter/
│       ├── __init__.py
│       ├── config.py                 # Configuration management
│       ├── logger.py                 # Logging setup
│       └── main.py                   # Application entry point
├── tests/
│   ├── __init__.py
│   ├── conftest.py                   # Pytest fixtures
│   ├── test_config.py
│   └── test_main.py
├── .env.sample                       # Environment variables template
├── .editorconfig                     # Editor configuration
├── .gitignore
├── .pre-commit-config.yaml           # Pre-commit hooks
├── docker-compose.yml                # Docker orchestration
├── Dockerfile                        # Container definition
├── Makefile                          # Common commands
├── pyproject.toml                    # Project configuration
├── README.md                         # This file
└── SETUP.md                          # Detailed setup guide
```

## Optional Dependencies

Install optional dependency groups as needed:

```bash
# Web/HTTP libraries
uv sync --extra web

# CLI tools
uv sync --extra cli

# Data science (pandas/numpy)
uv sync --extra data-pandas

# Data science (polars)
uv sync --extra data-polars

# All extras
uv sync --all-extras
```

## Docker Usage

```bash
# Build and run with Docker
make docker-build
make docker-up

# View logs
make docker-logs

# Stop containers
make docker-down
```

## Testing

```bash
# Run tests
make test

# Run with coverage
make test-cov

# Open coverage report
open htmlcov/index.html
```

## Code Quality

```bash
# Format code
make format

# Run linting
make lint

# Type checking
make type-check

# Run all checks (pre-commit)
make pre-commit
```

## Production Considerations

When preparing for production:

1. **Security Checks**: Uncomment security scanning in [.pre-commit-config.yaml](.pre-commit-config.yaml)
2. **Environment Variables**: Review [.env.sample](.env.sample) and ensure all secrets are properly configured
3. **Logging**: Structured logs automatically output JSON in production (when `APP_ENV=production`)
4. **Docker**: Build optimized production images (see [Dockerfile](Dockerfile) comments)
5. **CI/CD**: Configure [GitHub Actions](.github/workflows/ci.yml) for your deployment target

## Recommended IDE Extensions

See [SETUP.md - Recommended Cursor/VSCode Extensions](SETUP.md#recommended-cursorvscode-extensions) for the complete list of extensions and installation commands.

## Resources

- [uv Documentation](https://github.com/astral-sh/uv)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [pytest Documentation](https://docs.pytest.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [structlog Documentation](https://www.structlog.org/)

## Next Steps

1. Read [SETUP.md](SETUP.md) for detailed setup instructions
2. Customize [pyproject.toml](pyproject.toml) with your project details
3. Update [src/feed_filter/main.py](src/feed_filter/main.py) with your application logic
4. Write tests in [tests/](tests/)
5. Configure CI/CD in [.github/workflows/ci.yml](.github/workflows/ci.yml)

## License

[Add your license here]
