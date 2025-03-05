import logging
from driftai.audio import AudioRecorder


def test_recorder() -> None:
    chunk_duration = None
    
    # try:
    #     user_duration = input("Enter chunk duration in seconds (default is 2): ")
    #     if user_duration.strip():
    #         chunk_duration = float(user_duration)
    # except ValueError:
    #     logging.error("Invalid input. Using default 2 seconds.")
    
    recorder = AudioRecorder(chunk_duration=chunk_duration)
    recorder.start_recording()
    
    logging.info(f"Audio recording has started in the background with {chunk_duration} second chunks.")
    logging.info("Type 'stop' to stop recording.")
    
    try:
        while True:
            user_input = input("> ").strip().lower()
            if user_input == "stop":
                logging.info("Stopping the recording...")
                recorder.stop_recording()
                break
            elif user_input == "help":
                logging.info(
                    "Commands available:" \
                    "\n  stop - Stop recording and exit" \
                    "\n  help - Show this help message"
                )
            else:
                logging.info(f"Unknown command: {user_input}. Type 'help' for available commands.")
    except KeyboardInterrupt:
        logging.error("\nInterrupted by user. Stopping recording...")
        recorder.stop_recording()
    
    logging.info("Program exited.")
