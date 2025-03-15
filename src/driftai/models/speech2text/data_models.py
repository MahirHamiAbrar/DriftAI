from pydantic import BaseModel
from driftai.models.status import ModelStatus


class ExceptionObject(BaseModel):
    error: str

class AudioFileObject(BaseModel):
    audio_file: str

class ModelStatusCheck(BaseModel):
    status: ModelStatus

class TranscriptionStatusCheck(BaseModel):
    job_id: str
    status: ModelStatus
    audio_file: str
    result: dict | None = None
