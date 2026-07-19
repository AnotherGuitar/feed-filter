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

## NAS Automation (QNAP + Container Station)

feed-filter runs on a schedule from a QNAP NAS (Container Station/Docker)
rather than depending on a laptop being powered on. The pieces:

### Repo location on the NAS

The repo lives at `/share/Container/feed-filter` (the same share Container
Station itself uses, `CACHEDEV1_DATA/Container`). Git isn't available on the
bare QTS host OS, so all git operations (pull/commit/push) happen *inside*
the runner container, not on the host shell.

The real `docker` CLI on QTS isn't on `$PATH` - it lives at:

```
/share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker
```

### Runner image

[Dockerfile.nas](Dockerfile.nas) builds a small `python:3.13-slim` image with
`git` and `uv` added. Unlike the main [Dockerfile](Dockerfile), it does
**not** copy the app source in - the live repo checkout on the NAS share is
bind-mounted at `/repo` when the container runs, so it always executes
whatever's currently on disk with no rebuild step needed after a code change
(just `git pull` on the NAS copy, or re-sync).

Build it (from the NAS, in `/share/Container/feed-filter`):

```bash
DOCKER=/share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker
$DOCKER build -f Dockerfile.nas -t feed-filter-nas:latest .
```

### Runner script

[scripts/update_and_publish_nas.sh](scripts/update_and_publish_nas.sh) is the
NAS-adapted equivalent of
[scripts/update_and_publish.sh](scripts/update_and_publish.sh) (the older
macOS/launchd version - the laptop's launchd job is now unloaded, but the
plist at `~/Library/LaunchAgents/com.feedfilter.updatefeeds.plist` is still
installed as a manual fallback; re-enable with `launchctl load` on that path
if the NAS is ever down). The NAS script:

1. `git pull --rebase origin main` - picks up anything pushed from elsewhere
   first, so it isn't building on a stale base.
2. Runs `feed-filter --config` for every `configs/*.yaml`.
3. Commits and pushes any changed `docs/*.xml`, authenticating with a GitHub
   token (see below) rather than SSH/stored credentials.
4. Pings the WebSub hub for each config once the new content is live.

It intentionally drops macOS-only bits from the original script
(`terminal-notifier`, the hardcoded `/usr/local/bin/uv` path).

Only one machine should be pushing at a time - running both the laptop and
NAS jobs concurrently risks push races (the rebase step resolves most of
them automatically, but not always; this is why the laptop job is disabled
rather than left running alongside the NAS).

### GitHub credential (PAT)

The container needs push access. We use a **fine-grained GitHub personal
access token**, scoped to just this repo:

- Repository access: only `AnotherGuitar/feed-filter`
- Permissions: **Contents: Read and write** (nothing else)
- Created: 2026-07-18, 90-day expiration (~2026-10-16) - regenerate before
  then via github.com/settings/personal-access-tokens, same scope, and
  overwrite the file below.

The token is **never stored in the repo or committed** - it lives outside the
git working tree entirely, in a restricted-permission env file on the NAS:

```
/share/Container/feed-filter-secrets/github_token.env   (mode 600)
```

containing a single line:

```
GITHUB_TOKEN=github_pat_...
```

The runner script reads it as an environment variable at push time
(`https://x-access-token:${GITHUB_TOKEN}@github.com/...`) - it's never
written into `.git/config` or any file inside the repo itself.

### Scheduling: a self-contained cron container

QNAP's Task Scheduler UI wasn't present in Control Panel on this NAS/QTS
build, and editing the system crontab (`/etc/config/crontab`) directly
requires root - `karate` is in the `administrators` group but that only
grants read access to that file (owner `admin`, uid 0), and `sudo` needs an
interactive password we don't want to script around.

Instead, the container runs its own scheduler and stays up permanently:

- [scripts/nas-crontab](scripts/nas-crontab) - a standard crontab file, read
  by [supercronic](https://github.com/aptible/supercronic) (a static,
  dependency-free cron replacement built for containers - Debian's `cron`
  package pulls in `systemd`, whose postinst script fails when it isn't
  PID 1). Currently: `0 2,8,14,20 * * *`, matching the old launchd cadence.
- [scripts/nas-entrypoint.sh](scripts/nas-entrypoint.sh) - the image's `CMD`,
  just execs `supercronic` against that crontab file.
- supercronic forwards its own process environment (set via `docker run
  --env-file`, i.e. `GITHUB_TOKEN`) to every job it runs, so no secret ever
  needs to be written into a file inside the container or the repo.

Start it once (survives NAS reboots via `--restart unless-stopped`, since
Container Station's Docker daemon itself starts on boot):

```bash
DOCKER=/share/CACHEDEV1_DATA/.qpkg/container-station/bin/docker
$DOCKER run -d --name feed-filter-scheduler --restart unless-stopped \
  --env-file /share/Container/feed-filter-secrets/github_token.env \
  -v /share/Container/feed-filter:/repo \
  feed-filter-nas:latest
```

Check on it:

```bash
$DOCKER logs feed-filter-scheduler       # supercronic startup + job output
$DOCKER ps --filter name=feed-filter-scheduler
```

To change the schedule: edit `scripts/nas-crontab`, `git pull` (or re-sync)
on the NAS, then `docker restart feed-filter-scheduler` - no image rebuild
needed, since the crontab file is bind-mounted along with the rest of the
repo. A rebuild (`docker build -f Dockerfile.nas ...`) is only needed after
changing `Dockerfile.nas` itself (e.g. bumping the supercronic version).

### SSH access to the NAS

Passwordless SSH key auth is set up for the `karate` account (a member of
the `administrators` group), from the Mac's `~/.ssh/id_ed25519_nasa` key,
targeting `nasa.local`. The built-in `admin` account's password was lost at
setup time; `karate` was used instead since it already had admin-group
membership.

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
