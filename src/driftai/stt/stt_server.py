# TODO: Add Exception Handling, what if received "unload_model" request twice in a row?

import gc
import uuid
import torch
import ctypes
from fastapi import FastAPI, BackgroundTasks
from driftai.stt.data_models import (
    AudioFileObject,
    ExceptionObject,
    ModelStatusCheck,
    TranscriptionStatusCheck
)
from driftai.stt import AudioTranscriptor, TranscriptionStatus


# create FastAPI app
app = FastAPI()

# global dictionary to save job status
job_status: dict[str, TranscriptionStatusCheck] = {}

# model loading status
model_status = ModelStatusCheck(
    status = TranscriptionStatus.ModelNotLoaded
)


# the background task function to load the model
def audio_transcriptor_load_task() -> None:
    global audio_transcriptor, model_status

    # change status to "model loading"
    model_status.status = TranscriptionStatus.ModelLoading

    # load the model
    audio_transcriptor = AudioTranscriptor()
    audio_transcriptor.load_model()

    # change status to "model loaded"
    model_status.status = TranscriptionStatus.ModelLoaded


# audio transcription background task
def transcribe_audio_task(job: TranscriptionStatusCheck) -> None:
    global audio_transcriptor, job_status

    # get the job id
    job_id = job.job_id

    # set transcription status to "processing"
    job_status[job_id].status = TranscriptionStatus.TranscriptionProcessing

    # transcribe the audio
    result = audio_transcriptor.transcribe(audio=job.audio_file)

    # set transcription status to "complete"
    job_status[job_id].result = result
    job_status[job_id].status = TranscriptionStatus.TranscriptionComplete


# free memory
def trim_memory() -> int:
  """
    Ref:
        [1] https://github.com/pytorch/pytorch/issues/68114#issuecomment-2160334255
        [2] https://www.softwareatscale.dev/p/run-python-servers-more-efficiently
  """
  libc = ctypes.CDLL("libc.so.6")
  return libc.malloc_trim(0)



@app.get('/stt/model_status')
def check_model_status() -> ModelStatusCheck:
    global model_status
    return model_status


@app.post("/stt/load_model")
def load_model(bg_tasks: BackgroundTasks) -> ModelStatusCheck:
    global model_status

    # set status to "job queued"
    model_status.status = TranscriptionStatus.JobQueued

    # start the background model loading task
    bg_tasks.add_task(audio_transcriptor_load_task)

    return model_status


@app.post('/stt/transcribe/')
def transcribe_audio(audio_file_obj: AudioFileObject, bg_tasks: BackgroundTasks) -> TranscriptionStatusCheck:
    # generate a random job id
    job_id = str(uuid.uuid4()).replace('-', '_')

    # set job status
    job_status[job_id] = TranscriptionStatusCheck(
        job_id = job_id,
        status = TranscriptionStatus.JobQueued,
        audio_file = audio_file_obj.audio_file
    )

    # add the background task
    bg_tasks.add_task(transcribe_audio_task, job_status[job_id])

    return job_status[job_id]


@app.get('/stt/transcription_status/{job_id}')
def get_transcription_status(job_id: str) -> TranscriptionStatusCheck:
    global job_status
    return job_status[job_id]


@app.post('/stt/unload_model')
def unload_model() -> ModelStatusCheck:
    global audio_transcriptor, model_status
    
    del audio_transcriptor

    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    # do the garbage collection
    gc.collect()
    trim_memory()

    model_status.status = TranscriptionStatus.ModelNotLoaded
    return model_status


