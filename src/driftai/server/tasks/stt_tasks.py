from driftai.models.status import ModelStatus
from driftai.models.speech2text import (
    # transcription
    AudioTranscriptor,

    # data models
    AudioFileObject,
    ModelStatusCheck,
    TranscriptionStatusCheck
)

# model loading status
model_status = ModelStatusCheck(
    status = ModelStatus.NotLoaded
)

# the background task function to load the model
def audio_transcriptor_load_task() -> None:
    global audio_transcriptor, model_status

    # change status to "model loading"
    model_status.status = ModelStatus.Loading

    # load the model
    audio_transcriptor = AudioTranscriptor()
    audio_transcriptor.load_model()

    # change status to "model loaded"
    model_status.status = ModelStatus.Loaded


# audio transcription background task
def transcribe_audio_task(job: TranscriptionStatusCheck) -> None:
    global audio_transcriptor, job_status

    # get the job id
    job_id = job.job_id

    # set transcription status to "processing"
    job_status[job_id].status = ModelStatus.DataProcessing

    # transcribe the audio
    result = audio_transcriptor.transcribe(audio=job.audio_file)

    # set transcription status to "complete"
    job_status[job_id].result = result
    job_status[job_id].status = ModelStatus.DataProcessingComplete

