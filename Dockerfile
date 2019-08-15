FROM ubuntu:16.04

RUN mkdir -p /root/.ssh
COPY sm_id_rsa.pub /root/.ssh/authorized_keys

COPY train.sh /usr/bin/train
RUN chmod +x /usr/bin/train