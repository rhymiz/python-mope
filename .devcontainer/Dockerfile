# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.238.1/containers/python-3/.devcontainer/base.Dockerfile

ARG VARIANT=“3.7-bullseye”
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}
ARG NODE_VERSION="none"
RUN if [ "${NODE_VERSION}" != "none" ]; then su vscode -c "umask 0002 && . /usr/local/share/nvm/nvm.sh && nvm install ${NODE_VERSION} 2>&1"; fi
ENV PYTHONOPTIMIZE 1
ENV PYTHONUNBUFFERED TRUE
RUN apt-get update && apt-get install gnupg2 -y