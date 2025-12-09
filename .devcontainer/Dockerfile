FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

RUN apt-get update && \
    apt-get install -y \
    git curl wget locales build-essential libgl1 && \
    locale-gen en_US.UTF-8 && \
    locale-gen mi_NZ.UTF-8

ENV LANG=mi_NZ.UTF-8
ENV LC_ALL=mi_NZ.UTF-8

WORKDIR /workspaces/The_Awa_Network
