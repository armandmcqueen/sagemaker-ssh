# sagemaker-ssh

## Generate ssh creds

`
ssh-keygen -q -t rsa -N '' -f id_rsa
`

Creates 

```
- id_rsa
- id_rsa.pub
```

### In container

Put `id_rsa.pub` into container as `/root/.ssh/authorized_keys`

### In ec2 instance

Put `id_rsa` into `~/.ssh/id_rsa`

## Finding 


