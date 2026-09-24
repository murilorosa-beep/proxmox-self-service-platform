from fastapi import FastAPI

app = FastAPI(
    title="Proxmox Self-Service Platform",
    version="0.1.0"
)

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "service": "proxmox-self-service"
    }
