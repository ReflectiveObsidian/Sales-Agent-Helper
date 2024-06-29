import io
import os
import speech_recognition as sr
import nltk
from nltk.tokenize import sent_tokenize
from threading import Thread

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from datetime import datetime, timedelta
from queue import Queue
from tempfile import NamedTemporaryFile
from time import sleep
from sys import platform
from faster_whisper import WhisperModel

from call_managers.call_manager import CallManager
from model.call_log import CallLog


class WhisperCallManager(CallManager):
    def __init__(self, add_call_log_callback, salesperson_device_id_callback, customer_device_id_callback):
        self.add_call_log_callback = add_call_log_callback
        self.salesperson_device_id_callback = salesperson_device_id_callback
        self.customer_device_id_callback = customer_device_id_callback
        self.inCall = False

        model = "medium.en"
        device = "cuda"
        compute_type = "auto"
        threads = 0
        energy_threshold = 1000
        self.record_timeout = 2
        self.phrase_timeout = 2

        self.phrase_time = [None, None]
        self.last_sample = [bytes(), bytes()]
        self.data_queues = [Queue(), Queue()]
        self.recorder = [sr.Recognizer(), sr.Recognizer()]
        for r in self.recorder:
            r.energy_threshold = energy_threshold
            r.dynamic_energy_threshold = False
        
        nltk.download('punkt')
        self.audio_model = WhisperModel(model, device=device, compute_type=compute_type, cpu_threads=threads)

        self.temp_files = [NamedTemporaryFile().name, NamedTemporaryFile().name]
        self.transcriptions = [[''], ['']]

    def record_callback(self, index):
        def callback(_, audio: sr.AudioData):
            """
            Threaded callback function to receive audio data when recordings finish.
            audio: An AudioData containing the recorded bytes.
            """
            # Grab the raw bytes and push it into the thread safe queue.
            data = audio.get_raw_data()
            self.data_queues[index].put(data)
        
        return callback

    def record_and_transcribe(self, index):
        while self.inCall:
            now = datetime.utcnow()
            # Pull raw recorded audio from the queue.
            if not self.data_queues[index].empty():
                phrase_complete = False
                # If enough time has passed between recordings, consider the phrase complete.
                # Clear the current working audio buffer to start over with the new data.
                if self.phrase_time[index] and now - self.phrase_time[index] > timedelta(seconds=self.phrase_timeout):
                    self.last_sample[index] = bytes()
                    phrase_complete = True
                # This is the last time we received new audio data from the queue.
                self.phrase_time[index] = now

                # Concatenate our current audio data with the latest audio data.
                while not self.data_queues[index].empty():
                    data = self.data_queues[index].get()
                    self.last_sample[index] += data

                # Use AudioData to convert the raw data to wav data.
                audio_data = sr.AudioData(self.last_sample[index], self.sources[index].SAMPLE_RATE, self.sources[index].SAMPLE_WIDTH)
                wav_data = io.BytesIO(audio_data.get_wav_data())

                # Write wav data to the temporary file as bytes.
                with open(self.temp_files[index], 'w+b') as f:
                    f.write(wav_data.read())

                # Read the transcription.
                text = ""
                segments, info = self.audio_model.transcribe(self.temp_files[index])
                for segment in segments:
                    text += segment.text

                # If we detected a pause between recordings, add a new item to our transcription.
                # Otherwise edit the existing one.
                if phrase_complete:
                    self.transcriptions[index].append(text)
                else:
                    self.transcriptions[index][-1] = text

                # Create call log with device information
                device_name = f"device {index+1}"
                call_log = CallLog(now, device_name, self.transcriptions[index][-1])
                self.add_call_log_callback(call_log)

            sleep(2)

    def start_call(self):
        self.inCall = True

        self.sources = [sr.Microphone(sample_rate=16000, device_index=self.salesperson_device_id_callback()),
                        sr.Microphone(sample_rate=16000, device_index=self.customer_device_id_callback())]
        
        for source in self.sources:
            with source:
                try:
                    self.recorder[self.sources.index(source)].adjust_for_ambient_noise(source, duration=1)
                except Exception as e:
                    print(f"Error adjusting for ambient noise: {e}")
                    self.controller.handle_end_call()
                    return
        # Start threads for each device
        threads = []
        for i in range(2):
            # Start recording and transcription in separate threads
            thread = Thread(target=self.record_and_transcribe, args=(i,))
            thread.start()
            threads.append(thread)
            
            # Listen in background for each device
            self.recorder[i].listen_in_background(self.sources[i], self.record_callback(i), phrase_time_limit=self.record_timeout)

        # Wait for threads to finish
        for thread in threads:
            thread.join()

    def end_call(self):
        self.inCall = False