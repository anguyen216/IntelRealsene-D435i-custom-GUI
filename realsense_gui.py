#!/usr/bin/env python3
# realsense_gui.py
# GUI main function; where things come together
import tkinter as tk
from tkinter import messagebox
import numpy as np
import pyrealsense2 as rs
import utils
from datetime import datetime
import cv2
import os

#========== COMMAND FUNCTIONS ==========
def record():
    """
    Collects entered filename, resets setup, and starts recording
    """
    global ENTRY, VISUAL_PRESET, KEER_REC, OUTNAME, OUTFOLDER
    global COLORIZER, SN
    KEEP_REC = True
    fname = ENTRY.get()
    if fname == "":
        messagebox.showinfo(title="Invalid file name",
                            message="you did not enter a file name")
        return
    else:
        # set up stream pipeline
        pipe = rs.pipeline()
        cfg = rs.config()
        cfg.enable_device(SN)
        colorizer = rs.colorizer()
        preset_id, preset_name = utils.get_preset(VISUAL_PRESET)
        # create new folder using date as name if not already exists
        if not os.path.exists(OUTFOLDER):
            os.makedirs(OUTFOLDER)
        # determine output file name
        # naming convention: date\id_setting.bag
        OUTNAME = "_".join([fname, preset_name])
        OUTNAME = OUTFOLDER + "\\" + OUTNAME + ".bag"

        # enable all image format
        cfg.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 30)
        cfg.enable_stream(rs.stream.color, 848, 480, rs.format.rgb8, 30)
        cfg.enable_stream(rs.stream.infrared, 848, 480, rs.format.y8, 30)
        cfg.enable_record_to_file(OUTNAME)

        # start stream
        profile = pipe.start(cfg)
        depth_sensor = profile.get_device().first_depth_sensor()
        depth_sensor.set_option(rs.option.visual_preset, preset_id)
        while KEEP_REC:
            frames = pipe.wait_for_frames()
            dframe = frames.get_depth_frame()
            #f = np.asanyarray(COLORIZER.colorize(dframe).get_data())
            #f = np.asanyarray(dframe.get_data())
            # apply color map on depth image
            # image must be converted to 8-bit per pixel first
            #dmap = cv2.applyColorMap(cv2.convertScaleAbs(f, alpha=0.3), cv2.COLORMAP_JET)
            dmap = np.asanyarray(colorizer.colorize(dframe).get_data())
            #dmap = cv2.cvtColor(dmap, cv2.COLOR_RGB2BGR)
            cv2.namedWindow('Depth video', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Depth video', dmap)
            cv2.waitKey(1)
            if cv2.getWindowProperty('Depth video', 0) < 0:
                pipe.stop()
                cv2.destroyAllWindows()
                stop()
                return

def stop():
    """
    pauses recording
    """
    global KEEP_REC, ENTRY
    KEEP_REC = False
    ENTRY.delete(0, 'end')

def discard():
    """
    Discard current video and reset the progress
    """
    global KEEP_REC, ENTRY, OUTNAME
    KEEP_REC = False
    ENTRY.delete(0, "end")
    if os.path.exists(OUTNAME):
        os.remove(OUTNAME)
    messagebox.showinfo(title="Action Succeeded",
                        message="Successfully discard record")

def quit_program():
    """
    Close camera stream properly and quit the program
    """
    global WINDOW, KEEP_REC
    KEEP_REC = False
    WINDOW.quit()
    return

#========== MAIN ==========
def main():
    # SETUP
    global WINDOW, ENTRY
    global SN, COLORIZER
    WINDOW = tk.Tk()
    SN = utils.get_serial()
    COLORIZER = rs.colorizer()

    # TEXT FIELD AND BUTTONS
    tk.Label(WINDOW, text="Enter file name").grid(row=0)
    ENTRY = tk.Entry(WINDOW)
    ENTRY.grid(row=0, column=1)
    rec_btn = tk.Button(WINDOW, text="Start record", command=record)
    rec_btn.grid(row=3, column=0, sticky=tk.W, pady=4)
    discard_btn = tk.Button(WINDOW, text="Discard", command=discard)
    discard_btn.grid(row=3, column=1, sticky=tk.W, pady=4)
    quit_btn = tk.Button(WINDOW, text="Quit", command=quit_program)
    quit_btn.grid(row=3, column=2, stick=tk.W, pady=4)

    # keep GUI window going until quit()
    WINDOW.mainloop()

#========== GLOBAL SETUP ==========
# Hardcode visual preset dictionary here
# hopefully, preset order is the same across devices
# of the same model
VISUAL_PRESET = {0: "custom", 1: "default", 3: "higha",
                4: "highd", 5: "medd"}
KEEP_REC = True
WINDOW = None
DATE = str(datetime.now().date())
ENTRY = None
OUTNAME = ""
# getting folder to save files to
OUTFOLDER = os.getcwd()
OUTFOLDER = OUTFOLDER.split("\\")[:3]
OUTFOLDER = "\\".join(OUTFOLDER)
OUTFOLDER = os.path.join(OUTFOLDER, "Documents")
OUTFOLDER = OUTFOLDER + "\\PorkBoardData"
OUTFOLDER = os.path.join(OUTFOLDER, DATE)


if __name__ == "__main__":
    main()
