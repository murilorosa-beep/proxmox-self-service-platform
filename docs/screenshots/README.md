# Screenshot Checklist

This directory is reserved for real project evidence. Do not add mock screenshots or images containing credentials.

Before committing an image, verify that it does not expose API tokens, passwords, private keys, environment-file contents, real Terraform variables, state contents, browser sessions, unrelated infrastructure, or sensitive company information. Crop or retake the screenshot when in doubt; do not silently edit evidence.

## Recommended Captures

- [ ] `01-proxmox-vms.png`
  - Proxmox VM list showing `portal-dev-01` and `portal-dev-02`.
  - Include useful columns such as VMID, name, status, CPU, and memory.
  - Crop out unrelated hosts, storage names, users, and other company VMs.

- [ ] `02-api-job-ready.png`
  - Terminal showing a sanitized `POST /api/vms` response and the final job with `status: ready`.
  - Keep the job state, VM name, VMID, and lab IP visible.
  - Ensure command history does not show credentials or environment variables.

- [ ] `03-terraform-state.png`
  - `terraform state list` showing the managed VM resource addresses.
  - Do not show the contents of `terraform.tfstate`.

- [ ] `04-terraform-plan.png`
  - A clean plan ending with `No changes. Your infrastructure matches the configuration.`
  - Avoid commands that print provider environment variables.

- [ ] `05-ansible-playbook.png`
  - First successful base-playbook run with task names and recap.
  - Crop usernames, filesystem paths, and inventory details if they reveal sensitive infrastructure.

- [ ] `06-ansible-idempotency.png`
  - Second playbook run showing `changed=0`, `unreachable=0`, and `failed=0`.
  - This is one of the strongest portfolio screenshots because it demonstrates convergence.

- [ ] `07-qemu-agent.png`
  - Proxmox shell showing `qm agent <vmid> get-host-name` and the expected hostname.
  - Include only the relevant command and response.

- [ ] `08-fastapi-docs.png`
  - FastAPI Swagger UI at `/docs`, showing the health, VM, and job endpoints.
  - Use a clean browser window and hide bookmarks, account details, and unrelated tabs.

- [ ] `09-job-flow.png`
  - Sanitized `/api/jobs/{job_id}` response with `status: ready`, allocation, resource, and Ansible completion.
  - Remove or crop any unrelated job errors that could expose internal paths.

## Optional High-Value Captures

- [ ] `10-proxmox-vm-summary.png`
  - VM hardware/summary view showing the expected CPU, RAM, disk, network, Cloud-init drive, and running state.

- [ ] `11-api-to-ready-sequence.png`
  - A terminal layout showing the initial `202 Accepted` response and a later `ready` response together.

- [ ] `12-repository-structure.png`
  - GitHub repository page showing the clean project structure and documentation files.

## README Integration

Once reviewed images exist, the strongest initial README set is:

1. `01-proxmox-vms.png` — visible infrastructure result.
2. `02-api-job-ready.png` or `11-api-to-ready-sequence.png` — self-service workflow.
3. `04-terraform-plan.png` — infrastructure convergence.
4. `06-ansible-idempotency.png` — configuration convergence.
5. `08-fastapi-docs.png` — API surface.

Only reference files that actually exist so the README never contains broken image links.
