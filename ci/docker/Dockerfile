FROM python:3

RUN apt-get update && apt-get install unzip
RUN pip install mock jinja2 boto3
RUN wget https://releases.hashicorp.com/packer/1.0.0/packer_1.0.0_linux_amd64.zip \
        && unzip packer_1.0.0_linux_amd64.zip \
        && rm packer_1.0.0_linux_amd64.zip \
        && chmod +x packer \
        && mv packer /usr/bin

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

# Cleanup
RUN rm -rf /tmp/docker-build
