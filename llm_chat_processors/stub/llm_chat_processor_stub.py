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
        # Load LLM into memory here -----------------------------------

        # -------------------------------------------------------------

    def set_prompt(self, type: PromptType, chatlog, model_callback, enabled):
        self.model_callback = model_callback # Call this function to update the model with your response
        self.type = type # Use this in run() to determine what prompt to give to the llm
        self.chat_log = chatlog # List of ChatLog
        self.enabled = enabled # If enabled, llm will be prompted on chatlog update

    def chatlog_update_listener(self, chatlog):
        self.chat_log = chatlog
        if self.enabled:
            self.run()

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def run(self):
        if not self.active:
            self.active = True
            model_callback = self.model_callback
            type = self.type
            chat_log = self.chat_log
            enabled = self.enabled

            # PROMPT LLM HERE -----------------------------------
            # Choose prompt based on self.type
            sleep(5)
            if type == PromptType.WARNINGS:
                model_callback("Hello Warning")
            elif type == PromptType.TODO:
                model_callback("Hello Todo")
            # --------------------------------------------------

            self.active = False

