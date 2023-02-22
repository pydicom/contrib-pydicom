# pydicom_PIL.py

"""View DICOM images using Python image Library (PIL)
Usage:
>>> import pydicom
>>> from pydicom.contrib.pydicom_PIL import show_PIL
>>> ds = pydicom.dcmread("filename")
>>> show_PIL(ds)
Requires Numpy:
    http://numpy.scipy.org/
Python Imaging Library:
    http://www.pythonware.com/products/pil/
and DICOM Modality LUT module
    http://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.11.html#sect_C.11.1
"""
# Copyright (c) 2009 Darcy Mason, Adit Panchal
# This file is part of pydicom, relased under an MIT license.
#    See the file LICENSE included with this distribution, also
#    available at https://github.com/pydicom/pydicom

# Based on image.py from pydicom version 0.9.3,
#    LUT code added by Adit Panchal
# Tested on Python 2.5.4 (32-bit) on Mac OS X 10.6
#    using numpy 1.3.0 and PIL 1.1.7b1


try:
    from PIL import Image,ImageEnhance
    have_PIL = True
except ImportError:
    have_PIL = False

#apply_modality_lut() function comes with pydicom module
try:
    from pydicom.pixel_data_handlers.util import apply_modality_lut
    have_lut = True
except ImportError:
    have_lut = False


def get_LUT_value(dataset):
    """Apply the RGB Look-Up Table for the given
       dataset"""
    if not have_lut:
        raise ImportError("pydicom is not available."
                          "See https://pydicom.github.io/pydicom/dev/tutorials/installation.html"
                          "to download and install")

    #Pixel Data
    pixel_data = dataset.pixel_array

    return apply_modality_lut(pixel_data,dataset)


def get_PIL_image(dataset,brightness_factor = 1.0):
    """Get Image object from Python Imaging Library(PIL)

       Manipulate image brightness using brightness_factor parameter,
       receives a float value,
       Default = 1.0
       Brighter > 1.0 | Darker < 1.0 

    """
    if not have_PIL:
        raise ImportError("Python Imaging Library is not available. "
                          "See http://www.pythonware.com/products/pil/ "
                          "to download and install")

    if ('PixelData' not in dataset):
        raise TypeError("Cannot show image -- DICOM dataset does not have "
                        "pixel data")
    
    bits = dataset.BitsAllocated

    samples = dataset.SamplesPerPixel

    if bits == 8 and samples == 1:

        mode = "L"

    elif bits == 8 and samples == 3:

        mode = "RGB"

    elif bits == 16:
        # not sure about this -- PIL source says is 'experimental'
        # and no documentation. Also, should bytes swap depending
        # on endian of file and system??
        mode = "I;16"
    else:
        
        raise TypeError("Don't know PIL mode for %d BitsAllocated "
                        "and %d SamplesPerPixel" % (bits, samples))

    #LUTification returns ndarrays
    #can only apply LUT if pydicom is installed
    image = get_LUT_value(dataset)

    try:
        #if pixel data has only one frame
        im = Image.fromarray(image).convert(mode)

    except:
        #When pixel data has multiple frames, output the first one
        im = Image.fromarray(image[0]).convert(mode)

    if not brightness_factor == 1.0:
        #enhancer will enhance
        enhancer = ImageEnhance.Brightness(im)

        #save enhanced version
        better_im = enhancer.enhance(brightness_factor)

        return better_im

    
    #return default brightness
    return im


def show_PIL(dataset):
    """Display an image using the Python Imaging Library (PIL)"""
    im = get_PIL_image(dataset)

    im.show()


def create_GIF(dataset,brightness_factor = 1.0,filename="clip"):
    """Create a GIF using the Python Imaging Library (PIL)
    
       Only if DICOM file has multiple frames

       Manipulate image brightness using brightness_factor parameter,
       receives a float value,
       Default = 1.0
       Brighter > 1.0 | Darker < 1.0

       Use filename parameter to specify the name of the file created
       Receives a string value
    """
    if not have_PIL:
        raise ImportError("Python Imaging Library is not available. "
                          "See http://www.pythonware.com/products/pil/ "
                          "to download and install")

    if ('PixelData' not in dataset):
        raise TypeError("Cannot show image -- DICOM dataset does not have "
                        "pixel data")
    
    bits = dataset.BitsAllocated

    samples = dataset.SamplesPerPixel

    if bits == 8 and samples == 1:

        mode = "L"

    elif bits == 8 and samples == 3:

        mode = "RGB"

    elif bits == 16:
        # not sure about this -- PIL source says is 'experimental'
        # and no documentation. Also, should bytes swap depending
        # on endian of file and system??
        mode = "I;16"
    else:
        
        raise TypeError("Don't know PIL mode for %d BitsAllocated "
                        "and %d SamplesPerPixel" % (bits, samples))

    #Can only apply LUT if pydicom is installed                    
    #LUTification returns ndarrays
    frames = get_LUT_value(dataset)

    #Create the first frame 
    gif = Image.fromarray(frames[0]).convert(mode)

    if not brightness_factor == 1.0:
        #enhancer will enhance
        enhancer = ImageEnhance.Brightness(gif)

        #save enhanced version
        better_gif = enhancer.enhance(brightness_factor)

        #Create the rest of the frames
        data = []

        #Loop thru each frame
        for item in frames[1:]:

            frame = Image.fromarray(item).convert(mode)

            enhancer = ImageEnhance.Brightness(frame)

            better_frame = enhancer.enhance(brightness_factor)

            data.append(better_frame)

        better_gif.save(f'./{filename}.gif', save_all=True, quality=100 , append_images=data, optimize=True, duration=15, loop=0)
    
    #Create the rest of the frames
    data = []

    #Loop thru each frame
    for item in frames[1:]:

        frame = Image.fromarray(item).convert(mode)

        enhancer = ImageEnhance.Brightness(frame)

        better_frame = enhancer.enhance(brightness_factor)

        data.append(better_frame)
    
    #default brightness
    gif.save(f'./{filename}.gif', save_all=True, quality=100 , append_images=data, optimize=True, duration=15, loop=0)
