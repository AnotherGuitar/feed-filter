# Setup & Onboarding Guide

This guide provides detailed instructions for setting up a new project based on this template, configuring your development environment, and understanding the project structure.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Creating a New Project from Template](#creating-a-new-project-from-template)
- [Initial Setup (First Time)](#initial-setup-first-time)
- [Daily Development Workflow](#daily-development-workflow)
- [Understanding the Project Structure](#understanding-the-project-structure)
- [Configuration Management](#configuration-management)
- [Testing Strategy](#testing-strategy)
- [Docker Workflow](#docker-workflow)
- [CI/CD Pipeline](#cicd-pipeline)
- [Deployment Options](#deployment-options)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.12+** (Python 3.13 recommended)
  - Check: `python3.13 --version` or `python3.12 --version`
  - Install: `brew install python@3.13` (macOS) or see [python.org](https://www.python.org/downloads/)
- **uv** - Fast Python package manager
  - Install: `brew install uv` (macOS) or `curl -LsSf https://astral.sh/uv/install.sh | sh`
  - Check: `uv --version`
- **Docker** (optional but recommended)
  - Install: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
  - Check: `docker --version`
- **Git**
  - Install: `brew install git` (macOS) or see [git-scm.com](https://git-scm.com/)
  - Check: `git --version`
- **make** (usually pre-installed on macOS/Linux)
  - Check: `make --version`

## Creating a New Project from Template

### Step 1: Copy the Template

```bash
# Navigate to your workspace
cd /path/to/your/workspace

# Copy the template directory
cp -r python-project-template my-new-project
cd my-new-project
```

### Step 2: Rename the Package

Replace `feed_filter` and `feed-filter` with your actual project name:

```bash
# Set your project name (use lowercase with underscores for package name)
PROJECT_NAME="my_awesome_project"
PROJECT_SLUG="my-awesome-project"

# Rename the source directory
mv src/feed_filter src/${PROJECT_NAME}

# Update all references in files
# macOS/BSD sed:
find . -type f \( -name "*.py" -o -name "*.toml" -o -name "*.yml" -o -name "*.yaml" -o -name "*.md" -o -name "Dockerfile" -o -name "docker-compose.yml" \) -exec sed -i '' "s/feed_filter/${PROJECT_NAME}/g" {} +
find . -type f \( -name "*.py" -o -name "*.toml" -o -name "*.yml" -o -name "*.yaml" -o -name "*.md" -o -name "Dockerfile" -o -name "docker-compose.yml" \) -exec sed -i '' "s/feed-filter/${PROJECT_SLUG}/g" {} +

# GNU sed (Linux):
# find . -type f \( -name "*.py" -o -name "*.toml" -o -name "*.yml" -o -name "*.yaml" -o -name "*.md" -o -name "Dockerfile" -o -name "docker-compose.yml" \) -exec sed -i "s/feed_filter/${PROJECT_NAME}/g" {} +
# find . -type f \( -name "*.py" -o -name "*.toml" -o -name "*.yml" -o -name "*.yaml" -o -name "*.md" -o -name "Dockerfile" -o -name "docker-compose.yml" \) -exec sed -i "s/feed-filter/${PROJECT_SLUG}/g" {} +
```

### Step 3: Update Project Metadata

Edit [pyproject.toml](pyproject.toml) and update:
- `name` - Your project name
- `version` - Starting version (e.g., "0.1.0")
- `description` - Brief project description
- `authors` - Your name and email (optional)
- `dependencies` - Add project-specific dependencies

### Step 4: Initialize Git Repository

```bash
# Initialize git
git init

# Create initial commit
git add .
git commit -m "Initial commit from python-project-template"

# (Optional) Create GitHub repository and push
# gh repo create my-new-project --private --source=. --remote=origin
# git push -u origin main
```

## Initial Setup (First Time)

### 1. Create Environment File

```bash
# Copy the environment template
cp .env.sample .env

# Edit .env with your settings
# Use your preferred editor: code .env, vim .env, nano .env, etc.
```

Edit [.env](.env) and configure:
- `APP_NAME` - Your application name
- `APP_ENV` - Environment (development, staging, production)
- `DEBUG` - Debug mode (true/false)
- `LOG_LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Add any additional configuration your project needs

### 2. Install Dependencies

```bash
# Option A: Quick setup with make (recommended)
make setup

# Option B: Manual setup
uv sync --python 3.13 --all-extras
uv run pre-commit install
```

This will:
- Create a virtual environment in `.venv/`
- Install all dependencies (production + dev)
- Install pre-commit hooks

### 3. Verify Installation

```bash
# Activate virtual environment
source .venv/bin/activate

# Verify installation
python --version  # Should show 3.13.x or 3.12.x
which python      # Should point to .venv/bin/python

# Run tests
make test

# Run the application
python -m ${PROJECT_NAME}.main
```

## Daily Development Workflow

### Starting Your Session

```bash
# 1. Navigate to project directory
cd /path/to/my-new-project

# 2. Activate virtual environment
source .venv/bin/activate

# 3. Pull latest changes (if working with a team)
git pull

# 4. Install any new dependencies
uv sync
```

### Development Cycle

```bash
# Write code in src/

# Run tests frequently
make test

# Check code quality
make lint
make type-check

# Format code
make format

# Run application
python -m ${PROJECT_NAME}.main
```

### Before Committing

```bash
# Run all checks
make pre-commit

# If checks pass, commit
git add .
git commit -m "Your commit message"

# Pre-commit hooks will run automatically
# Fix any issues and commit again if needed
```

## Understanding the Project Structure

### Source Code (`src/`)

```
src/feed_filter/
├── __init__.py          # Package initialization, version info
├── config.py            # Configuration management with pydantic
├── logger.py            # Structured logging setup
└── main.py              # Application entry point
```

**Key Concepts:**

- **config.py**: Type-safe configuration using pydantic-settings
  - Loads from `.env` file and environment variables
  - Validates configuration on startup
  - Provides typed access to settings

- **logger.py**: Structured logging with structlog
  - JSON output in production
  - Human-readable console output in development
  - Includes timestamps, log levels, and context

- **main.py**: Your application entry point
  - Replace with your actual application logic
  - Use as a reference for importing config and logger

### Tests (`tests/`)

```
tests/
├── __init__.py          # Test package initialization
├── conftest.py          # Shared pytest fixtures
├── test_config.py       # Configuration tests
└── test_main.py         # Application logic tests
```

**Testing Best Practices:**

1. **One test file per source file**: `test_module.py` tests `module.py`
2. **Use fixtures**: Define in `conftest.py` for reuse
3. **Mock external dependencies**: Use `pytest-mock` for mocking
4. **Test behavior, not implementation**: Focus on what code does, not how
5. **Aim for high coverage**: Run `make test-cov` regularly

### Configuration Files

- **pyproject.toml**: Central configuration for Python project
  - Dependencies and optional dependency groups
  - Tool configurations (pytest, ruff, mypy)
  - Build system configuration

- **.pre-commit-config.yaml**: Pre-commit hooks
  - Runs automatically before each commit
  - Includes linting, formatting, type checking
  - Add security checks for production projects

- **Makefile**: Common development commands
  - Provides consistent interface across projects
  - Combines multiple steps (e.g., `make setup`)
  - Documents available commands (`make help`)

- **.editorconfig**: Editor configuration
  - Ensures consistent formatting across editors
  - Works with VSCode, PyCharm, Sublime, etc.

## Configuration Management

### Environment Variables

The project uses pydantic-settings for type-safe configuration:

```python
# src/feed_filter/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "my-app"
    debug: bool = False
    # Add your settings here
```

### Adding New Configuration

1. **Define in config.py**:
```python
class Settings(BaseSettings):
    # ... existing settings ...

    # New setting with validation
    api_timeout: int = Field(default=30, ge=1, le=300)
    database_url: str = Field(..., description="Database connection string")
```

2. **Add to .env.sample**:
```bash
# .env.sample
API_TIMEOUT=30
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
```

3. **Update your .env**:
```bash
# .env (not committed to git)
API_TIMEOUT=60
DATABASE_URL=postgresql://myuser:mypass@localhost:5432/mydb
```

4. **Use in your code**:
```python
from feed_filter.config import settings

timeout = settings.api_timeout
db_url = settings.database_url
```

## Testing Strategy

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test file
uv run pytest tests/test_config.py

# Run specific test
uv run pytest tests/test_config.py::test_settings_defaults

# Run with verbose output
uv run pytest -v

# Run and stop on first failure
uv run pytest -x
```

### Writing Tests

**Example test structure**:

```python
# tests/test_mymodule.py
import pytest
from feed_filter.mymodule import MyClass

class TestMyClass:
    """Tests for MyClass."""

    def test_initialization(self):
        """Test MyClass can be initialized."""
        obj = MyClass(value=42)
        assert obj.value == 42

    def test_method_behavior(self):
        """Test MyClass.method behaves correctly."""
        obj = MyClass(value=10)
        result = obj.method()
        assert result == 20  # Example assertion

    @pytest.mark.asyncio
    async def test_async_method(self):
        """Test async methods."""
        obj = MyClass()
        result = await obj.async_method()
        assert result is not None
```

### Using Fixtures

```python
# tests/conftest.py
@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {"key": "value", "count": 42}

# tests/test_mymodule.py
def test_with_fixture(sample_data):
    """Test using fixture."""
    assert sample_data["count"] == 42
```

### Mocking

```python
from unittest.mock import patch

def test_with_mock(mocker):
    """Test with mocked dependency."""
    # Mock an external API call
    mock_response = mocker.patch("feed_filter.api.fetch_data")
    mock_response.return_value = {"status": "success"}

    # Your test code
    result = your_function_that_calls_api()
    assert result["status"] == "success"
```

## Docker Workflow

### Local Development with Docker

```bash
# Build the image
make docker-build

# Start containers
make docker-up

# View logs
make docker-logs

# Stop containers
make docker-down

# Open shell in container
make docker-shell
```

### Docker Compose Services

The default [docker-compose.yml](docker-compose.yml) includes:
- **app**: Your Python application
- **Commented examples**: PostgreSQL, Redis

**To add a database**:

1. Uncomment the `postgres` service in docker-compose.yml
2. Add database configuration to `.env`:
```bash
DB_HOST=postgres
DB_PORT=5432
DB_NAME=myapp
DB_USER=postgres
DB_PASSWORD=postgres
```
3. Update [config.py](src/feed_filter/config.py) with database settings
4. Rebuild: `make docker-build && make docker-up`

### Building Production Images

For production deployment, update [Dockerfile](Dockerfile):

```dockerfile
# Use production dependencies only
RUN uv pip install -e .

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# Run as non-root user (already configured)
USER appuser
```

## CI/CD Pipeline

### GitHub Actions

The template includes a basic CI workflow in [.github/workflows/ci.yml](.github/workflows/ci.yml):

**What it does**:
1. Runs on push/PR to main and develop branches
2. Tests on Python 3.12 and 3.13
3. Runs linting, formatting, type checking
4. Runs tests with coverage
5. Builds Docker image

**Customizing CI**:

1. **Add secrets**: Go to GitHub repo → Settings → Secrets
2. **Configure branches**: Edit `on.push.branches` in ci.yml
3. **Add deployment**: Add deployment steps after tests pass
4. **Add code coverage**: Uncomment Codecov section and add token

**Example: Add deployment to AWS ECS**:

```yaml
# Add to .github/workflows/ci.yml after test job
deploy:
  needs: test
  runs-on: ubuntu-latest
  if: github.ref == 'refs/heads/main'
  steps:
    - uses: actions/checkout@v4

    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1

    # Add your deployment steps here
```

## Deployment Options

This template is designed for flexible deployment:

### Option 1: AWS ECS (Container Service)

1. Build and push Docker image to ECR
2. Create ECS task definition
3. Deploy to ECS Fargate or EC2
4. Use Terraform for infrastructure as code

### Option 2: Local NAS (Docker)

1. Build Docker image: `make docker-build`
2. Save image: `docker save your-app > app.tar`
3. Copy to NAS and load: `docker load < app.tar`
4. Run with docker-compose on NAS

### Option 3: Cloud VM (DigitalOcean, Linode, etc.)

1. SSH into VM
2. Clone repository
3. Install dependencies: `make setup`
4. Run with systemd or supervisor

### Option 4: Serverless (AWS Lambda, Cloud Run, etc.)

1. Modify Dockerfile for serverless runtime
2. Deploy using platform-specific tools
3. Configure environment variables

## Troubleshooting

### Common Issues

**Issue**: `uv: command not found`
```bash
# Solution: Install uv
brew install uv  # macOS
# or
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Issue**: `python: No module named feed_filter`
```bash
# Solution: Ensure virtual environment is activated and package is installed
source .venv/bin/activate
uv sync
```

**Issue**: Pre-commit hooks fail
```bash
# Solution: Run formatting and fix issues
make format
make lint
# Then commit again
```

**Issue**: Docker build fails
```bash
# Solution: Clean Docker cache and rebuild
docker system prune -a
make docker-build
```

**Issue**: Tests fail in CI but pass locally
```bash
# Solution: Ensure same Python version
python --version  # Check local version
# Update .github/workflows/ci.yml if needed
```

### Getting Help

1. **Check logs**: `make docker-logs` or check application logs
2. **Run with debug**: Set `DEBUG=true` in `.env`
3. **Check dependencies**: `uv pip list`
4. **Clean and reinstall**: `make clean && make setup`

## Recommended Cursor/VSCode Extensions

Install these extensions for the best development experience:

### Essential Python Development
- [Claude Code](vscode:extension/anthropic.claude-code) - AI-powered coding assistant
- [Python](vscode:extension/ms-python.python) - Python language support
- [Python (Anysphere)](vscode:extension/anysphere.cursorpyright) - Python type checking and IntelliSense
- [Python Debugger](vscode:extension/ms-python.debugpy) - Python debugging support

### Code Quality & Formatting
- [markdownlint](vscode:extension/davidanson.vscode-markdownlint) - Markdown linting and style checking
- [YAML](vscode:extension/redhat.vscode-yaml) - YAML support with validation

### Git & Version Control
- [Git History](vscode:extension/donjayamanne.githistory) - View git log, file history, compare branches
- [GitHub Actions](vscode:extension/github.vscode-github-actions) - GitHub Actions support
- [GitHub Pull Requests](vscode:extension/github.vscode-pull-request-github) - Review and manage GitHub pull requests

### Docker & Containers
- [Docker](vscode:extension/ms-azuretools.vscode-docker) - Docker container management
- [Container Tools](vscode:extension/ms-azuretools.vscode-containers) - Container development and management

### Optional (based on project needs)
- [Jupyter](vscode:extension/ms-toolsai.jupyter) - Jupyter notebook support (for data projects)
- [Jupyter Notebook Renderers](vscode:extension/ms-toolsai.jupyter-renderers) - Enhanced Jupyter output
- [Rainbow CSV](vscode:extension/mechatroner.rainbow-csv) - CSV file colorization (for data projects)
- [HashiCorp Terraform](vscode:extension/hashicorp.terraform) - Terraform syntax (for infrastructure projects)
- [SQLTools](vscode:extension/mtxr.sqltools) - SQL database management (for database projects)

**Installation**: Click the links above to install, or run in terminal:
```bash
# Install all essential extensions at once
cursor --install-extension anthropic.claude-code
cursor --install-extension ms-python.python
cursor --install-extension anysphere.cursorpyright
cursor --install-extension ms-python.debugpy
cursor --install-extension davidanson.vscode-markdownlint
cursor --install-extension redhat.vscode-yaml
cursor --install-extension donjayamanne.githistory
cursor --install-extension github.vscode-github-actions
cursor --install-extension github.vscode-pull-request-github
cursor --install-extension ms-azuretools.vscode-docker
cursor --install-extension ms-azuretools.vscode-containers
```

## Additional Resources

- **uv Documentation**: https://github.com/astral-sh/uv
- **Pydantic Settings**: https://docs.pydantic.dev/latest/concepts/pydantic_settings/
- **pytest Documentation**: https://docs.pytest.org/
- **structlog Documentation**: https://www.structlog.org/
- **Docker Documentation**: https://docs.docker.com/
- **GitHub Actions**: https://docs.github.com/en/actions

## For Claude Code / AI Assistants

This template is designed to be AI-assistant friendly:

**Key Information**:
- **Python Version**: 3.12+ (3.13 recommended)
- **Package Manager**: uv (fast, modern)
- **Testing**: pytest with coverage, async support, mocking
- **Code Quality**: ruff (linting + formatting), mypy (type checking)
- **Configuration**: pydantic-settings (type-safe, environment-based)
- **Logging**: structlog (structured, production-ready)
- **Deployment**: Docker-based, flexible target options

**Common Tasks**:
- Add dependency: Edit `pyproject.toml`, run `uv sync`
- Add config: Edit `config.py`, add to `.env.sample` and `.env`
- Add feature: Create module in `src/`, add tests in `tests/`
- Add endpoint: Depends on project type (add CLI, API, etc.)

**Best Practices**:
- Always write tests for new features
- Run `make pre-commit` before committing
- Use type hints for better code quality
- Log important events with structured context
- Document complex logic with docstrings
