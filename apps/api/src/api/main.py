from fastapi import FastAPI

from api.routes.tasks import router as tasks_router

app = FastAPI(title="Jira Evidence Automation API", version="0.1.0")
app.include_router(tasks_router)


@app.get("/health")
def health():
    return {"status": "ok"}
