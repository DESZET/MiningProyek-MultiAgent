# HF Spaces standard Dockerfile pattern (CPU only — install torch CPU explicitly)
# Reference: https://huggingface.co/docs/hub/spaces-sdks-docker

FROM python:3.11

WORKDIR /code

# Install torch CPU FIRST (avoid pulling CUDA libs we won't use)
RUN pip install --no-cache-dir torch==2.4.1 --index-url https://download.pytorch.org/whl/cpu

# Install other deps
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Set up the standard "user" with UID 1000 — required by HF Spaces
RUN useradd -m -u 1000 user
USER user

ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

COPY --chown=user . $HOME/app

# HF Spaces expects port 7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
