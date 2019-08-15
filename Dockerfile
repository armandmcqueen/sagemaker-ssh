FROM ubuntu:16.04
# FROM nvidia/cuda:10.0-devel-ubuntu18.04
RUN apt-get update -y
RUN apt-get install -y --no-install-recommends openssh-client openssh-server && \
    mkdir -p /var/run/sshd

RUN mkdir -p /root/.ssh
COPY id_rsa.pub /root/.ssh/authorized_keys

COPY train.sh /usr/bin/train
RUN chmod +x /usr/bin/train
RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd

EXPOSE 1234