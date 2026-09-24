from datetime import datetime, timezone
from uuid import uuid4

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field


app = FastAPI(
    title="Proxmox Self-Service Platform",
    version="0.3.0"
)


class VMCreateRequest(BaseModel):
    name: str = Field(min_length=3, max_length=40)
    cpu: int = Field(ge=1, le=8)
    memory_mb: int = Field(ge=1024, le=16384)
    disk_gb: int = Field(ge=20, le=200)


jobs = {}


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "proxmox-self-service"
    }


@app.post("/api/vms", status_code=status.HTTP_202_ACCEPTED)
def create_vm(vm: VMCreateRequest):
    job_id = str(uuid4())

    job = {
        "id": job_id,
        "type": "create_vm",
        "status": "queued",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "vm": vm.model_dump()
    }

    jobs[job_id] = job

    return job


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str):
    job = jobs.get(job_id)

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job


@app.get("/api/jobs")
def list_jobs():
    return list(jobs.values())
