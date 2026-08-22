FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml ./
COPY prism ./prism
RUN pip install --no-cache-dir .

# templates はイメージに同梱(実行時に volume で上書き可能)
COPY templates ./templates

# 実行時の可変データは volume 前提(docker-compose.yml 参照)。
# compose を使わない素の `docker run` でもテンプレートが見つかるよう既定を焼き込む
ENV PRISM_ROOT=/work
ENV PRISM_TEMPLATES_DIR=/app/templates
WORKDIR /work
ENTRYPOINT ["prism"]
CMD ["--help"]
