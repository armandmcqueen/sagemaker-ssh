FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y --no-install-recommends openssh-client openssh-server && \
    mkdir -p /var/run/sshd && \
    mkdir -p /root/.ssh

COPY id_rsa.pub /root/.ssh/authorized_keys

COPY train_entrypoint.sh /usr/bin/train
RUN chmod +x /usr/bin/train

EXPOSE 22