import boto3
import json
from invoke import task
import tabulate



def filter_by_sgs(network_interfaces, sg_ids):
    "Return the network interfaces that have all sg_ids present. This is the security groups given to the training job"
    def sg_match(network_interface):
        group_ids = [sg["GroupId"] for sg in network_interface["Groups"]]
        for sg in sg_ids:
            if sg not in group_ids:
                return False
        return True

    matching_network_interfaces = [n for n in network_interfaces if sg_match(n)]
    return matching_network_interfaces

def get_network_inferfaces(subnet):
    client = boto3.client('ec2')
    response = client.describe_network_interfaces(
            Filters=[
                {
                    'Name': 'subnet-id',
                    'Values': [subnet]
                },
            ]
    )
    return response["NetworkInterfaces"]
    # print(json.dumps(response, indent=4))

def filter_by_device_id(network_interfaces, device_id):
    def device_index_match(network_interface):
        return network_interface["Attachment"]["DeviceIndex"] == device_id

    matching_network_interfaces = [n for n in network_interfaces if device_index_match(n)]
    return matching_network_interfaces


def filter_by_ssh_connectivity(network_interfaces, c, port=22, verbose=False):
    if verbose:
        print("Filtering by ssh connections now")

    def ssh_succeeds(network_interface):
        ip = network_interface["PrivateIpAddress"]
        if verbose:
            print(f'\nAttempting to ssh to {ip}')
        try:
            hide = not verbose
            c.run(f'ssh -o StrictHostKeyChecking=no -p {port} root@{ip} cat /opt/ml/input/config/resourceconfig.json', hide=hide)
            if verbose:
                print("\nSucceeded")
        except Exception as e:
            if verbose:
                print("Failed")
            return False
            # print(type(e))
            # print(e)
        return True

    matching_network_interfaces = [n for n in network_interfaces if ssh_succeeds(n)]
    return matching_network_interfaces


def display_network_interfaces(network_interfaces):
    for n in network_interfaces:
        device_index = n["Attachment"]["DeviceIndex"]
        status = n["Status"]
        sg_names = [sg["GroupName"] for sg in n["Groups"]]
        private_ip = n["PrivateIpAddress"]
        id = n["NetworkInterfaceId"]
        print(id, device_index, status, private_ip, sg_names)


    
def extract_ips(network_interfaces):
    return [n["PrivateIpAddress"] for n in network_interfaces]


def describe_instance(c, ip):
    # print(ip)
    resourceconfig = json.loads(c.run(f'ssh -o StrictHostKeyChecking=no -p 1234 root@{ip} cat /opt/ml/input/config/resourceconfig.json', hide=True).stdout)
    current_host = resourceconfig["current_host"]
    all_hosts = resourceconfig["hosts"]

    hyperparams = json.loads(c.run(f'ssh -o StrictHostKeyChecking=no -p 1234 root@{ip} cat /opt/ml/input/config/hyperparameters.json', hide=True).stdout)
    job_name = hyperparams["sagemaker_job_name"] if "sagemaker_job_name" in hyperparams.keys() else "Unknown Job Name"

    # print(resourceconfig)
    # print(hyperparams)
    return job_name, current_host, all_hosts, ip

    

@task()
def smssh(c, subnet, security_groups="", port=22, verbose=False):
    # subnet = "subnet-21ac2f2e"
    # security_groups = ["sg-0eaeb8cc84c955b74",
    #                    "sg-0043f63c9ad9ffc1d",
    #                    "sg-0d931ecdaccd26af3"]
    security_groups = security_groups.split(",")
    network_interfaces = get_network_inferfaces(subnet)
    network_interfaces = filter_by_sgs(network_interfaces, security_groups)
    # network_interfaces = filter_by_device_id(network_interfaces, 2)
    network_interfaces = filter_by_ssh_connectivity(network_interfaces, c, port=port, verbose=verbose)
    if verbose:
        print("Matching network interfaces:")
        display_network_interfaces(network_interfaces)

    ips = extract_ips(network_interfaces)
    rows = []
    for ip in ips:
        if verbose:
            print(f'Trying ssh to {ip}')
        description_array = describe_instance(c, ip)
        rows.append(description_array)
        if verbose:
            print("")

    rows = sorted(rows, key=lambda r: (r[0], r[1]))
    header = ["Job Name", "Host Id", "Hosts in Training Job", "IP"]
    print(tabulate.tabulate(rows, headers=header))

        # try:
        #     c.run(f'ssh -p 1234 root@{ip} cat /opt/ml/input/config/resourceconfig.json')
        # except Exception as e:
        #     print("Error", e)