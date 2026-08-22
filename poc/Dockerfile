FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml README.md ./
COPY prism ./prism
RUN pip install --no-cache-dir .

# templates はイメージに同梱(実行時に volume で上書き可能)
COPY templates ./templates

# 実行時の可変データは volume 前提(docker-compose.yml 参照)
ENV PRISM_ROOT=/work
WORKDIR /work
ENTRYPOINT ["prism"]
CMD ["--help"]
