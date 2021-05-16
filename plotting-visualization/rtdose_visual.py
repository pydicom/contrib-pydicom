# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 10:45:06 2021

@author: Francisco Piqueras Guardiola
@author: Fernando Hueso González

Note: This code is designed to be run in spyder environment
"""
import pydicom
import matplotlib.pyplot as plt
import os
import numpy as np
import gzip
import sys

#!/usr/bin/python


# Here we define the functions that we are going to use in our program
def remove_keymap_conflicts(new_keys_set):
    """
    Removes possible conflicts created by the use of a key that already has an use in the plot.

    Parameters
    ----------
    new_keys_set : set

    Returns
    -------
    None.

    """
    for prop in plt.rcParams:
        if prop.startswith("keymap."):
            keys = plt.rcParams[prop]
            remove_list = set(keys) & new_keys_set
            for key in remove_list:
                keys.remove(key)


def multi_slice_viewer(volume):
    """
    This function uses the  methods found in https://github.com/jni/mpl-volume-viewer
    available under a BSD license.
    Parameters
    ----------
    volume : numpy.ndarray
        An array of uint32 with three dimensions (a,b,c)

    Returns
    -------
    None.

    """

    remove_keymap_conflicts({"n", "p", "c"})
    fig, ax = plt.subplots()
    ax.volume = volume
    ax.index = volume.shape[0] // 2
    ax.axis = 0
    ax.imshow(volume[ax.index, :, :], cMap, vmin=cMin, vmax=cMax)
    fig.canvas.mpl_connect("key_press_event", process_key)


def process_key(event):
    """
    Processes a key input given by the user

    Parameters
    ----------
    event : matplotlib.backend_bases.KeyEvent
        Key event that is supported by fig.canvas.mpl_connect()

    Returns
    -------
    None.

    """

    fig = event.canvas.figure
    ax = fig.axes[0]

    if event.key == "p":
        previous_slice(ax)
        draw(ax, False)
    elif event.key == "n":
        next_slice(ax)
        draw(ax, False)
    elif event.key == "c":
        change_axis(ax)
        draw(ax, True)

    fig.canvas.draw_idle()


def draw(ax, changing):
    """
    Draws the new plot once the key input has changed the settings

    Parameters
    ----------
    ax : matplotlib.axes._subplots.AxesSubplot
        Subplot made by matplotlib.

    changing : Boolean
        A boolean variable that remains False unless we change the axis we are plotting.

    Returns
    -------
    None.

    """
    volume = ax.volume
    if ax.axis == 0:
        if changing:
            del ax.images[
                0
            ]  # this is needed in order to avoid making a new plot in ax.images[1]
            ax.imshow(volume[ax.index, :, :], cMap, vmin=cMin, vmax=cMax)
        else:
            ax.images[0].set_array(volume[ax.index, :, :])

    elif ax.axis == 1:
        if changing:
            del ax.images[0]
            ax.imshow(volume[:, ax.index, :], cMap, vmin=cMin, vmax=cMax)
        else:
            ax.images[0].set_array(volume[:, ax.index, :])

    elif ax.axis == 2:
        if changing:
            del ax.images[0]
            ax.imshow(volume[:, :, ax.index], cMap, vmin=cMin, vmax=cMax)
        else:
            ax.images[0].set_array(volume[:, :, ax.index])


def previous_slice(ax):
    """
    Go to the previous slice.

    Parameters
    ----------
    ax : matplotlib.axes._subplots.AxesSubplot
        Subplot made by matplotlib.

    Returns
    -------
    None.

    """

    volume = ax.volume
    ax.index = (ax.index - 1) % volume.shape[ax.axis]  # wrap around using %


def next_slice(ax):
    """
    Go to the next slice.

    Parameters
    ----------
    ax : matplotlib.axes._subplots.AxesSubplot
        Subplot made by matplotlib.

    Returns
    -------
    None.

    """
    volume = ax.volume
    ax.index = (ax.index + 1) % volume.shape[ax.axis]


def change_axis(ax):
    """
    Changes the axis of view

    Parameters
    ----------
    ax : matplotlib.axes._subplots.AxesSubplot
        Subplot made by matplotlib.
    Returns
    -------
    None.

    """
    volume = ax.volume
    ax.axis = (ax.axis + 1) % 3
    ax.index = volume.shape[ax.axis] // 2


# Define the path folder where the file is , or directly the RTdose full file name
path = "C:/Users/kpiqu/OneDrive - Universitat de Valencia/Máster Física Médica/TFM/Comienzos PyDICOM y Slicer/SlicerRtData-/eclipse-8.1.20-phantom-ent/Original"
global cMin, cMax, cMap
cMap = "inferno"
cMin = None
cMax = None


# This would print all the files and directories
if __name__ == "__main__":

    if os.path.isdir(path):

        dirs = os.listdir(path)
        for file in dirs:
            if not os.path.isdir(path + "/" + file):
                ds = pydicom.dcmread(path + "/" + file, force=True)
                if (
                    ds.file_meta.MediaStorageSOPClassUID
                    == "1.2.840.10008.5.1.4.1.1.481.2"
                ):
                    print("The RTDose file is named:", file)
                    print(".")
                    print(".")
                    print(".")
                    break

    else:
        cwd = os.getcwd()

        if not os.path.isfile(cwd + "/" + path):
            print("Input file not found")
            sys.exit()

        if path.endswith(".gz"):
            with gzip.open(path, "rb") as f_in:
                ds = pydicom.dcmread(f_in, force=True)
        else:
            ds = pydicom.dcmread(cwd + "/" + path, force=True)

        if ds.file_meta.MediaStorageSOPClassUID == "1.2.840.10008.5.1.4.1.1.481.2":
            print("The RTDose file is named:", path)
            print(".")
            print(".")
            print(".")
        else:
            print("The file is not in RTDose format ")
            sys.exit()
        if not hasattr(ds.file_meta, "TransferSyntaxUID"):
            ds.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian

    dose = ds.pixel_array.astype("float")
    dose *= ds.DoseGridScaling
    print("The maximum value of the dose is: ", np.max(dose), "Gy")
    print("The mean value of the dose is: ", np.mean(dose), "Gy")
    print("The median value of the dose is: ", np.median(dose), "Gy")
    print("The minimum value of the dose is: ", np.min(dose), "Gy")
    print(".")
    print(".")
    print(".")
    print("To go to the previous slice press 'p'")
    print("To go to the next slice press 'n'")
    print("To change the axis of view press 'c'")

    multi_slice_viewer(dose)
    print(".")
    print(".")
    print(".")

    print(
        "Process finished. If the program has not plotted the scan, check if there is an RTDose file in the path folder"
    )
