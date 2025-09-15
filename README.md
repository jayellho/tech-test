# HTX Technical Test


## Get started
1. Single VM deployment
2. Scalable deployment




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
