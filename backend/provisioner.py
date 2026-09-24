import json
import os
import subprocess
import threading
from pathlib import Path

from dotenv import dotenv_values


ROOT = Path(__file__).resolve().parents[1]
TERRAFORM_DIR = ROOT / "terraform"
PORTAL_VARS = TERRAFORM_DIR / "portal.auto.tfvars.json"
TERRAFORM_ENV = Path.home() / ".config/proxmox-self-service/terraform.env"
TERRAFORM_PLAN = TERRAFORM_DIR / "portal.tfplan"

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

            job["status"] = "provisioned"

            job["resource"] = {
                "name": vm["name"],
                "vm_id": vm_id,
                "ip": ipv4_address,
            }

        except Exception as exc:
            job["status"] = "failed"
            job["error"] = str(exc)[-3000:]

            # Se Terraform ainda não começou o apply,
            # podemos restaurar a configuração anterior.
            if not apply_started:
                PORTAL_VARS.write_text(original_content)

        finally:
            if TERRAFORM_PLAN.exists():
                TERRAFORM_PLAN.unlink()
