FROM python:3

RUN apt-get update && apt-get install unzip wget

# Set starkandwayne repo and install bosh
RUN wget -q -O - https://raw.githubusercontent.com/starkandwayne/homebrew-cf/master/public.key | apt-key add - && \
    echo "deb http://apt.starkandwayne.com stable main" | tee /etc/apt/sources.list.d/starkandwayne.list && \
    apt-get -y -qq update && \
    apt-get -y -qq install bosh-cli jq

# packer
RUN pip install mock jinja2 boto3
RUN wget https://releases.hashicorp.com/packer/1.0.0/packer_1.0.0_linux_amd64.zip \
        && unzip packer_1.0.0_linux_amd64.zip \
        && rm packer_1.0.0_linux_amd64.zip \
        && chmod +x packer \
        && mv packer /usr/bin

# Golang
ENV GO_VERSION=1.12.1
ENV GO_SHA256SUM=2a3fdabf665496a0db5f41ec6af7a9b15a49fbe71a85a50ca38b1f13a103aeec

RUN curl -LO https://storage.googleapis.com/golang/go${GO_VERSION}.linux-amd64.tar.gz && \
    echo "${GO_SHA256SUM}  go${GO_VERSION}.linux-amd64.tar.gz" > go_${GO_VERSION}_SHA256SUM && \
    sha256sum -cw --status go_${GO_VERSION}_SHA256SUM
RUN tar -C /usr/local -xzf go${GO_VERSION}.linux-amd64.tar.gz
ENV GOPATH /root/go
RUN mkdir -p /root/go/bin
ENV PATH $PATH:/usr/local/go/bin:$GOPATH/bin
RUN go get github.com/onsi/ginkgo
RUN go install github.com/onsi/ginkgo/...
RUN go get -u golang.org/x/lint/golint

# install tile-config-generator
ENV TCG_VERSION=v0.0.16
ENV TCG_SHA256SUM=327013f3fde4ac77cfa2e2c2ba2cd3addb736c279c3caa73091004750b134af5

RUN wget https://github.com/pivotalservices/tile-config-generator/releases/download/${TCG_VERSION}/tile-config-generator-linux \
  -O tile-config-generator && \
  echo "${TCG_SHA256SUM}  tile-config-generator" > tcg_SHA256SUM && \
  sha256sum -cw --status tcg_SHA256SUM && \
  mv tile-config-generator /usr/local/bin && \
  chmod a+x /usr/local/bin/tile-config-generator

# Cleanup
RUN rm -rf /tmp/docker-build
