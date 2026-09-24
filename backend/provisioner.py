import json
import os
import socket
import subprocess
import tempfile
import threading
import time
from pathlib import Path

from dotenv import dotenv_values


ROOT = Path(__file__).resolve().parents[1]

TERRAFORM_DIR = ROOT / "terraform"
PORTAL_VARS = TERRAFORM_DIR / "portal.auto.tfvars.json"
TERRAFORM_ENV = Path.home() / ".config/proxmox-self-service/terraform.env"
TERRAFORM_PLAN = TERRAFORM_DIR / "portal.tfplan"

ANSIBLE_PLAYBOOK = ROOT / "ansible" / "playbooks" / "base.yml"

SSH_PRIVATE_KEY = Path.home() / ".ssh" / "self-service-managed"
PLATFORM_KNOWN_HOSTS = Path.home() / ".ssh" / "self-service-known_hosts"

terraform_lock = threading.Lock()


def terraform_environment():
    env = os.environ.copy()

    values = dotenv_values(TERRAFORM_ENV)

    for key, value in values.items():
        if value is not None:
            env[key] = value

    return env


def run_terraform(*args):
    return subprocess.run(
        ["terraform", *args],
        cwd=TERRAFORM_DIR,
        env=terraform_environment(),
        text=True,
        capture_output=True,
    )


def load_portal_vms():
    if not PORTAL_VARS.exists():
        return {"portal_vms": {}}

    data = json.loads(PORTAL_VARS.read_text())
    data.setdefault("portal_vms", {})

    return data


def save_portal_vms(data):
    temporary = PORTAL_VARS.with_suffix(".tmp")

    temporary.write_text(
        json.dumps(data, indent=2) + "\n"
    )

    temporary.replace(PORTAL_VARS)


def allocate_resources(data):
    portal_vms = data["portal_vms"]

    used_vmids = {
        int(vm["vm_id"])
        for vm in portal_vms.values()
    }

    vm_id = 9400

    while vm_id in used_vmids:
        vm_id += 1

    used_ips = {
        vm["ipv4_address"]
        for vm in portal_vms.values()
    }

    for host in range(110, 200):
        address = f"172.16.16.{host}/24"

        if address not in used_ips:
            return vm_id, address

    raise RuntimeError("No IP addresses available in portal pool")


def wait_for_ssh(host, timeout=240):
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            with socket.create_connection((host, 22), timeout=5):
                return
        except OSError:
            time.sleep(5)

    raise RuntimeError(
        f"SSH did not become available on {host}:22 within {timeout} seconds"
    )


def register_host_key(host):
    PLATFORM_KNOWN_HOSTS.parent.mkdir(
        mode=0o700,
        parents=True,
        exist_ok=True,
    )

    if PLATFORM_KNOWN_HOSTS.exists():
        subprocess.run(
            [
                "ssh-keygen",
                "-f",
                str(PLATFORM_KNOWN_HOSTS),
                "-R",
                host,
            ],
            text=True,
            capture_output=True,
        )

    last_error = None

    for _ in range(10):
        scan = subprocess.run(
            [
                "ssh-keyscan",
                "-T",
                "5",
                "-H",
                "-t",
                "ed25519",
                host,
            ],
            text=True,
            capture_output=True,
        )

        if scan.returncode == 0 and scan.stdout.strip():
            with PLATFORM_KNOWN_HOSTS.open("a") as known_hosts:
                known_hosts.write(scan.stdout)

            PLATFORM_KNOWN_HOSTS.chmod(0o600)

            fingerprint = subprocess.run(
                ["ssh-keygen", "-lf", "-"],
                input=scan.stdout,
                text=True,
                capture_output=True,
            )

            return fingerprint.stdout.strip()

        last_error = scan.stderr
        time.sleep(3)

    raise RuntimeError(
        f"Could not obtain SSH host key from {host}: {last_error}"
    )


def run_ansible(vm_name, host):
    inventory = f"""[portal_vms]
{vm_name} ansible_host={host}

[portal_vms:vars]
ansible_user=devops
ansible_ssh_private_key_file={SSH_PRIVATE_KEY}
ansible_python_interpreter=/usr/bin/python3
ansible_ssh_common_args='-o UserKnownHostsFile={PLATFORM_KNOWN_HOSTS} -o StrictHostKeyChecking=yes'
"""

    inventory_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".ini",
            prefix="self-service-",
            delete=False,
        ) as temporary_inventory:
            temporary_inventory.write(inventory)
            inventory_path = temporary_inventory.name

        return subprocess.run(
            [
                "ansible-playbook",
                "-i",
                inventory_path,
                str(ANSIBLE_PLAYBOOK),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

    finally:
        if inventory_path:
            Path(inventory_path).unlink(missing_ok=True)


def provision_vm(job_id, jobs):
    with terraform_lock:
        job = jobs[job_id]
        vm = job["vm"]

        original_content = (
            PORTAL_VARS.read_text()
            if PORTAL_VARS.exists()
            else '{\n  "portal_vms": {}\n}\n'
        )

        apply_started = False

        try:
            job["status"] = "allocating"

            data = load_portal_vms()

            if vm["name"] in data["portal_vms"]:
                raise RuntimeError(
                    f'VM "{vm["name"]}" already exists'
                )

            vm_id, ipv4_address = allocate_resources(data)
            host = ipv4_address.split("/")[0]

            data["portal_vms"][vm["name"]] = {
                "vm_id": vm_id,
                "cpu_cores": vm["cpu"],
                "memory_mb": vm["memory_mb"],
                "disk_size_gb": vm["disk_gb"],
                "ipv4_address": ipv4_address,
            }

            save_portal_vms(data)

            job["allocation"] = {
                "vm_id": vm_id,
                "ip": ipv4_address,
            }

            job["status"] = "planning"

            plan = run_terraform(
                "plan",
                "-input=false",
                "-out=portal.tfplan",
            )

            if plan.returncode != 0:
                PORTAL_VARS.write_text(original_content)

                raise RuntimeError(
                    plan.stderr or plan.stdout
                )

            job["status"] = "applying"
            apply_started = True

            apply = run_terraform(
                "apply",
                "-input=false",
                "portal.tfplan",
            )

            if apply.returncode != 0:
                raise RuntimeError(
                    apply.stderr or apply.stdout
                )

            job["status"] = "waiting_for_ssh"

            wait_for_ssh(host)

            job["status"] = "registering_host_key"

            job["ssh_host_fingerprint"] = register_host_key(host)

            job["status"] = "configuring"

            ansible = run_ansible(
                vm["name"],
                host,
            )

            if ansible.returncode != 0:
                raise RuntimeError(
                    ansible.stderr or ansible.stdout
                )

            job["status"] = "ready"

            job["resource"] = {
                "name": vm["name"],
                "vm_id": vm_id,
                "ip": ipv4_address,
            }

            job["configuration"] = {
                "ansible": "completed"
            }

        except Exception as exc:
            job["status"] = "failed"
            job["error"] = str(exc)[-5000:]

            # Restore desired configuration only if Terraform apply
            # never started. Once infrastructure may have changed,
            # automatic rollback would be unsafe.
            if not apply_started:
                PORTAL_VARS.write_text(original_content)

        finally:
            if TERRAFORM_PLAN.exists():
                TERRAFORM_PLAN.unlink()
