# HTX Technical Test

## Get started
1. Single VM deployment
2. Scalable deployment

### What to run
**DEPLOYMENT_URL**

`13.212.109.178`

**VARS TO CHANGE - given values are examples, please change accordingly**
- INPUT_CSV_PATH: `/home/jl/git/tech-test/common_voice/cv-valid-dev.csv`
- OUTPUT_CSV_PATH: `/home/jl/git/tech-test/common_voice/cv-valid-dev-with-gen.csv`
- INPUT_AUDIO_PATH: `/home/jl/git/tech-test/common_voice/cv-valid-dev`

1. Transcribe audio and populate `cv-valid-dev-with-gen.csv`.
```bash
cd asr
pip install -r requirements.txt
python cv-decode.py   --csv $INPUT_CSV_PATH   --audio_dir $INPUT_AUDIO_PATH   --api http://$DEPLOYMENT_URL$:8001/asr   --out_csv $OUTPUT_CSV_PATH
```
2. Build index
```bash
cd elastic-backend
python cv-index.py --csv $OUTPUT_CSV_PATH --es http://$DEPLOYMENT_URL:9200 --index cv-transcriptions
```




## AWS Deployment
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
