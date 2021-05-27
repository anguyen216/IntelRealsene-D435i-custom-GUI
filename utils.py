#!/usr/bin/env python3
# GUI utility functions
import numpy as np
import pyrealsense2 as rs

def get_serial():
    """
    Get serial number of connected intel camera
    """
    context = rs.context()
    sn = context.devices[0].get_info(rs.camera_info.serial_number)
    return sn


def get_preset(preset_dict):
    """
    Randomly selected a preset to use for the current record
    All presets have equal probability of being chosen
    Input:
    - preset_dict: dictionary of preset to choose from
                   intel realsense D435i has 6 different presets
                   keys in preset_dict are in range [0, 5]
    Output:
    - id of the preset in the dictionary
    - return the value of preset
    """
    keys = list(preset_dict.keys())
    # equal weights for all presets
    weights = np.full(len(keys), 1/len(keys)).tolist()
    preset_id = np.random.choice(keys, p=weights)
    return preset_id, preset_dict[preset_id]
