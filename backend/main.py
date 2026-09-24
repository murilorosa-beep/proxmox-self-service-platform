from fastapi import FastAPI, status
from pydantic import BaseModel, Field

app = FastAPI(
    title="Proxmox Self-Service Platform",
    version="0.2.0"
)


class VMCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=40)
    cpu: int = Field(ge=1, le=8)
    memory_mb: int = Field(ge=1024, le=16384)
    disk_gb: int = Field(ge=20, le=200)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "proxmox-self-service"
    }


@app.post("/api/vms", status_code=status.HTTP_202_ACCEPTED)
def create_vm(vm: VMCreateRequest):
    return {
        "status": "accepted",
        "message": "VM provisioning request accepted",
        "request": vm
    }
