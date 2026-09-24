moved {
  from = proxmox_virtual_environment_vm.vm
  to   = proxmox_virtual_environment_vm.vm["tf-dev-01"]
}

resource "proxmox_virtual_environment_vm" "vm" {
  for_each = var.vms

  name        = each.key
  description = "Managed by Terraform - Proxmox Self-Service Platform"
  tags        = ["lab", "terraform", "self-service"]

  node_name = var.node_name
  vm_id     = each.value.vm_id

  started = true

  clone {
    vm_id        = var.template_vm_id
    node_name    = var.node_name
    datastore_id = "local-lvm"
    full         = true
  }

  cpu {
    cores = each.value.cpu_cores
    type  = "x86-64-v2-AES"
  }

  memory {
    dedicated = each.value.memory_mb
  }

  scsi_hardware = "virtio-scsi-single"

  disk {
    datastore_id = "local-lvm"
    interface    = "scsi0"
    size         = each.value.disk_size_gb
    discard      = "on"
    ssd          = true
  }

  network_device {
    bridge = var.bridge
    model  = "virtio"
  }

  initialization {
    datastore_id = "local-lvm"

    dns {
      domain  = var.dns_domain
      servers = var.dns_servers
    }

    ip_config {
      ipv4 {
        address = each.value.ipv4_address
        gateway = var.ipv4_gateway
      }
    }

    user_account {
      username = var.cloud_init_user
      keys = [
        trimspace(file(pathexpand(var.ssh_public_key_path))),
        trimspace(var.ansible_ssh_public_key)
      ]
    }
  }

  agent {
    enabled = true

    wait_for_ip {
      disabled = true
    }
  }

  operating_system {
    type = "l26"
  }

  serial_device {
    device = "socket"
  }

  stop_on_destroy = true
}
