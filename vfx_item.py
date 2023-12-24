import tkinter as tk
class VFX_OBJECT:
    def __init__(self):
        self.path = ""
        self.filename = ""
        self.shotname = ""
        self.start_frame = ""
        self.end_frame = ""
        self.scene_name = ""
        self.plates = []

class TIMELINE_OBJECT:
    def __init__(self):
        self.deliver_path = "Path not set"
        self.start_frame = ""
        self.company = ""
        self.version = ""
        self.production = ""
        self.drop = 0
        self.fps = 0.0
        self.vfx_objects = []
        self.tracks = 0
        self.summary = ""


class PLATE:
    def __init__(self):
        self.path = ""
        self.filename = ""
        self.start_frame = ""
        self.end_frame = ""
        self.layer = 0



class EditableListbox(tk.Listbox):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.edit_entry = None
        self.bind("<Double-Button-1>", self.start_editing)

    def start_editing(self, event):
        selected_index = self.curselection()
        if selected_index:
            index = selected_index[0]
            item = self.get(index)
            self.edit_entry = Entry(self, bd=1, relief="solid", justify=tk.LEFT)
            self.edit_entry.insert(0, item)
            self.edit_entry.grid(row=index, column=0, sticky="nsew")
            self.edit_entry.focus_set()
            self.edit_entry.bind("<Return>", lambda event, idx=index: self.stop_editing(idx))

    def stop_editing(self, index):
        edited_text = self.edit_entry.get()
        self.edit_entry.destroy()
        self.edit_entry = None
        self.delete(index)
        self.insert(index, edited_text)
        update_naming_convention_var()



