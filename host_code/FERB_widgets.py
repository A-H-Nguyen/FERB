import tkinter as tk

from tkinter import ttk

class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def get_num_children(self) -> int:
        return len(self.scrollable_frame.grid_slaves())
    
    def add_frame(self, frame):
        frame_num = self.get_num_children() + 1
        frame.grid(row= frame_num, column=0, sticky="ew")

        print(f"Added frame number {frame_num}")

    def get_frame(self, frame_id):
        children = self.scrollable_frame.winfo_children()
        for child in children:
            if hasattr(child, 'id') and child.id == frame_id:
                return child

    def remove_frame_by_id(self, frame_id):
        child = self.get_frame(frame_id)
        child.pack_forget()
        child.destroy()


class ClientFrame(tk.Frame):
    def __init__(self, container, client_id, client_name:str, callback=None, *args, **kwargs):
        super().__init__(container, *args, **kwargs)

        self.id = client_id

        self.client_name = tk.Label(self, text=client_name)
        self.person_count_label = tk.Label(self, text="\nPerson Count:\n")
        self.person_count_data = tk.Label(self, text="PLACEHOLDER")

        if not callback:
            self.display_btn = tk.Button(self, text="Display", command=self.dummy)
        else:
            self.display_btn = tk.Button(self, text="Display", command=callback)

        self.client_name.grid(row=0, column=0, sticky="ew")
        self.person_count_label.grid(row=1, column=0, sticky="ew")
        self.person_count_data.grid(row=3, column=0, sticky="ew")
        self.display_btn.grid(row=0, column=1, columnspan=3, sticky="news")

    def dummy(self):
        pass
