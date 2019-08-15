#!/usr/bin/env bash

docker run --network=host -v /mnt/share/ssh:/root/.ssh -it armandmcqueen/sagemaker-ssh:latest /bin/bash
