# Identifying the SageMaker IPs

You can connect to SageMaker containers via a private IP address in the subnet that the training job is launched in.

Finding these IPs among the various network interfaces in the subnet is difficult. This tool helps to identify the correct IPs.

### Invoke

This uses the [`invoke`](http://docs.pyinvoke.org/en/1.3/index.html) library to run:





```
> invoke --help find-sm-ssh-ips
```
```
> invoke find-sm-ssh-ips --subnet=subnet-21ac2f2e --security-groups=sg-0eaeb8cc84c955b74

Job Name                             Host Id    Hosts in Training Job    IP
-----------------------------------  ---------  -----------------------  -------------
armand-ssh-test-2019-08-15T02-54-08  algo-1     ['algo-1', 'algo-2']     172.31.72.31
armand-ssh-test-2019-08-15T02-54-08  algo-2     ['algo-1', 'algo-2']     172.31.64.170


```

