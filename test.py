import tkinter as tk


class ReorderableListbox(tk.Listbox):
    def __init__(self, master, **kw):
        kw['selectmode'] = tk.EXTENDED
        tk.Listbox.__init__(self, master, kw)
        self.bind('<Button-1>', self.setCurrent)
        self.bind('<Control-1>', self.toggleSelection)
        self.bind('<B1-Motion>', self.shiftSelection)
        self.bind('<Leave>', self.onLeave)
        self.bind('<Enter>', self.onEnter)
        self.selectionClicked = False
        self.left = False
        self.unlockShifting()
        self.ctrlClicked = False

    def orderChangedEventHandler(self):
        pass

    def onLeave(self, event):
        if self.selectionClicked:
            self.left = True
            return 'break'

    def onEnter(self, event):
        self.left = False

    def setCurrent(self, event):
        self.ctrlClicked = False
        i = self.nearest(event.y)
        self.selectionClicked = self.selection_includes(i)
        if (self.selectionClicked):
            return 'break'

    def toggleSelection(self, event):
        self.ctrlClicked = True

    def moveElement(self, source, target):
        if not self.ctrlClicked:
            element = self.get(source)
            self.delete(source)
            self.insert(target, element)

    def unlockShifting(self):
        self.shifting = False

    def lockShifting(self):
        self.shifting = True

    def shiftSelection(self, event):
        if self.ctrlClicked:
            return
        selection = self.curselection()
        if not self.selectionClicked or len(selection) == 0:
            return

        selectionRange = range(min(selection), max(selection))
        currentIndex = self.nearest(event.y)

        if self.shifting:
            return 'break'

        lineHeight = 15
        bottomY = self.winfo_height()
        if event.y >= bottomY - lineHeight:
            self.lockShifting()
            self.see(self.nearest(bottomY - lineHeight) + 1)
            self.master.after(500, self.unlockShifting)
        if event.y <= lineHeight:
            self.lockShifting()
            self.see(self.nearest(lineHeight) - 1)
            self.master.after(500, self.unlockShifting)

        if currentIndex < min(selection):
            self.lockShifting()
            notInSelectionIndex = 0
            for i in selectionRange[::-1]:
                if not self.selection_includes(i):
                    self.moveElement(i, max(selection) - notInSelectionIndex)
                    notInSelectionIndex += 1
            currentIndex = min(selection) - 1
            self.moveElement(currentIndex, currentIndex + len(selection))
            self.orderChangedEventHandler()
        elif currentIndex > max(selection):
            self.lockShifting()
            notInSelectionIndex = 0
            for i in selectionRange:
                if not self.selection_includes(i):
                    self.moveElement(i, min(selection) + notInSelectionIndex)
                    notInSelectionIndex += 1
            currentIndex = max(selection) + 1
            self.moveElement(currentIndex, currentIndex - len(selection))
            self.orderChangedEventHandler()
        self.unlockShifting()
        return 'break'

def move_right():
    selected_indices = available_listbox.curselection()
    for idx in selected_indices:
        selected_listbox.insert(tk.END, available_listbox.get(idx))
        available_listbox.delete(idx)
    update_naming_convention_var()

def move_left():
    selected_indices = selected_listbox.curselection()
    for idx in selected_indices:
        available_listbox.insert(tk.END, selected_listbox.get(idx))
        selected_listbox.delete(idx)
    update_naming_convention_var()

def update_naming_convention_var(*args):
    selected_order = selected_listbox.get(0, tk.END)
    naming_convention_var.set("_".join(selected_order))


root = tk.Tk()
root.title("Generate Naming Convention")

available_vars = ["company", "production", "shot", "scene", "plate", "version", "filename"]

available_listbox = ReorderableListbox(root, selectmode=tk.SINGLE)
available_listbox.pack(side=tk.LEFT, padx=10, pady=10)

selected_listbox = ReorderableListbox(root, selectmode=tk.SINGLE)
selected_listbox.pack(side=tk.LEFT, padx=10, pady=10)

for var in available_vars:
    available_listbox.insert(tk.END, var)


move_right_button = tk.Button(root, text=">", command=move_right)
move_right_button.pack(side=tk.BOTTOM, padx=5)
move_left_button = tk.Button(root, text="<", command=move_left)
move_left_button.pack(padx=5)

naming_convention_label = tk.Label(root, text="Naming Convention:")
naming_convention_label.pack(pady=10)

naming_convention_var = tk.StringVar()
naming_convention_entry = tk.Entry(root, textvariable=naming_convention_var, state="readonly")
naming_convention_entry.pack(pady=10, padx=10)

root.mainloop()
