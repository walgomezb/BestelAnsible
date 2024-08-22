import ansible_runner
import json
import os
import yaml


def run_playbook(playbook_path, target_host, username, password):
    # Create a dynamic inventory
    dynamic_inventory = {
        "all": {
            "hosts": {
                "cisco_router": {
                    "ansible_host": target_host,
                    # "ansible_network_os": "cisco.ios.ios",
                    "ansible_user": username,
                    "ansible_password": password,
                    # "ansible_ssh_pass": password,
                    "ansible_connection": "network_cli",
                    "ansible_network_os": "ios",
                    "ansible_ssh_common_args": '-o StrictHostKeyChecking=no -o KexAlgorithms=diffie-hellman-group-exchange-sha1 -o HostKeyAlgorithms=ssh-rsa -o ProxyCommand="sshpass -p C1sco12345 ssh -vvv -o StrictHostKeyChecking=no -W %h:%p -q developer@10.10.20.50"',
                }
            }
        }
    }

    # Write the inventory to a temporary file
    inventory_path = "dynamic_inventory.json"
    with open(inventory_path, "w") as inventory_file:
        json.dump(dynamic_inventory, inventory_file)

    # Run the playbook using ansible-runner
    r = ansible_runner.run(
        private_data_dir=".",
        playbook=playbook_path,
        inventory=dynamic_inventory,
       
        verbosity=3,
    )

    # Clean up the temporary inventory file
    # os.remove(inventory_path)

    # Print the results
    print(f"Status: {r.status}")
    print(f"RC: {r.rc}")
    for event in r.events:
        print(event["event"])


if __name__ == "__main__":
    playbook_path = "get_voice_port_details.yml"
    target_host = "201.148.0.101"
    username = "z3qu3nC@ct1"
    password = "Onbo@rd1NG#0ToUcH2024"
    target_host = "10.10.20.181"
    username = "cisco"
    password = "cisco"
    run_playbook(playbook_path, target_host, username, password)
