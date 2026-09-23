output "vm_id" {
  description = "Proxmox VMID."
  value       = proxmox_virtual_environment_vm.vm.vm_id
}

output "vm_name" {
  description = "Virtual machine name."
  value       = proxmox_virtual_environment_vm.vm.name
}

output "configured_ipv4_address" {
  description = "IPv4 address configured through Cloud-init."
  value       = var.ipv4_address
}

output "node_name" {
  description = "Proxmox node."
  value       = proxmox_virtual_environment_vm.vm.node_name
}
