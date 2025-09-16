# HTX Technical Test

### Deployment specifics
1. Public IP: `13.212.109.178`
2. Search UI: `http://13.212.109.178:3000`
3. ASR API: `http://13.212.109.178:8001`
4. Elasticsearch: `http://13.212.109.178:9200`

### What to run
Assumption: Instructions below assume that service endpoints are running on AWS and transcription and indexing has not been done. In reality, transcription and indexing has already been done (so you can skip steps 3 and 4).

1. Clone repository,download common voice dataset and create `.env`.
```bash
# Clone repository
git clone https://github.com/jayellho/tech-test.git
cd tech-test

# Download dataset
wget "https://www.dropbox.com/scl/fi/i9yvfqpf7p8uye5o8k1sj/common_voice.zip?rlkey=lz3dtjuhekc3xw4jnoeoqy5yu&dl=1" -O common_voice.zip
unzip common_voice.zip

# Rename .env_default
mv .env_default .env
```

2. (Optional) Set environment variables - if not done, just replace the variables below with the raw values here.
```bash
export INPUT_CSV_PATH=./common_voice/cv-valid-dev.csv
export OUTPUT_CSV_PATH=./common_voice/cv-valid-dev-with-gen.csv
export INPUT_AUDIO_PATH=./common_voice/cv-valid-dev
export DEPLOYMENT_URL=13.212.109.178
```
   
3. Transcribe audio and populate `cv-valid-dev-with-gen.csv`.
```bash
cd asr
pip install -r requirements.txt
python cv-decode.py   --csv $INPUT_CSV_PATH   --audio_dir $INPUT_AUDIO_PATH   --api http://$DEPLOYMENT_URL:8001/asr   --out_csv $OUTPUT_CSV_PATH
```
4. Build index
```bash
cd elastic-backend
python cv-index.py --csv $OUTPUT_CSV_PATH --es http://$DEPLOYMENT_URL:9200 --index cv-transcriptions
```

## AWS Deployment - just for reference.
### Install Docker
1. Install Docker with a convenience script.
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

2. Allow running Docker without `sudo`.
```bash
sudo systemctl enable --now docker
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
docker context use default
docker run --rm hello-world # test if successfully set-up.
```
