from typing import Optional
from fastapi import File, Form, UploadFile
from pydantic import BaseModel

class ImageRequestDTO:
    def __init__(
        self,
        image: UploadFile = File(...),
        description: Optional[str] = Form(None)
    ):
        self.image = image
        self.description = description

