import pyaudio
import wave
import multiprocessing
import os
from faster_whisper import WhisperModel
import tempfile

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 10  # Adjust as needed
OUTPUT_DIRECTORY = "recordings"

class WhisperCallManager():
    def __init__(self, add_call_log_callback, salesperson_device_id_callback, customer_device_id_callback):
        self.add_call_log_callback = add_call_log_callback
        self.salesperson_device_id_callback = salesperson_device_id_callback
        self.customer_device_id_callback = customer_device_id_callback
        self.inCall = False

        # Ensure the output directory exists
        os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

        self.tempfile_names = [self.create_tempfile_name(suffix=".wav") for _ in range(2)]

    def create_tempfile_name(self, suffix=".wav"):
        return os.path.join(OUTPUT_DIRECTORY, next(tempfile._get_candidate_names()) + suffix)

    def start_call(self):
        # Create processes for each input device
        process1 = multiprocessing.Process(target=self.record_audio, args=(self.salesperson_device_id_callback, self.tempfile_names[0]))
        process2 = multiprocessing.Process(target=self.record_audio, args=(self.customer_device_id_callback, self.tempfile_names[1]))

        # Start recording and transcription processes
        process1.start()
        process2.start()

        try:
            while True:
                # Check if processes are alive and restart if necessary
                if not process1.is_alive():
                    process1 = multiprocessing.Process(target=self.record_audio, args=(self.salesperson_device_id_callback, self.tempfile_names[0]))
                    process1.start()
                
                if not process2.is_alive():
                    process2 = multiprocessing.Process(target=self.record_audio, args=(self.customer_device_id_callback, self.tempfile_names[1]))
                    process2.start()

        except KeyboardInterrupt:
            print("Stopping recording and transcription.")

            # Terminate the processes
            process1.terminate()
            process2.terminate()

            # Wait for processes to join
            process1.join()
            process2.join()

    def end_call(self):
        self.inCall = False

    def record_audio(self, device_index, temp_filename):
        audio = pyaudio.PyAudio()
        
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True, frames_per_buffer=CHUNK, input_device_index=device_index)

        frames = []
        print(f"Recording from input {device_index}...")

        while True:
            for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)

            # Save audio to the temporary WAV file
            self.save_audio(frames, temp_filename)

            # Transcribe the recorded audio
            self.transcribe_audio(temp_filename)

            frames.clear()  # Clear frames for the next recording

    def transcribe_audio(self, filename):
        model = WhisperModel("medium.en", device="cuda", compute_type="auto", cpu_threads=0)
        print(f"Transcribing {filename}...")
        segments, info = model.transcribe(filename)
        text = ''.join(segment.text for segment in segments)
        print(f"Transcription for {filename}: {text}")

    def save_audio(self, frames, filename):
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(pyaudio.PyAudio().get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))