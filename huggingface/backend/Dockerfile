# HF Space (Docker) for the Asahlagi FastAPI backend.
#
# Builds by cloning the backend from the public GitHub repo so the code is not
# duplicated in the Space. To deploy the latest commit, trigger a
# "Factory rebuild" on the Space (it ignores the layer cache and re-clones).
#
# Secrets (DATABASE_URL, HF_SPACE_URL, CORS_ALLOWED_ORIGINS) are provided as
# HF Space secrets at runtime, NOT baked into the image. The repo has no .env
# (gitignored), so cloning never exposes credentials.

FROM python:3.12-slim

# git for cloning the repo
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Cache-bust: bump this value (or use Factory rebuild) to force a fresh clone.
ARG CACHEBUST=2026-05-25

RUN git clone --depth 1 https://github.com/ravi-arnan/TempaCapstoneProject.git /tmp/repo \
    && cp -r /tmp/repo/backend /code \
    && rm -rf /tmp/repo

WORKDIR /code
RUN pip install --no-cache-dir -r requirements.txt

# HF Spaces standard user (UID 1000)
RUN useradd -m -u 1000 user && chown -R user /code
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# HF Spaces expects the app on port 7860
EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]
