from pydantic import BaseModel
from driftai.stt import TranscriptionStatus


class ExceptionObject(BaseModel):
    error: Exception

class AudioFileObject(BaseModel):
    audio_file: str

class ModelStatusCheck(BaseModel):
    status: TranscriptionStatus

class TranscriptionStatusCheck(BaseModel):
    job_id: str
    status: TranscriptionStatus
    audio_file: str
    result: dict | None = None
