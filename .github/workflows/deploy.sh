#!/bin/bash

# Exit on any error
set -ex

# for staging
# GIT_BRANCH="${GITHUB_REF##refs/heads/}"
# if [ "$GIT_BRANCH" == "main" ]; then

GIT_TAG="${GITHUB_REF##refs/tags/}"
if [[ $GITHUB_REF != $GIT_TAG ]]; then
# Configure SSH
mkdir ~/.ssh
echo -e "Host *\n\tStrictHostKeyChecking no\n" >> ~/.ssh/config
echo "$SSH_PRIVATE_KEY_PROD" > ~/.ssh/id_rsa
chmod 700 ~/.ssh/id_rsa

# Deploy code
rsync -avhz --delete --filter=":- .gitignore" --exclude=.git --exclude=.github . root@$SSH_PROD_DOMAIN:/root/sport-life-community

# Run
ssh root@$SSH_PROD_DOMAIN "docker compose --project-directory ./sport-life-community build"
ssh root@$SSH_PROD_DOMAIN "docker compose --project-directory ./sport-life-community stop"
ssh root@$SSH_PROD_DOMAIN "docker compose --project-directory ./sport-life-community up -d"
# ssh root@$SSH_PROD_DOMAIN "docker system prune -a -f"
fi
