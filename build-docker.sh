#!/bin/bash

docker start nix-docker > /dev/null # start nix-docker container if not already running
docker exec -it nix-docker nix build -L .#docker
docker exec -it nix-docker cp -L ./result ./result.tar.gz # copy artifacts to the host system
mv result.tar.gz result
