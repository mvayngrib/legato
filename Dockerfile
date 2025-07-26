# syntax=docker/dockerfile:1.3
FROM nvidia/cuda:12.1.0-base-ubuntu22.04 

# Install Python + deps
RUN apt-get update && apt-get install -y python3-pip python-is-python3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# CUDA compat (if needed)
RUN ldconfig /usr/local/cuda-12.1/compat/

# Install Python libs
RUN --mount=type=cache,target=/root/.cache/pip \
    python3 -m pip install --upgrade pip && \
    python3 -m pip install --upgrade runpod~=1.7.7 \
      torch==2.6.0 --extra-index-url https://download.pytorch.org/whl/cu121 \
      transformers==4.50.0 \
      datasets==2.18.0 \
      pillow==11.1.0 \
      tqdm \
      hf-transfer \
      huggingface-hub \
      pyparsing==3.1.1 \
      typing-extensions>=4.8.0 \
      packaging \
      requests>=2.32.2

WORKDIR /legato
COPY . /legato
ENV PYTHONPATH="/legato"
ARG HF_TOKEN
RUN --mount=type=secret,id=hf_token \
    HUGGINGFACE_TOKEN=$(cat /run/secrets/hf_token) && \
    python3 -c "from legato.models import LegatoModel; LegatoModel.from_pretrained('guangyangmusic/legato', token='$HUGGINGFACE_TOKEN')"

ENV HF_HUB_OFFLINE=1

CMD ["python3", "/legato/scripts/runpod_handler.py"]
