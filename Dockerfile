FROM nvidia/cuda:10.0-devel-ubuntu18.04

RUN mkdir -p /root/.ssh
COPY id_rsa.pub /root/.ssh/authorized_keys

COPY train.sh /usr/bin/train
RUN chmod +x /usr/bin/train