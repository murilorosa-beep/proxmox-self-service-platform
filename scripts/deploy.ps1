$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$TerraformDir = Join-Path $Root "terraform"
$InventoryFile = Join-Path $Root "ansible\inventory\generated.ini"

Write-Host ""
Write-Host "=== Proxmox Self-Service Deployment ==="
Write-Host ""

# --------------------------------------------------
# 1. Load Terraform environment
# --------------------------------------------------

Write-Host "[1/5] Loading Proxmox environment..."

Push-Location $TerraformDir

try {
    . .\local-env.ps1

    # --------------------------------------------------
    # 2. Terraform apply
    # --------------------------------------------------

    Write-Host "[2/5] Applying Terraform..."

    terraform apply -auto-approve

    if ($LASTEXITCODE -ne 0) {
        throw "Terraform apply failed."
    }
}
finally {
    Pop-Location
}

# --------------------------------------------------
# 3. Generate Ansible inventory
# --------------------------------------------------

Write-Host "[3/5] Generating Ansible inventory..."

& "$Root\scripts\generate-inventory.ps1"

if ($LASTEXITCODE -ne 0) {
    throw "Inventory generation failed."
}

# --------------------------------------------------
# 4. Send inventory to Ansible controller
# --------------------------------------------------

Write-Host "[4/5] Sending inventory to Ansible controller..."

scp $InventoryFile suporte@10.10.0.222:/home/suporte/inventory.ini

if ($LASTEXITCODE -ne 0) {
    throw "Failed to upload Ansible inventory."
}

# --------------------------------------------------
# 5. Run Ansible remotely
# --------------------------------------------------

Write-Host "[5/5] Running Ansible configuration..."

ssh -t suporte@10.10.0.222 `
    "sudo cp /home/suporte/inventory.ini /opt/ansible/proxmox-lab/inventory.ini && sudo ansible-playbook -i /opt/ansible/proxmox-lab/inventory.ini /opt/ansible/proxmox-lab/base.yml"

if ($LASTEXITCODE -ne 0) {
    throw "Ansible configuration failed."
}

# --------------------------------------------------
# Finished
# --------------------------------------------------

Write-Host ""
Write-Host "=== Deployment completed successfully ==="
Write-Host ""
Write-Host "Terraform infrastructure: OK"
Write-Host "Ansible inventory:       OK"
Write-Host "Ansible configuration:   OK"
Write-Host ""