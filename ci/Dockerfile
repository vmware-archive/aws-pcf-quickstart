FROM python:3

RUN apt-get update && apt-get install unzip
RUN pip install mock jinja2 awscli
RUN wget https://releases.hashicorp.com/packer/1.0.0/packer_1.0.0_linux_amd64.zip \
        && unzip packer_1.0.0_linux_amd64.zip \
        && rm packer_1.0.0_linux_amd64.zip \
        && chmod +x packer \
        && mv packer /usr/bin
