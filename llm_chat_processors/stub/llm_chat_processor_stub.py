from time import sleep
from typing import List
import threading

from llm_chat_processors.llm_chat_processor import LLMChatProcessor
from llm_chat_processors.prompt_type import PromptType
from model.call_log import CallLog

# Runs on calling set_prompt, and whenever the chat log is updated, until stop is called
class LLMChatProcessorStub(LLMChatProcessor):
    
    def __init__(self):
        self.active = False
        self.enabled = False
        # Load LLM into memory here

    def set_prompt(self, type: PromptType, model, model_callback, enabled):
        self.model_callback = model_callback
        self.type = type
        self.chat_log = model.get_call_logs()
        self.enabled = enabled

    def chatlog_update_listener(self, model):
        self.chat_log = model.get_call_logs()
        if self.enabled:
            self.run()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def run(self):
        if not self.active:
            self.active = True
            # Prompt LLM and get response here
            # Choose prompt based on self.type
            sleep(5)
            self.model_callback("Hello")
            self.active = False

