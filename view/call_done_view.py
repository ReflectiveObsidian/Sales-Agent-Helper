import tkinter as tk

from tkinter import scrolledtext

class CallDoneView:
    def __init__(self, master=None, back_view=None):
        self.master = master
        self.back_view = back_view
        self.frame = tk.Frame(self.master)

        tk.Label(self.frame, text='End-of-call summary', font=("Helvetica", 16)).pack(padx=10, pady=10)

        self.call_logs = scrolledtext.ScrolledText(self.frame, bg='white', height = 20)
        self.call_logs.pack(padx=10, pady=10)

        self.todo_list = scrolledtext.ScrolledText(self.frame, bg='white', height = 10)
        self.todo_list.pack(padx=10, pady=10)

        tk.Button(self.frame, text='Go back', bg='#99FF99', command=self.go_back).pack()

    def start_page(self):
        self.frame.pack()

    def go_back(self):
        self.frame.pack_forget()
        self.back_view.start_page()

    def update(self, model):
        self.call_logs.delete('1.0', tk.END)
        self.call_logs.insert('insert', self.formatted_call_logs(model.get_call_logs()))
        self.call_logs.see("end")

        self.todo_list.delete('1.0', tk.END)
        self.todo_list.insert('insert', model.get_todo_list())

    def formatted_call_logs(self, call_logs):
        return "\n\n".join([str(call_log) for call_log in call_logs])
