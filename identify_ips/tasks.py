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
            c.run(f'ssh -o StrictHostKeyChecking=no -o ConnectTimeout=2 -p {port} root@{ip} hostname', hide=hide)
            if verbose:
                print("Succeeded")
        except Exception as e:
            if verbose:
                print("Failed")
            return False
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


def describe_instance(c, ip, port):

    resourceconfig = json.loads(c.run(f'ssh -o StrictHostKeyChecking=no -p {port} root@{ip} cat /opt/ml/input/config/resourceconfig.json', hide=True).stdout)
    current_host = resourceconfig["current_host"]
    all_hosts = resourceconfig["hosts"]

    hyperparams = json.loads(c.run(f'ssh -o StrictHostKeyChecking=no -p {port} root@{ip} cat /opt/ml/input/config/hyperparameters.json', hide=True).stdout)
    job_name = hyperparams["sagemaker_job_name"] if "sagemaker_job_name" in hyperparams.keys() else "Unknown Job Name"

    return job_name, current_host, all_hosts, ip

    

@task(help={'subnet': "The subnet where the SageMaker job is running, e.g. 'sg-1234567890'.",
            'security-groups': "The security groups attached to the SageMaker training job. A comma separated list, e.g. 'sg-123456,sg-234567'.",
            'port': "The port that the ssh daemon is running on. Default is 22.",
            'verbose': "Get detailed information about what is running. Very verbose."})
def find_sm_ssh_ips(c, subnet, security_groups="", port=22, verbose=False):
    security_groups = security_groups.split(",")
    network_interfaces = get_network_inferfaces(subnet)
    network_interfaces = filter_by_sgs(network_interfaces, security_groups)
    network_interfaces = filter_by_device_id(network_interfaces, 2)
    network_interfaces = filter_by_ssh_connectivity(network_interfaces, c, port=port, verbose=verbose)
    if verbose:
        print("\nMatching network interfaces:")
        display_network_interfaces(network_interfaces)

    ips = extract_ips(network_interfaces)
    rows = []
    if verbose:
        print("")
    for ip in ips:
        if verbose:
            print(f'Retrieving details from {ip}')
        description_array = describe_instance(c, ip, port=port)
        rows.append(description_array)

    rows = sorted(rows, key=lambda r: (r[0], r[1]))
    header = ["Job Name", "Host Id", "Hosts in Training Job", "IP"]
    print("")
    print(tabulate.tabulate(rows, headers=header))
