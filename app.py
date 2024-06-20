import threading
import tkinter as tk

from model.model import Model
from view.view import View

# Call Managers
from call_managers.stub.call_stub import CallStub
from call_managers.whisper_call_manager import WhisperCallManager

# Chat Processors
from chat_processors.stub.emotion_stub import EmotionStub
from chat_processors.text2emotion_chat_processor import Text2EmotionChatProcessor

class Controller:
    def __init__(self):
        self.root = tk.Tk()
        self.view = View(self.root, self)
        self.model = Model(self.view)
        self.call_manager = None

        #self.emotion_processor = EmotionStub(lambda emotion: self.model.set_emotion(emotion)) # Stub
        self.emotion_processor = Text2EmotionChatProcessor(lambda emotion: self.model.set_emotion(emotion))
        emotion_processor_callback = self.emotion_processor.get_callback()
        self.model.set_call_log_observer(emotion_processor_callback)
        
        # Configure the grid to expand with the window
        for i in range(5):
            self.root.grid_rowconfigure(i, weight=1)
            self.root.grid_columnconfigure(i, weight=1)

    def run(self):
        self.root.title("Sales Helper")
        self.root.mainloop()

    def handle_start_call(self):
        #self.call_manager = CallStub(lambda call_log: self.model.add_call_log(call_log)) # To Replace
        self.call_manager = WhisperCallManager(lambda call_log: self.model.add_call_log(call_log))
        self.call_manager_thread = threading.Thread(target=self.call_manager.start_call)
        self.call_manager_thread.start()

    def handle_end_call(self):
        if self.call_manager is not None:
            self.call_manager.end_call()
            self.call_manager_thread.join()
            self.call_manager = None
        
if __name__ == "__main__":
    app = Controller()
    app.run()