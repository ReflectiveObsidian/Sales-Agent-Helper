import tkinter as tk

from tkinter import scrolledtext

class View:
    def __init__(self, master, controller):
        master.geometry("800x800")
        self.controller = controller

        self.call_logs = scrolledtext.ScrolledText(master, bg='white')
        self.call_logs.pack(padx=10, pady=10)

        self.emotion_label = tk.Label(master, text="Emotion:")
        self.emotion_label.pack(padx=10, pady=10)

        self.emotion = tk.Label(master, text="waiting...", bg='white')
        self.emotion.pack()

        self.personalities_label = tk.Label(master, text="Personalities:")
        self.personalities_label.pack(padx=10, pady=10)

        self.personalities = tk.Label(master, bg='white', text="waiting...")
        self.personalities.pack(padx=10, pady=10)

        self.warnings_label = tk.Label(master, text="Warnings:")
        self.warnings_label.pack(padx=10, pady=10)

        self.warnings = tk.Label(master, bg='white', text="waiting...")
        self.warnings.pack(padx=10, pady=10)
        
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(padx=10, pady=10)

        self.button = tk.Button(self.button_frame, bg='#99FF99', text="Start Call", command=self.controller.handle_start_call)
        self.button.grid(row=0, column=0, padx=10, pady=10)

        self.end_button = tk.Button(self.button_frame, bg='#FF9999', text="End Call", command=self.controller.handle_end_call)
        self.end_button.grid(row=0, column=1, padx=10, pady=10)


    def update(self, model):
        self.call_logs.delete('1.0', tk.END)
        self.call_logs.insert('insert', self.formatted_call_logs(model.get_call_logs()))
        self.call_logs.see("end")
        self.emotion.config(text=model.get_emotion()[0])
        self.personalities.config(text=model.get_personalities())
        self.warnings.config(text=model.get_warnings())

    def formatted_call_logs(self, call_logs):
        return "\n\n".join([str(call_log) for call_log in call_logs])