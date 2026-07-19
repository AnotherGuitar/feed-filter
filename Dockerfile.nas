# Runner image for the NAS scheduled job (see scripts/update_and_publish_nas.sh
# and README.md "NAS automation" section). Unlike the main Dockerfile, this
# image does NOT copy the app source in - the live repo directory on the NAS
# share is bind-mounted at /repo at `docker run` time, so it always runs
# whatever's currently checked out there without needing an image rebuild.
FROM python:3.13-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

WORKDIR /repo

CMD ["bash", "scripts/update_and_publish_nas.sh"]
