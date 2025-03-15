from pydantic import BaseModel
from driftai.stt import JobStatus


class ExceptionObject(BaseModel):
    error: str

class AudioFileObject(BaseModel):
    audio_file: str

class ModelStatusCheck(BaseModel):
    status: JobStatus

class TranscriptionStatusCheck(BaseModel):
    job_id: str
    status: JobStatus
    audio_file: str
    result: dict | None = None
