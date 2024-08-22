from flask import Flask, request, jsonify
import ansible_runner
import yaml
import os,json
import re


app = Flask(__name__)


@app.route("/run_playbook", methods=["POST"])
def run_playbook():
    data = request.json
    target_ip = data.get("target_ip")
    target_ip = data.get("target_ip")
    username = data.get("username")
    password = data.get("password")

    if not target_ip or not username or not password:
        return jsonify({"error": "target_ip, username, and password are required"}), 400

    # Define the dynamic inventory as a dictionary
    dynamic_inventory = {
        "all": {
            "hosts": {
                "cisco_router": {
                    "ansible_host": target_ip,
                    # "ansible_network_os": "cisco.ios.ios",
                    "ansible_user": username,
                    "ansible_password": password,
                    # "ansible_ssh_pass": password,
                    "ansible_connection": "network_cli",
                    "ansible_network_os": "ios",
                    #parametros para usar un JumpBox
                    #"ansible_ssh_common_args": '-o StrictHostKeyChecking=no -o KexAlgorithms=diffie-hellman-group-exchange-sha1 -o HostKeyAlgorithms=ssh-rsa -o ProxyCommand="sshpass -p C1sco12345 ssh -o StrictHostKeyChecking=no -W %h:%p -q developer@10.10.20.50"',
                    "ansible_ssh_common_args": '-o StrictHostKeyChecking=no -o KexAlgorithms=diffie-hellman-group-exchange-sha1 -o HostKeyAlgorithms=ssh-rsa',
                }
            }
        }
    }

    # Path to the playbook file
    playbook_path = "get_voice_port_details.yml"

    # Example playbook content to get the running config from a specific Cisco IOS router
    playbook_content = [
        {
            "name": "Get running config from Cisco IOS router",
            "hosts": "cisco_router",
            "gather_facts": "no",
            "tasks": [
                {
                    "name": "Get running config",
                    "cisco.ios.ios_command": {"commands": ["show running-config"]},
                    "register": "running_config",
                },
                {
                    "name": "Print running config",
                    "debug": {"msg": "{{ running_config.stdout[0] }}"},
                },
            ],
        }
    ]

    # Write the inventory to a temporary file
    inventory_path = "dynamic_inventory.json"
    with open(inventory_path, "w") as inventory_file:
        json.dump(dynamic_inventory, inventory_file)

    # Run the playbook using ansible-runner
    runner = ansible_runner.run(
        private_data_dir=".",
        playbook=playbook_path,
        inventory=dynamic_inventory,
        verbosity=3,
    )

    # Collect the results
    interface_configs = None
    for event in runner.events:
        if "event_data" in event and "res" in event["event_data"]:
            if "msg" in event["event_data"]["res"]:
                interface_configs = event["event_data"]["res"]["msg"]
                break

    if interface_configs is None:
        return jsonify({"error": "Failed to retrieve interface configurations"}), 500

    # Filter Loopback interfaces
    loopback_interfaces = {}
    interfaces = interface_configs.split("interface ")
    for interface in interfaces:
        if interface.startswith("Loopback"):
            interface_name = re.search(r"Loopback[0-9]+", interface).group(0)
            loopback_interfaces[interface_name] = "interface " + interface.strip()

    return jsonify(loopback_interfaces)


@app.route("/get_voice_ports", methods=["POST"])
def get_voice_ports():
    data = request.json
    target_ip = data.get("target_ip")
    username = data.get("username")
    password = data.get("password")

    if not target_ip or not username or not password:
        return jsonify({"error": "target_ip, username, and password are required"}), 400

    # Define the dynamic inventory as a dictionary
    dynamic_inventory = {
        "all": {
            "hosts": {
                "cisco_router": {
                    "ansible_host": target_ip,
                    # "ansible_network_os": "cisco.ios.ios",
                    "ansible_user": username,
                    "ansible_password": password,
                    # "ansible_ssh_pass": password,
                    "ansible_connection": "network_cli",
                    "ansible_network_os": "ios",
                    # parametros para usar un JumpBox
                    # "ansible_ssh_common_args": '-o StrictHostKeyChecking=no -o KexAlgorithms=diffie-hellman-group-exchange-sha1 -o HostKeyAlgorithms=ssh-rsa -o ProxyCommand="sshpass -p C1sco12345 ssh -o StrictHostKeyChecking=no -W %h:%p -q developer@10.10.20.50"',
                    "ansible_ssh_common_args": "-o StrictHostKeyChecking=no -o KexAlgorithms=diffie-hellman-group-exchange-sha1 -o HostKeyAlgorithms=ssh-rsa",
                }
            }
        }
    }

    # Path to the playbook file
    playbook_path = "get_voice_port_details.yml"

    # Example playbook content to get the voice-port config from a specific Cisco IOS router
    # Example playbook content to get the voice-port config from a specific Cisco IOS router
    playbook_content = [
        {
            "name": "Get voice-port config from Cisco IOS router",
            "hosts": "cisco_router",
            "gather_facts": "no",
            "tasks": [
                {
                    "name": "Get voice_port_configs",
                    "cisco.ios.ios_command": {
                        "commands": ["show running-config | section voice-port"]
                    },
                    "register": "voice_port_configs",
                },
                {
                    "name": "Get voice_port_summary",
                    "cisco.ios.ios_command": {"commands": ["show voice port sum"]},
                    "register": "voice_port_summary",
                },
                {
                    "name": "Print voice_port_configs",
                    "debug": {"msg": "{{ voice_port_configs.stdout[0] }}"},
                },
                {
                    "name": "Print voice_port_summary",
                    "debug": {"msg": "{{ voice_port_summary.stdout[0] }}"},
                },
            ],
        }
    ]

    # Write the playbook content to the specified file
    with open(playbook_path, "w") as playbook_file:
        yaml.dump(playbook_content, playbook_file)

    # Run the playbook using ansible-runner
    runner = ansible_runner.run(
        private_data_dir=".",
        playbook=playbook_path,
        inventory=dynamic_inventory,
        verbosity=3,
    )

    # Collect the results
    voice_port_configs = None
    for event in runner.events:
        if "event_data" in event and "res" in event["event_data"]:
            if "msg" in event["event_data"]["res"]:
                voice_port_configs = event["event_data"]["res"]["msg"]
                break

    if voice_port_configs is None:
        return jsonify({"error": "Failed to retrieve voice-port configurations"}), 500

    else:
        print("voicePort Config primera parte: " + str(voice_port_configs))

    # Collect the results
    voice_port_configs = None
    voice_port_summary = None

    # Debugging: Print all events
    print("Events:")
    for event in runner.events:
        if "event_data" in event and "res" in event["event_data"]:
            if "stdout" in event["event_data"]["res"]:
                print(event["event_data"])

    for event in runner.events:
        if "event_data" in event and "res" in event["event_data"]:
            if "stdout" in event["event_data"]["res"]:
                stdout = event['event_data']['res']['stdout']
                if isinstance(stdout, list):
                    stdout = "\n".join(stdout)
                if "voice_port_configs" in event["event_data"]["task"]:
                    voice_port_configs = stdout
                elif "voice_port_summary" in event["event_data"]["task"]:
                    voice_port_summary = stdout

    if voice_port_configs is None or voice_port_summary is None:
        return (
            jsonify(
                {"error": "Failed to retrieve voice-port configurations or summary"}
            ),
            500,
        )

    # Parse voice-port summary to get OPER values
    oper_status = {}
    summary_lines = voice_port_summary.splitlines()
    for line in summary_lines:
        match = re.match(r"(\S+)\s+--\s+\S+\s+\S+\s+(\S+)", line)
        if match:
            port, oper = match.groups()
            oper_status[port] = oper

    # Filter voice-port configurations
    voice_ports = []
    ports = voice_port_configs.split("voice-port ")
    for port in ports:
        if port.strip():
            port_config = "voice-port " + port.strip()
            port_name = re.search(r"voice-port (\S+)", port_config).group(1)
            description = re.search(r"description (.+)", port_config)
            input_gain = re.search(r"input gain (\d+)", port_config)
            output_attenuation = re.search(r"output attenuation (\-?\d+)", port_config)
            admin_status = "shutdown" if "shutdown" in port_config else "up"
            oper = oper_status.get(port_name, "NA")
            voice_ports.append(
                {
                    "port": port_name,
                    "description": description.group(1) if description else "",
                    "input_gain": input_gain.group(1) if input_gain else "0",
                    "output_attenuation": (
                        output_attenuation.group(1) if output_attenuation else "0"
                    ),
                    "admin_status": admin_status,
                    "oper": oper,
                }
            )

    return jsonify(voice_ports)


@app.route("/writeVoicePortConfig", methods=["POST"])
def write_voice_port_config():
    data = request.json
    target_ip = data.get("target_ip")
    username = data.get("username")
    password = data.get("password")
    port_name = data.get("port_name")
    input_gain = data.get("input_gain",0)
    output_attenuation = data.get("output_attenuation", 0)
    description = data.get("description", "NA")
    admin_status = data.get("admin_status", "up")

    if not target_ip or not username or not password or not port_name:
        return (
            jsonify(
                {"error": "target_ip, username, password, and port_name are required"}
            ),
            400,
        )

    # Define the dynamic inventory as a dictionary
    dynamic_inventory = {
        "all": {
            "hosts": {
                "cisco_router": {
                    "ansible_host": target_ip,
                    # "ansible_network_os": "cisco.ios.ios",
                    "ansible_user": username,
                    "ansible_password": password,
                    # "ansible_ssh_pass": password,
                    "ansible_connection": "network_cli",
                    "ansible_network_os": "ios",
                    # parametros para usar un JumpBox
                    # "ansible_ssh_common_args": '-o StrictHostKeyChecking=no -o KexAlgorithms=diffie-hellman-group-exchange-sha1 -o HostKeyAlgorithms=ssh-rsa -o ProxyCommand="sshpass -p C1sco12345 ssh -o StrictHostKeyChecking=no -W %h:%p -q developer@10.10.20.50"',
                    "ansible_ssh_common_args": "-o StrictHostKeyChecking=no -o KexAlgorithms=diffie-hellman-group-exchange-sha1 -o HostKeyAlgorithms=ssh-rsa",
                }
            }
        }
    }

    # Path to the playbook file
    playbook_path = "configure_voice_port_playbook.yml"

    # Example playbook content to configure the voice-port on a specific Cisco IOS router
    playbook_content = [
        {
            "name": "Configure voice-port on Cisco IOS router",
            "hosts": "cisco_router",
            "gather_facts": "no",
            "tasks": [
                {
                    "name": "Configure voice-port",
                    "cisco.ios.ios_config": {
                        "lines": [
                            
                            "{{ 'input gain ' + input_gain if input_gain != 'NA' else '' }}",
                            "{{ 'output attenuation ' + output_attenuation if output_attenuation != 'NA' else '' }}",
                            "{{ 'shutdown' if admin_status == 'shutdown' else 'no shutdown' }}",
                        ],
                        "parents": "voice-port {{ port_name }}",
                    },
                }
            ],
        }
    ]

    # Write the playbook content to the specified file
    with open(playbook_path, "w") as playbook_file:
        yaml.dump(playbook_content, playbook_file)

    # Run the playbook using ansible-runner with verbosity level 3 (equivalent to -vvv)
    runner = ansible_runner.run(
        private_data_dir=".",
        playbook=playbook_path,
        inventory=dynamic_inventory,
        extravars={
            "port_name": port_name,
            "input_gain": input_gain,
            "output_attenuation": output_attenuation,
            "description": description,
            "admin_status": admin_status,
        },
        verbosity=3,  # Set verbosity level here
    )

    # Collect the results
    if runner.rc != 0:
        return jsonify({"error": "Failed to configure voice-port"}), 500

    return jsonify({"status": "Voice-port configured successfully"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
