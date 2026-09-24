$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$TerraformDir = Join-Path $Root "terraform"
$InventoryFile = Join-Path $Root "ansible\inventory\generated.ini"

Push-Location $TerraformDir

try {
    $vms = terraform output -json vms | ConvertFrom-Json
}
finally {
    Pop-Location
}

$lines = @(
    "[proxmox_lab]"
)

$vms.PSObject.Properties |
    Sort-Object Name |
    ForEach-Object {
        $name = $_.Name
        $ip = $_.Value.ip -replace '/\d+$', ''

        $lines += "$name ansible_host=$ip"
    }

$lines += ""
$lines += "[proxmox_lab:vars]"
$lines += "ansible_user=devops"
$lines += "ansible_ssh_private_key_file=/root/.ssh/proxmox-self-service-ansible"
$lines += "ansible_python_interpreter=/usr/bin/python3"

$lines | Set-Content -Path $InventoryFile -Encoding ascii

Write-Host "Inventory generated:"
Write-Host $InventoryFile
Get-Content $InventoryFile
