#!/usr/bin/env bash

echo "Starting ssh daemon"
/usr/sbin/sshd -p 22; sleep infinity
echo "Done with ssh daemon"