import tkinter as tk

from tkinter import scrolledtext

from view.call_done_view import CallDoneView

class View:
    def __init__(self, master, controller):
        master.geometry("800x800")
        self.controller = controller
        self.frame = tk.Frame(master)
        self.call_done_view = CallDoneView(master, back_view=self)

        self.frame.pack()

        tk.Label(self.frame, text='Call Dashboard', font=("Helvetica", 16)).pack(padx=10, pady=10)

        self.call_logs = scrolledtext.ScrolledText(self.frame, bg='white')
        self.call_logs.pack(padx=10, pady=10)

        self.emotion_label = tk.Label(self.frame, text="Emotion:")
        self.emotion_label.pack(padx=10, pady=10)

        self.emotion = tk.Label(self.frame, text="waiting...", bg='white')
        self.emotion.pack()

        self.personalities_label = tk.Label(self.frame, text="Personalities:")
        self.personalities_label.pack(padx=10, pady=10)

        self.personalities = tk.Label(self.frame, bg='white', text="waiting...")
        self.personalities.pack(padx=10, pady=10)

        self.warnings_label = tk.Label(self.frame, text="Warnings:")
        self.warnings_label.pack(padx=10, pady=10)

        self.warnings = tk.Label(self.frame, bg='white', text="waiting...")
        self.warnings.pack(padx=10, pady=10)
        
        self.button_frame = tk.Frame(self.frame)
        self.button_frame.pack(padx=10, pady=10)

        self.start_button = tk.Button(self.button_frame, bg='#99FF99', text="Start New Call", command=self.handle_start_call)
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.end_button = tk.Button(self.button_frame, bg='#FF9999', text="End Call and show To-Do", state="disabled", command=self.handle_end_call)
        self.end_button.grid(row=0, column=1, padx=10, pady=10)

    def handle_start_call(self):
        self.controller.handle_start_call()
        self.start_button.config(state="disabled")
        self.end_button.config(state="normal")
        
    def handle_end_call(self):
        self.start_button.config(state="normal")
        self.go_to_call_done_view()
        self.controller.handle_end_call()

    def update(self, model):
        self.call_logs.delete('1.0', tk.END)
        self.call_logs.insert('insert', self.formatted_call_logs(model.get_call_logs()))
        self.call_logs.see("end")
        self.emotion.config(text=model.get_emotion()[0])
        self.personalities.config(text=model.get_personalities())
        self.warnings.config(text=model.get_warnings())

        self.call_done_view.update(model)

    def formatted_call_logs(self, call_logs):
        return "\n\n".join([str(call_log) for call_log in call_logs])
    
    def start_page(self):
        self.frame.pack()
    
    def go_to_call_done_view(self):
        self.frame.pack_forget()
        self.call_done_view.start_page()