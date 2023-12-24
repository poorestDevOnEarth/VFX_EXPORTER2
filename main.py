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


def update_naming_convention_var(*args):
    def update_naming_convention_var(*args):
        naming_convention = ""

        company = company_var.get()
        production = production_var.get()
        shot = shot_var.get()
        scene = scene_var.get()
        plate = plate_var.get()
        version = version_var.get()

        if company:
            naming_convention += company
        if production:
            if naming_convention:
                naming_convention += "_"
            naming_convention += production
        if shot:
            if naming_convention:
                naming_convention += "_"
            naming_convention += shot
        if scene:
            if naming_convention:
                naming_convention += "_"
            naming_convention += scene
        if plate:
            if naming_convention:
                naming_convention += "_"
            naming_convention += plate
        if version:
            if naming_convention:
                naming_convention += "_"
            naming_convention += version
        if filename:
            if naming_convention:
                naming_convention += "_"
            naming_convention += filename


        naming_convention_var.set(naming_convention)

    naming_convention_var.set(f"{company_var.get()}_{production_var.get()}_{shot_var.get()}_{scene_var.get()}_{filename_var.get()}_{plate_var.get()}_{version_var.get()}")

def generate_render_qeue(layer, folder):
    rinter.resolve.OpenPage("edit")
    if layer == 1:
        VFX_OBJECT.plate = rinter.timeline.GetTrackName("video", 1)
        rinter.timeline.SetTrackEnable("video", 2, False)
        rinter.timeline.SetTrackEnable("video", 1, True)
    if layer == 2:
        VFX_OBJECT.plate = rinter.timeline.GetTrackName("video", 2)
        rinter.timeline.SetTrackEnable("video", 2, True)
        rinter.timeline.SetTrackEnable("video", 1, False)
    if layer > 2:
        VFX_OBJECT.plate = "Element"

    for t in timeline_markers:
        # go to marker
        tc = frames_to_timecode(fps, 0, start_frame + t)
        VFX_OBJECT.start_frame = start_frame + t
        rinter.timeline.SetCurrentTimecode(tc)

        clip = rinter.timeline.GetCurrentVideoItem()

        mpi = clip.GetMediaPoolItem()
        mediapool_item = clip.GetMediaPoolItem()
        VFX_OBJECT.end_frame = clip.GetEnd()

        VFX_OBJECT.path = mpi.GetClipProperty('File Path')
        VFX_OBJECT.filename = os.path.splitext(os.path.basename(VFX_OBJECT.path))[0]
        shot_scnen_name = (timeline_markers[t]['name']).split('_')


        VFX_OBJECT.shotname = shot_scnen_name[0]
        VFX_OBJECT.scene_name = shot_scnen_name[1]
        #vfx_object.shotname = re.sub('[^A-Za-z0-9]+', '', vfx_object.shotname)  # remove specialchars
        #vfx_object.scene_name = vfx_object.scene_name.strip()
        #print(vfx_object)
        #vfx_object.filename = re.sub('[^A-Za-z0-9]+', '', vfx_object.filename)  # remove specialchars

        ################### ENTER NAMING HERE ##########################
        version = "v001"
        project_name = "SUR"
        company_name = "UFA"
        custom_filename = f"{company_name}_{project_name}_{VFX_OBJECT.shotname}_{VFX_OBJECT.scene_name}_{VFX_OBJECT.plate}_{version}"
        custom_subfolder_filename = custom_filename
        custom_target_dir = folder + f"{separator}{custom_filename}"
        #custom_target_dir = folder + f"{separator}{vfx_object.scene_name}{separator}{custom_filename}"

        ################### ENTER NAMING HERE ##########################


        project = rinter.project.SetRenderSettings({'SelectAllFrames': 0,
                                                    "MarkIn": VFX_OBJECT.start_frame,
                                                    "MarkOut": VFX_OBJECT.end_frame - 1,
                                                    "TargetDir": custom_target_dir,
                                                    "CustomName": custom_filename,
                                                    "ExportVideo": 1,
                                                    "ExportAudio": 0,
                                                    })
        rinter.project.AddRenderJob()

        # print values for debugging
        print(f"shot_name: {VFX_OBJECT.shotname}")
        print(f"scene_name: {VFX_OBJECT.scene_name}")
        print(f"path: {VFX_OBJECT.path}")
        print(f"filename: {VFX_OBJECT.filename}")
        print(f"startframe: {VFX_OBJECT.start_frame}")
        print(f"endframe: {VFX_OBJECT.end_frame}")

def open_directory_dialog():
    TIMELINE_OBJECT.deliver_path = filedialog.askdirectory()
    path_variable.set(TIMELINE_OBJECT.deliver_path)  # Update the StringVar
    print(TIMELINE_OBJECT.deliver_path)
    root.focus_force()

def start_render_queue():
    folder = os.path.expanduser(f"{TIMELINE_OBJECT.deliver_path}{separator}VFX_Package")

    generate_render_qeue(1, folder)  # Pass 'folder' as an argument
    messagebox.showinfo("showinfo", "Rendering queue started. Press OK to generate layer 2 queue")

    generate_render_qeue(2, folder)  # Pass 'folder' as an argument

if __name__ == '__main__':

    if platform == "win32":
        separator = "\\"
    elif platform == "darwin":
        separator = "/"

    rinter = Rinter()

    #folder_path = filedialog.askdirectory()
    rinter.start()
    vfx_object = VFX_OBJECT()
    timeline_object = TIMELINE_OBJECT()
    start_frame = rinter.timeline.GetStartFrame()
    timeline_markers = rinter.timeline.GetMarkers()
    fps = rinter.timeline.GetSetting('timelineFrameRate')
    drop = rinter.timeline.GetSetting('timelineDropFrameTimecode')
    filename = "A004C008"
    root = tk.Tk()
    root.title("VFX_Flow_3000")

    input_frame = tk.Frame(root)
    input_frame.pack(padx=20, pady=20, anchor="w")

    company_label = tk.Label(input_frame, text="Production Company:", anchor="w")
    company_label.pack(side="top", fill="x")
    company_var = tk.StringVar()
    company_var.trace("w", update_naming_convention_var)  # Call update_naming_convention_var when company_var changes
    company_entry = tk.Entry(input_frame, textvariable=company_var)
    company_entry.pack(side="top", fill="x")

    production_label = tk.Label(input_frame, text="Production:", anchor="w")
    production_label.pack(side="top", fill="x")
    production_var = tk.StringVar()
    production_var.trace("w", update_naming_convention_var)  # Call update_naming_convention_var when production_var changes
    production_entry = tk.Entry(input_frame, textvariable=production_var)
    production_entry.pack(side="top", fill="x")

    shot_label = tk.Label(input_frame, text="Shot:", anchor="w")
    shot_label.pack(side="top", fill="x")
    shot_var = tk.StringVar()
    shot_var.trace("w", update_naming_convention_var)  # Call update_naming_convention_var when shot_var changes
    shot_entry = tk.Entry(input_frame, textvariable=shot_var)
    shot_entry.pack(side="top", fill="x")

    filename_label = tk.Label(input_frame, text="Filename:", anchor="w")
    filename_label.pack(side="top", fill="x")
    filename_var = tk.StringVar()
    filename_var.trace("w", update_naming_convention_var)  # Call update_naming_convention_var when filename_var changes
    filename_entry = tk.Entry(input_frame, textvariable=filename_var)
    filename_entry.pack(side="top", fill="x")

    scene_label = tk.Label(input_frame, text="Scene:", anchor="w")
    scene_label.pack(side="top", fill="x")
    scene_var = tk.StringVar()
    scene_var.trace("w", update_naming_convention_var)  # Call update_naming_convention_var when scene_var changes
    scene_entry = tk.Entry(input_frame, textvariable=scene_var)
    scene_entry.pack(side="top", fill="x")

    plate_label = tk.Label(input_frame, text="Plate:", anchor="w")
    plate_label.pack(side="top", fill="x")
    plate_var = tk.StringVar()
    plate_var.trace("w", update_naming_convention_var)  # Call update_naming_convention_var when plate_var changes
    plate_entry = tk.Entry(input_frame, textvariable=plate_var)
    plate_entry.pack(side="top", fill="x")

    version_label = tk.Label(input_frame, text="Version:", anchor="w")
    version_label.pack(side="top", fill="x")
    version_var = tk.StringVar()
    version_var.trace("w", update_naming_convention_var)  # Call update_naming_convention_var when version_var changes
    version_entry = tk.Entry(input_frame, textvariable=version_var)
    version_entry.pack(side="top", fill="x")

    button = tk.Button(root, text="Set Deliver Folder", command=open_directory_dialog)
    button.pack(padx=20, pady=(20, 0), anchor="w")

    path_variable = tk.StringVar()
    path_variable.set("Deliver Path not set")  # You can set an initial path here

    path = tk.Label(root, textvariable=path_variable, anchor="w")
    path.pack(padx=20, pady=0, anchor="w")

    naming_convention_label = tk.Label(root, text="Naming Convention:", anchor="w")
    naming_convention_label.pack(padx=20, pady=5, anchor="w")
    naming_convention_var = tk.StringVar()
    naming_convention_entry = tk.Entry(root, textvariable=naming_convention_var)
    naming_convention_entry.pack(padx=20, pady=5, fill="x", anchor="w")

    start_button = tk.Button(root, text="Start", command=start_render_queue)
    start_button.pack(padx=20, pady=20, anchor="w", side="bottom")

    root.mainloop()

    print(f"{timeline_object.deliver_path}{separator}VFX_Package")

    if not os.path.exists(f"{timeline_object.deliver_path}{separator}VFX_Package"):
        os.mkdir(os.path.expanduser(f"{timeline_object.deliver_path}{separator}VFX_Package"))

    folder = os.path.expanduser(f"{timeline_object.deliver_path}{separator}VFX_Package")
    generate_render_qeue(1)

    messagebox.showinfo("showinfo", "Please render created qeue in Davinci. When done press OK to generate layer2 qeue")


    generate_render_qeue(2)
    root.destroy()


