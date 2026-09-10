from typing import Literal

from pydantic import BaseModel

class ConversionResponse(BaseModel):
    task_id: str
    status: Literal["processing"]
    message: str
    output_url: str = None
