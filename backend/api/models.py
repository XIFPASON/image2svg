from pydantic import BaseModel

class ConversionResponse(BaseModel):
    task_id: str
    status: str
    message: str
    output_url: str = None
