# SSHing into SageMaker training jobs

1. Create keypair so that your ec2 instance can SSH int o the SageMaker container.
2. Put public key in container. Make private key available to ssh on ec2 instance.
3. Add a training job entrypoint into container that launches ssh daemon and waits.
4. Launch training job with a subnet specified

Now when the SageMaker instances are spun up, each container will have a visible network interface.  

 