from pydantic import BaseModel


class JiraSearchTaskRequest(BaseModel):
    prompt: str
    capture_screenshots: bool = False
    export_csv: bool = True
    max_results: int = 100
