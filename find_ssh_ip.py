import boto3
import json
import subprocess

def sh(cmd):
    return subprocess.check_output(cmd, shell=True)


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


def display_network_interfaces(network_interfaces):
    for n in network_interfaces:
        device_index = n["Attachment"]["DeviceIndex"]
        status = n["Status"]
        sg_names = [sg["GroupName"] for sg in n["Groups"]]
        private_ip = n["PrivateIpAddress"]
        id = n["NetworkInterfaceId"]
        print(id, device_index, status, private_ip, sg_names)

def attempt_ssh(ip):
    sh(f'ssh root@{ip} cat /opt/ml/input/config/resourceconfig.json')
    
def extract_ips(network_interfaces):
    return [n["PrivateIpAddress"] for n in network_interfaces]


if __name__ == '__main__':
    subnet = "subnet-21ac2f2e"
    security_groups = ["sg-0eaeb8cc84c955b74",
                       "sg-0043f63c9ad9ffc1d",
                       "sg-0d931ecdaccd26af3"]
    network_interfaces = get_network_inferfaces(subnet)
    network_interfaces = filter_by_sgs(network_interfaces, security_groups)
    network_interfaces = filter_by_device_id(network_interfaces, 2)
    display_network_interfaces(network_interfaces)
    
    ips = extract_ips(network_interfaces)
    for ip in ips:
        print(f'Trying ssh to {ip}')
        attempt_ssh(ip)
    
    