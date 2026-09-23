resource "proxmox_virtual_environment_vm" "vm" {
  name        = var.vm_name
  description = "Managed by Terraform - Proxmox Self-Service Platform"
  tags        = ["lab", "terraform", "self-service"]

  node_name = var.node_name
  vm_id     = var.vm_id

  started = true

  clone {
    vm_id        = var.template_vm_id
    node_name    = var.node_name
    datastore_id = "local-lvm"
    full         = true
  }

  cpu {
    cores = var.cpu_cores
    type  = "x86-64-v2-AES"
  }

  memory {
    dedicated = var.memory_mb
  }

  scsi_hardware = "virtio-scsi-single"

  disk {
    datastore_id = "local-lvm"
    interface    = "scsi0"
    size         = var.disk_size_gb
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
        address = var.ipv4_address
        gateway = var.ipv4_gateway
      }
    }

    user_account {
      username = var.cloud_init_user
      keys = [
        trimspace(file(pathexpand(var.ssh_public_key_path)))
      ]
    }
  }

  agent {
    enabled = false
  }

  operating_system {
    type = "l26"
  }

  serial_device {
    device = "socket"
  }

  stop_on_destroy = true
}
