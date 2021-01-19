from fastapi import FastAPI

app = FastAPI()

@app.post("/deploy")
async def deploy():
    return {}
