from enum import Enum


class ModelStatus(Enum):
    Queued = 0
    Loading = 2
    Loaded = 1
    NotLoaded = -1

    DataProcessing = 11
    DataProcessingComplete = 10
    DataProcessingFailed = -10
