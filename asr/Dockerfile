# asr/Dockerfile
FROM python:3.12-slim

# install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsndfile1 \
 && rm -rf /var/lib/apt/lists/*

# set working directory
WORKDIR /app


COPY requirements.txt /app/requirements.txt

# install packages.
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy in 'asr' folder into container at /app
COPY asr/ /app/

EXPOSE 8001

CMD ["uvicorn", "asr_api:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]