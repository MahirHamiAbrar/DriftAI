import datetime
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional


class JobStatus(Enum):
    """Enumeration of possible job statuses"""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    PAUSED = "paused"


class Job:
    """
    Class to track job status and related metadata.
    Handles status updates and stores additional job-related information.
    """
    def __init__(self, job_id: Optional[str] = None, 
                 name: str = "Unnamed Job",
                 description: str = "",
                 initial_status: JobStatus = JobStatus.PENDING):
        """
        Initialize a new job with the given parameters.
        
        Args:
            job_id: Unique identifier for the job. If None, a UUID will be generated.
            name: Human-readable name for the job.
            description: Detailed description of the job.
            initial_status: Starting status for the job.
        """
        self.job_id = job_id if job_id else str(uuid.uuid4())
        self.name = name
        self.description = description
        self._status = initial_status
        self.created_at = datetime.datetime.now()
        self.updated_at = self.created_at
        self.status_history = [(self.created_at, initial_status)]
        self.data = {}  # Additional data related to the job
        self.progress = 0.0  # Progress from 0.0 to 1.0
        self.error_message = None  # Stores error messages if job fails
        self.result = None  # Stores the result of completed jobs

    @property
    def status(self) -> JobStatus:
        """Get the current job status"""
        return self._status
    
    @status.setter
    def status(self, new_status: JobStatus) -> None:
        """
        Update the job status and record the change in history.
        
        Args:
            new_status: The new status to set for the job.
        """
        if new_status != self._status:
            timestamp = datetime.datetime.now()
            self._status = new_status
            self.updated_at = timestamp
            self.status_history.append((timestamp, new_status))
            
            # Auto-set error message for failed jobs if none exists
            if new_status == JobStatus.FAILED and not self.error_message:
                self.error_message = "Job failed without specific error message"
    
    def update_progress(self, progress: float) -> None:
        """
        Update the job progress.
        
        Args:
            progress: A float between 0.0 and 1.0 representing job completion percentage.
        """
        if not 0.0 <= progress <= 1.0:
            raise ValueError("Progress must be between 0.0 and 1.0")
        
        self.progress = progress
        self.updated_at = datetime.datetime.now()
        
        # Auto-update status to completed if progress reaches 100%
        if progress >= 1.0 and self._status != JobStatus.COMPLETED:
            self.status = JobStatus.COMPLETED
    
    def set_data(self, key: str, value: Any) -> None:
        """
        Store additional data related to the job.
        
        Args:
            key: The identifier for the data.
            value: The data to store.
        """
        self.data[key] = value
        self.updated_at = datetime.datetime.now()
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """
        Retrieve job-related data by key.
        
        Args:
            key: The identifier for the data to retrieve.
            default: Value to return if key is not found.
            
        Returns:
            The stored data value or the default if not found.
        """
        return self.data.get(key, default)
    
    def set_error(self, message: str) -> None:
        """
        Set an error message and update status to FAILED.
        
        Args:
            message: The error message to store.
        """
        self.error_message = message
        self.status = JobStatus.FAILED
    
    def set_result(self, result: Any) -> None:
        """
        Set the job result and update status to COMPLETED.
        
        Args:
            result: The result of the job.
        """
        self.result = result
        self.status = JobStatus.COMPLETED
    
    def get_elapsed_time(self) -> datetime.timedelta:
        """
        Calculate the elapsed time since job creation.
        
        Returns:
            Timedelta representing elapsed time.
        """
        return datetime.datetime.now() - self.created_at
    
    def get_status_history(self) -> List[Dict[str, Any]]:
        """
        Get the complete status change history in a structured format.
        
        Returns:
            List of dictionaries containing timestamp and status information.
        """
        return [
            {"timestamp": timestamp, "status": status.value}
            for timestamp, status in self.status_history
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert job information to a dictionary, useful for serialization.
        
        Returns:
            Dictionary representation of the job.
        """
        return {
            "job_id": self.job_id,
            "name": self.name,
            "description": self.description,
            "status": self._status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "progress": self.progress,
            "error_message": self.error_message,
            "data": self.data,
            "result": self.result
        }
    
    def __str__(self) -> str:
        """String representation of the job."""
        return f"Job(id={self.job_id}, name={self.name}, status={self._status.value}, progress={self.progress:.1%})"


class JobManager:
    """
    Manager class to handle multiple jobs.
    """
    def __init__(self):
        """Initialize a new job manager."""
        self.jobs = {}  # Dictionary of job_id -> Job
    
    def create_job(self, **kwargs) -> Job:
        """
        Create a new job and register it with the manager.
        
        Args:
            **kwargs: Arguments to pass to the Job constructor.
            
        Returns:
            The newly created Job instance.
        """
        job = Job(**kwargs)
        self.jobs[job.job_id] = job
        return job
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """
        Retrieve a job by its ID.
        
        Args:
            job_id: The ID of the job to retrieve.
            
        Returns:
            The Job instance if found, None otherwise.
        """
        return self.jobs.get(job_id)
    
    def update_job_status(self, job_id: str, status: JobStatus) -> bool:
        """
        Update the status of a job.
        
        Args:
            job_id: The ID of the job to update.
            status: The new status to set.
            
        Returns:
            True if successful, False if job not found.
        """
        job = self.get_job(job_id)
        if job:
            job.status = status
            return True
        return False
    
    def list_jobs(self, status: Optional[JobStatus] = None) -> List[Job]:
        """
        List all jobs, optionally filtered by status.
        
        Args:
            status: If provided, only return jobs with this status.
            
        Returns:
            List of Job instances.
        """
        if status is None:
            return list(self.jobs.values())
        
        return [job for job in self.jobs.values() if job.status == status]
    
    def clear_completed_jobs(self) -> int:
        """
        Remove all completed jobs from the manager.
        
        Returns:
            Number of jobs removed.
        """
        completed_ids = [
            job_id for job_id, job in self.jobs.items() 
            if job.status == JobStatus.COMPLETED
        ]
        
        for job_id in completed_ids:
            del self.jobs[job_id]
            
        return len(completed_ids)
