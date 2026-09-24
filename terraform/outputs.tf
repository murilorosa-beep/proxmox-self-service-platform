output "vms" {
  description = "Virtual machines managed by the platform."

  value = {
    for name, vm in proxmox_virtual_environment_vm.vm : name => {
      vm_id = vm.vm_id
      ip    = local.all_vms[name].ipv4_address
    }
  }
}
