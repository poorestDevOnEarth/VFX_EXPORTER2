import os
import sys
from Rinter import Rinter
from vfx_item import *
from pathlib import Path
import shutil
import re
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import *
from time import sleep
from sys import platform


def timecode_to_frames(timecode, frame_rate, drop):
    if int(timecode[9:]) > frame_rate:
        raise ValueError('SMPTE timecode to frame rate mismatch.', timecode, frame_rate)

    seconds = int(timecode[6:8])
    hours = int(timecode[:2])
    minutes = int(timecode[3:5])
    frames = int(timecode[9:])

    totalMinutes = int(60 * hours + minutes)

    # Drop frame calculation using the Duncan/Heidelberger method.
    if drop:

        dropFrames = int(round(frame_rate * 0.066666))
        timeBase = int(round(frame_rate))

        hourFrames = int(timeBase * 60 * 60)
        minuteFrames = int(timeBase * 60)

        frm = int(((hourFrames * hours) + (minuteFrames * minutes) + (timeBase * seconds) + frames) - (
                dropFrames * (totalMinutes - (totalMinutes // 10))))

        # Non drop frame calculation.
    else:

        frame_rate = int(round(frame_rate))
        frm = int((totalMinutes * 60 + seconds) * frame_rate + frames)

    return frm

def open_directory_dialog():
    timeline_object.deliver_path = filedialog.askdirectory()
    path_variable.set(timeline_object.deliver_path)  # Update the StringVar
    print(timeline_object.deliver_path)
    root.focus_force()

def frames_to_timecode(frame_rate, drop, total_frames):
    total_frames = abs(total_frames)
    # Drop frame calculation via Duncan/Heidelberger method.
    if drop:
        spacer = ':'
        spacer2 = ';'

        dropFrames = int(round(frame_rate * .066666))
        framesPerHour = int(round(frame_rate * 3600))
        framesPer24Hours = framesPerHour * 24
        framesPer10Minutes = int(round(frame_rate * 600))
        framesPerMinute = int(round(frame_rate) * 60 - dropFrames)

        total_frames = total_frames % framesPer24Hours

        d = total_frames // framesPer10Minutes
        m = total_frames % framesPer10Minutes

        if m > dropFrames:
            total_frames = total_frames + (dropFrames * 9 * d) + dropFrames * ((m - dropFrames) // framesPerMinute)

        else:
            total_frames = total_frames + dropFrames * 9 * d

        frRound = int(round(frame_rate))
        hr = int(total_frames // frRound // 60 // 60)
        mn = int((total_frames // frRound // 60) % 60)
        sc = int((total_frames // frRound) % 60)
        fr = int(total_frames % frRound)

    # Non drop frame calculation.
    else:

        frame_rate = int(round(frame_rate))
        spacer = ':'
        spacer2 = spacer

        frHour = frame_rate * 3600
        frMin = frame_rate * 60

        hr = int(total_frames // frHour)
        mn = int((total_frames - hr * frHour) // frMin)
        sc = int((total_frames - hr * frHour - mn * frMin) // frame_rate)
        fr = int(round(total_frames - hr * frHour - mn * frMin - sc * frame_rate))

    # Return SMPTE timecode string.
    return (
            str(hr).zfill(2) + spacer +
            str(mn).zfill(2) + spacer +
            str(sc).zfill(2) + spacer2 +
            str(fr).zfill(2)
    )

    #return "%02d:%02d:%02d%s%02d" % (fr, mn, sc, smpte_token, fr)

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

def update_naming_convention_var():
    selected_order = selected_listbox.get(0, tk.END)
    naming_convention_var.set("_".join(selected_order))

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

def update_selected_listbox(event):
    # Get the selected index in the selected_listbox
    selected_index = selected_listbox.curselection()

if __name__ == '__main__':

    if platform == "win32":
        separator = "\\"
    elif platform == "darwin":
        separator = "/"

    rinter = Rinter()
    folder_path = "/Users/martenmeiburg/Desktop/fail"
    rinter.start()

    #Get Markers from resolve
    timeline_object = TIMELINE_OBJECT()
    timeline_object.start_frame = rinter.timeline.GetStartFrame()
    timeline_object.drop = rinter.timeline.GetSetting('timelineDropFrameTimecode')
    timeline_object.fps = rinter.timeline.GetSetting('timelineFrameRate')
    timeline_markers = rinter.timeline.GetMarkers()

    # disable all tracks
    for i in range(rinter.timeline.GetTrackCount("video")):
        rinter.timeline.SetTrackEnable("video", i+1, False)

    # go to markers and receive plate infos
    rinter.resolve.OpenPage("edit")
    for t in timeline_markers:
        vfx_object = VFX_OBJECT()
        # go through every layer
        for layer in range(3):
            layer = layer + 1
            if layer == 1:
                rinter.timeline.SetTrackEnable("video", 3, False)
                rinter.timeline.SetTrackEnable("video", 2, False)
                rinter.timeline.SetTrackEnable("video", 1, True)
            if layer == 2:
                rinter.timeline.SetTrackEnable("video", 3, False)
                rinter.timeline.SetTrackEnable("video", 2, True)
                rinter.timeline.SetTrackEnable("video", 1, False)
            if layer == 3:
                rinter.timeline.SetTrackEnable("video", 3, True)
                rinter.timeline.SetTrackEnable("video", 2, False)
                rinter.timeline.SetTrackEnable("video", 1, False)

            tc = frames_to_timecode(timeline_object.fps, 0, timeline_object.start_frame + t)
            plate_object = PLATE()
            plate_object.start_frame = timeline_object.start_frame + t
            rinter.timeline.SetCurrentTimecode(tc)
            clip = rinter.timeline.GetCurrentVideoItem()
            if clip is None:
                continue

            mpi = clip.GetMediaPoolItem()

            plate_object.end_frame = clip.GetEnd()
            plate_object.path = mpi.GetClipProperty('File Path')
            plate_object.filename = mpi.GetClipProperty('File Name')
            plate_object.layer = layer
            vfx_object.plates.append(plate_object)

        shot_scnen_name = (timeline_markers[t]['name']).split('_')
        vfx_object.shotname = shot_scnen_name[0]
        head, sep, tail = shot_scnen_name[1].partition(' ')         #cut everthing after space
        vfx_object.scene_name = head
        timeline_object.vfx_objects.append(vfx_object)

    #output tkinter
    root = tk.Tk()
    root.title("VFX Export 3000")
    button_frame = tk.Frame(root)
    button_frame.pack(side=tk.TOP, anchor="w", padx=20, pady=20)

    # Frame for naming convention
    naming_frame = tk.Frame(root)
    naming_frame.pack(side=tk.TOP, pady=10)
    # Frame for summaries
    summary_frame = tk.Frame(root)
    summary_frame.pack(side=tk.TOP, pady=10)


    # available naming convention array
    available_vars = ["company", "production", "shot", "scene", "plate", "version", "filename"]
    label_var = tk.StringVar()

    # go through collected Timeline VFXObjects and store in summary
    for vfx in timeline_object.vfx_objects:
        timeline_object.summary = timeline_object.summary + '\n' + 'VFX:' + (vfx.shotname + '_' + vfx.scene_name)
        for plate in vfx.plates:
            timeline_object.summary = timeline_object.summary + '\n\t' "Plate: " + plate.filename + "Layer: " + str(plate.layer)


    # Set Deliver Folder Button
    button = tk.Button(button_frame, text="Set Deliver Folder", command=open_directory_dialog, justify=tk.LEFT)
    button.pack(side=tk.LEFT)

    # Deliver Path
    path_variable = tk.StringVar()
    path_variable.set("Deliver Path not set")
    path = tk.Label(button_frame, textvariable=path_variable, anchor="w")
    path.pack(side=tk.LEFT, padx=20, pady=0)



    # Label for VFX Shots summary (first label)
    label_var.set(timeline_object.summary)
    selected_label_1 = tk.Label(summary_frame, textvariable=label_var, anchor="nw", justify=tk.LEFT)
    selected_label_1.pack(side=tk.LEFT, padx=20, anchor=tk.NW)

    # Label for VFX Shots summary (second label)
    label_var.set(timeline_object.summary)
    selected_label_2 = tk.Label(summary_frame, textvariable=label_var, anchor="nw", justify=tk.LEFT)
    selected_label_2.pack(side=tk.LEFT, padx=20, anchor=tk.NW)

    # Generated naming convention string
    naming_convention_var = tk.StringVar()
    naming_convention_entry = tk.Label(naming_frame, textvariable=naming_convention_var, anchor="w")
    naming_convention_entry.pack(side=tk.LEFT, padx=20, anchor=tk.NW)

    # Replace ReorderableListbox with EditableListbox
    available_listbox = EditableListbox(root, selectmode=tk.SINGLE, justify=tk.LEFT)
    available_listbox.pack(side=tk.LEFT, padx=20, pady=10, anchor=tk.NW)

    selected_listbox = EditableListbox(root, selectmode=tk.SINGLE)
    selected_listbox.pack(side=tk.LEFT, padx=10, pady=10, anchor=tk.NW)

    for var in available_vars:
        available_listbox.insert(tk.END, var)
    # Create and pack the move_left_button
    move_left_button = tk.Button(root, text="<", command=move_left)
    move_left_button.pack(side=tk.TOP, padx=5)

    # Create and pack the move_right_button
    move_right_button = tk.Button(root, text=">", command=move_right)
    move_right_button.pack(side=tk.TOP, padx=5)


    root.mainloop()

    folder = os.path.expanduser(folder_path)
    print("sick")