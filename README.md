# Proxmox Self-Service VM Platform

A self-service private cloud platform for automated virtual machine provisioning on Proxmox VE.

## Overview

This project aims to build a self-service platform that allows users to provision virtual machines automatically in a Proxmox VE environment.

Instead of manually creating and configuring virtual machines through the Proxmox interface, users will be able to request infrastructure through a web portal.

The provisioning process will integrate Infrastructure as Code, automation and configuration management technologies.

## Architecture

```text
User
  ↓
Web Portal
  ↓
FastAPI
  ↓
Terraform
  ↓
Proxmox VE 9
  ↓
Cloud-init
  ↓
Ansible
  ↓
Monitoring / Security
```

## Technologies

* Proxmox VE 9
* Terraform
* Cloud-init
* Ansible
* Python
* FastAPI
* Docker
* Git
* GitHub
* Linux
* REST API
* Zabbix
* Wazuh

## Project Goals

Users will eventually be able to request virtual machines by specifying parameters such as:

* VM name
* CPU
* RAM
* Disk size
* Operating system
* Network
* Environment

The infrastructure will then be provisioned automatically through the Proxmox API.

## Current Milestone

The first milestone of the project is:

```text
Terraform
    ↓
Proxmox API
    ↓
Automated VM creation
```

The web portal and advanced automation features will be implemented after the base provisioning workflow is working.

## Repository Structure

```text
proxmox-self-service-platform/

├── terraform/
├── backend/
├── frontend/
├── ansible/
├── docs/
│   ├── screenshots/
│   └── diagrams/
├── .gitignore
└── README.md
```

## Roadmap

* [ ] Create Ubuntu 24.04 Cloud-init template
* [ ] Configure dedicated Proxmox API authentication
* [ ] Install and configure Terraform
* [ ] Provision the first VM using Terraform
* [ ] Parameterize CPU, RAM, disk and network
* [ ] Configure Cloud-init
* [ ] Create FastAPI backend
* [ ] Create self-service web portal
* [ ] Integrate Ansible
* [ ] Add VM inventory
* [ ] Add Start / Stop / Reboot / Delete operations
* [ ] Implement RBAC
* [ ] Implement approval workflow
* [ ] Implement resource quotas
* [ ] Implement automatic VM expiration
* [ ] Add CI/CD pipeline
* [ ] Integrate Zabbix monitoring
* [ ] Integrate Wazuh security monitoring

## Security

The project follows the principle of least privilege.

Terraform will use a dedicated Proxmox API account and API token instead of the `root@pam` account.

Sensitive information such as API tokens, passwords, SSH private keys, environment files and Terraform state files must never be committed to the public repository.

## Project Status

🚧 Work in progress.

Current phase: project structure and documentation.

## Author

Murilo Martins
