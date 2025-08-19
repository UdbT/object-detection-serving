ARG PYTHON_VERSION="3.12"

FROM python:${PYTHON_VERSION}-slim-bookworm AS builder
ARG PYTHON_VERSION
ARG POETRY_VERSION="1.8.3"

RUN apt-get update \
    && apt-get install --no-install-recommends --yes \
    build-essential \
    ffmpeg \
    && pip install poetry==${POETRY_VERSION} poetry-dynamic-versioning \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root

COPY poetry.lock pyproject.toml ./

RUN pip install --upgrade pip==24.* setuptools==70.* wheel==0.43.* && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --without dev --no-cache && \
    poetry run pip cache purge && \
    rm -rf ~/.cache/pypoetry/artifacts

FROM python:${PYTHON_VERSION}-slim-bookworm AS prod
ARG PYTHON_VERSION
WORKDIR /root

# Install curl for internal healthcheck
RUN apt-get update \
    && apt-get install --no-install-recommends --yes \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Only copy necessary files from builder
COPY --from=builder /usr/local/lib/python${PYTHON_VERSION}/site-packages /usr/local/lib/python${PYTHON_VERSION}/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# gRPC server
COPY main.py .
COPY src ./src
COPY configs ./configs
COPY resources ./resources

EXPOSE 50051
CMD ["python", "-m", "main"]
