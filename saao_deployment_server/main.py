from fastapi import FastAPI
from pydantic import BaseModel


class Deployment(BaseModel):
    """Model for a deployment request."""
    project: str
    version: str


app = FastAPI()


@app.post("/deploy")
async def deploy(deployment: Deployment):
    return {}
