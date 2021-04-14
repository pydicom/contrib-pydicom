# -*- coding: utf-8 -*-
"""
Created on Wed Mar 31 10:45:06 2021

@author: Francisco Piqueras Guardiola
@author: Fernando Hueso González
"""
import pydicom
import matplotlib.pyplot as plt
import os
import numpy as np
#!/usr/bin/python

# Define the path folder where the file is and the global variables
path = ''
dirs = os.listdir( path )
global gaxis
gaxis= 0 %2
global cMin, cMax,cMap
cMap = 'turbo'
cMin = None
cMax = None

#Here we define the functions that we are gona use in our program
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
        if prop.startswith('keymap.'):
            keys = plt.rcParams[prop]
            remove_list = set(keys) & new_keys_set
            for key in remove_list:
                keys.remove(key)
   
def multi_slice_viewer(volume):
    """
    Based on : https://www.datacamp.com/community/tutorials/matplotlib-3d-volumetric-data
    Parameters
    ----------
    volume : numpy.ndarray
        An array of uint32 with three dimensions (a,b,c)

    Returns
    -------
    None.

    """
    
    remove_keymap_conflicts({'n', 'p', 'c'})
    fig, ax = plt.subplots()
    ax.volume = volume
    ax.index = volume.shape[0] // 2
    ax.imshow(volume[ax.index,:,:],cMap, vmin=cMin, vmax=cMax)
    fig.canvas.mpl_connect('key_press_event', process_key)
    
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
    global gaxis 
    fig = event.canvas.figure
    ax = fig.axes[0]
 
    
    if event.key == 'p':
        previous_slice(ax,gaxis)
        draw(ax,gaxis,False)
    elif event.key == 'n':
        next_slice(ax,gaxis)
        draw(ax,gaxis,False)
    elif event.key == 'c':
        "Change the axis of view"
        if gaxis == 0:
            gaxis=1
        elif gaxis == 1:
            gaxis=2
        elif gaxis == 2:
            gaxis=0
        
        ax.index = (ax.index ) % ax.volume.shape[gaxis]
        del ax.images[0]
        draw(ax,gaxis,True)

    fig.canvas.draw_idle()

def draw(ax,axis,changing):
    """
    Draws the new plot once the key input has changed the settings 

    Parameters
    ----------
    ax : matplotlib.axes._subplots.AxesSubplot
        Subplot made by matplotlib.
    axis : int
        An integer number that defines which axis we are plotting.
    changing : Boole
        A boole variable that remains False unless we change the axis we are plotting.

    Returns
    -------
    None.

    """
    volume= ax.volume
    if axis== 0:
        if changing:
            ax.imshow(volume[ax.index,:,:],cMap, vmin=cMin, vmax=cMax)
            
        else:
            ax.images[0].set_array(volume[ax.index,:,:])
       
    elif axis== 1:
        if changing:
            ax.imshow(volume[:,ax.index,:],cMap, vmin=cMin, vmax=cMax)
        else:
            ax.images[0].set_array(volume[:,ax.index,:])
    
    elif axis == 2:
         if changing:
            ax.imshow(volume[:,:,ax.index],cMap, vmin=cMin, vmax=cMax)
         else:
            ax.images[0].set_array(volume[:,:,ax.index])
       

def previous_slice(ax,axis):
    """
    Go to the previous slice.

    Parameters
    ----------
    ax : matplotlib.axes._subplots.AxesSubplot
        Subplot made by matplotlib.
    axis : int
        An integer number that defines which axis we are plotting.

    Returns
    -------
    None.

    """
   
    volume = ax.volume
    ax.index = (ax.index - 1) % volume.shape[axis]  # wrap around using %
    
def next_slice(ax,axis):
    """
    Go to the next slice.

    Parameters
    ----------
    ax : matplotlib.axes._subplots.AxesSubplot
        Subplot made by matplotlib.
    axis : int
        An integer number that defines which axis we are plotting.

    Returns
    -------
    None.

    """
    volume = ax.volume
    ax.index = (ax.index + 1) % volume.shape[axis]


# This would print all the files and directories
for file in dirs:
  ds = pydicom.dcmread(path+"/"+file)
  if ds.file_meta.MediaStorageSOPClassUID == '1.2.840.10008.5.1.4.1.1.481.2':
      print("The RTDose file is named:",file)
      dose = ds.pixel_array.astype('float')
      dose *= ds.DoseGridScaling
      print("The value of the dose is: ",np.max(dose),'Gy')
      print("To go to the previous slice press 'p'")
      print("To go to the next slice press 'n'")
      print("To change the axis of view press 'c'")
      
      multi_slice_viewer(dose)
print("Process finished. If the program has not plotted the scan, check if there is an RTDose file in the path folder")

