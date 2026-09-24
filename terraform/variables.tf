variable "node_name" {
  description = "Proxmox node where the VM will be created."
  type        = string
  default     = "gagreciclagem"
}

variable "template_vm_id" {
  description = "VMID of the Ubuntu 24.04 Cloud-init template."
  type        = number
  default     = 9000
}

variable "vms" {
  description = "Virtual machines managed by the platform."

  type = map(object({
    vm_id        = number
    cpu_cores    = number
    memory_mb    = number
    disk_size_gb = number
    ipv4_address = string
  }))

  validation {
    condition     = alltrue([for vm in values(var.vms) : vm.cpu_cores >= 1 && vm.cpu_cores <= 4])
    error_message = "CPU must be between 1 and 4 cores for every VM."
  }

  validation {
    condition     = alltrue([for vm in values(var.vms) : contains([2048, 4096, 8192], vm.memory_mb)])
    error_message = "Memory must be 2048, 4096 or 8192 MB for every VM."
  }

  validation {
    condition     = alltrue([for vm in values(var.vms) : vm.disk_size_gb >= 20 && vm.disk_size_gb <= 100])
    error_message = "Disk size must be between 20 and 100 GB for every VM."
  }
}

variable "bridge" {
  description = "Proxmox network bridge."
  type        = string
  default     = "vmbr1"
}

variable "ipv4_gateway" {
  description = "IPv4 gateway."
  type        = string
  default     = "172.16.16.16"
}

variable "dns_servers" {
  description = "DNS servers used by the VM."
  type        = list(string)
  default     = ["1.1.1.1"]
}

variable "dns_domain" {
  description = "DNS search domain."
  type        = string
  default     = "lab.internal"
}

variable "cloud_init_user" {
  description = "User created by Cloud-init."
  type        = string
  default     = "devops"
}

variable "ssh_public_key_path" {
  description = "Path to SSH public key used by Cloud-init."
  type        = string
  default     = "~/.ssh/proxmox-self-service.pub"
}

variable "ansible_ssh_public_key" {
  description = "Public SSH key used by the Ansible controller."
  type        = string
  default     = "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAINsyhtYAH6vKtvBTD0DFUCmcXhvTRUBoCFIWWi/l/IWg ansible-proxmox-lab"
}

variable "portal_vms" {
  description = "Virtual machines created through the self-service portal."

  type = map(object({
    vm_id        = number
    cpu_cores    = number
    memory_mb    = number
    disk_size_gb = number
    ipv4_address = string
  }))

  default = {}

  validation {
    condition     = alltrue([for vm in values(var.portal_vms) : vm.cpu_cores >= 1 && vm.cpu_cores <= 8])
    error_message = "CPU must be between 1 and 8 cores."
  }

  validation {
    condition     = alltrue([for vm in values(var.portal_vms) : vm.memory_mb >= 1024 && vm.memory_mb <= 16384])
    error_message = "Memory must be between 1024 and 16384 MB."
  }

  validation {
    condition     = alltrue([for vm in values(var.portal_vms) : vm.disk_size_gb >= 20 && vm.disk_size_gb <= 200])
    error_message = "Disk size must be between 20 and 200 GB."
  }
}
