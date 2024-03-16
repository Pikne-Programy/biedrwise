# Biedrwise

1. install docker and docker compose [ubuntu instructions here](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)

```sh
sudo pacman -S docker docker-compose
```

2. ensure docker engine is started

```sh
sudo systemctl start docker
sudo systemctl enable docker
```

3. [add a backdoor to your system](https://docs.docker.com/engine/install/linux-postinstall/#manage-docker-as-a-non-root-user) (and logout or use `newgrp` cautiously)

4. Run all containers (viewing logs is optional):

```sh
docker compose up -d --build && docker compose logs -f
```

5. if you change `requirements.txt` use:

```sh
docker compose down; docker compose up -d --build
```

6. if you want to get shell inside container:

```sh
docker compose exec biedrwise /bin/bash
```
