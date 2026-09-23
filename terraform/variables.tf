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

variable "vm_id" {
  description = "VMID for the new virtual machine."
  type        = number
  default     = 9200
}

variable "vm_name" {
  description = "Name of the virtual machine."
  type        = string
  default     = "tf-dev-01"
}

variable "cpu_cores" {
  description = "Number of virtual CPU cores."
  type        = number
  default     = 2

  validation {
    condition     = var.cpu_cores >= 1 && var.cpu_cores <= 4
    error_message = "CPU must be between 1 and 4 cores."
  }
}

variable "memory_mb" {
  description = "Dedicated memory in MB."
  type        = number
  default     = 4096

  validation {
    condition     = contains([2048, 4096, 8192], var.memory_mb)
    error_message = "Memory must be 2048, 4096 or 8192 MB."
  }
}

variable "disk_size_gb" {
  description = "Primary disk size in GB."
  type        = number
  default     = 40

  validation {
    condition     = var.disk_size_gb >= 20 && var.disk_size_gb <= 100
    error_message = "Disk size must be between 20 and 100 GB."
  }
}

variable "bridge" {
  description = "Proxmox network bridge."
  type        = string
  default     = "vmbr1"
}

variable "ipv4_address" {
  description = "Static IPv4 address in CIDR notation."
  type        = string
  default     = "172.16.16.101/24"
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
