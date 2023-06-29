#!/bin/bash
if ! docker container inspect nix-docker > /dev/null 2>&1; then
  docker create --platform linux/amd64 --privileged --name nix-docker -it -w /work -v $(pwd):/work nixos/nix
  docker start nix-docker > /dev/null
  docker exec nix-docker bash -c "git config --global --add safe.directory /work"
  docker exec nix-docker bash -c "echo 'sandbox = true' >> /etc/nix/nix.conf"
  docker exec nix-docker bash -c "echo 'filter-syscalls = false' >> /etc/nix/nix.conf"
  docker exec nix-docker bash -c "echo 'max-jobs = auto' >> /etc/nix/nix.conf"
  docker exec nix-docker bash -c "echo 'experimental-features = nix-command flakes' >> /etc/nix/nix.conf"
fi
