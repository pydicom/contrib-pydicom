# ===================================================================
# imViewer-Simple.py
#
#    An example program that opens uncompressed DICOM images and
# converts them via numPy and PIL to be viewed in wxWidgets GUI
# apps.  The conversion is currently:
#
#    pydicom->NumPy->PIL->wxPython.Image->wxPython.Bitmap
#
# Gruesome but it mostly works.  Surely there is at least one
# of these steps that could be eliminated (probably PIL) but
# haven't tried that yet and I may want some of the PIL manipulation
# functions.
#
#    This won't handle RLE, embedded JPEG-Lossy, JPEG-lossless,
# JPEG2000, old ACR/NEMA files, or anything wierd.  Also doesn't
# handle some RGB images that I tried.
#
#    Have added Adit Panchal's LUT code.  It helps a lot, but needs
# to be further generalized.  Added test for window and/or level
# as 'list' type - crude, but it worked for a bunch of old MR and
# CT slices I have.
#
# Testing:      moderate
#               Tested on Windows 7 and MacOS 10.13 using numpy 1.15.2,
#               Pillow 5.2.0, Python 2.7.13 / 3.6.5, and wxPython 4.0.3
#
# Originally written by Dave Witten:  Nov. 11, 2009
# Updated by Aditya Panchal: Oct. 9, 2018
# ===================================================================

import pydicom
import wx

have_PIL = True
try:
    import PIL.Image
except ImportError:
    have_PIL = False

have_numpy = True
try:
    import numpy as np
except ImportError:
    have_numpy = False

# ----------------------------------------------------------------
#  Initialize image capabilities.
# ----------------------------------------------------------------

wx.InitAllImageHandlers()


def MsgDlg(window, string, caption='OFAImage', style=wx.YES_NO | wx.CANCEL):
    """Common MessageDialog."""
    dlg = wx.MessageDialog(window, string, caption, style)
    result = dlg.ShowModal()
    dlg.Destroy()
    return result


class ImFrame(wx.Frame):
    """Class for main window."""

    def __init__(self, parent, title):
        """Create the pydicom image example's main frame window."""

        style = wx.DEFAULT_FRAME_STYLE | wx.SUNKEN_BORDER | wx.CLIP_CHILDREN

        wx.Frame.__init__(
            self,
            parent,
            id=-1,
            title="",
            pos=wx.DefaultPosition,
            size=wx.Size(1024, 768),
            style=style)

        # --------------------------------------------------------
        # Set up the menubar.
        # --------------------------------------------------------
        self.mainmenu = wx.MenuBar()

        # Make the 'File' menu.
        menu = wx.Menu()
        item = menu.Append(wx.ID_ANY, '&Open...\tCtrl+O', 'Open file for editing')
        self.Bind(wx.EVT_MENU, self.OnFileOpen, item)
        item = menu.Append(wx.ID_ANY, 'E&xit', 'Exit Program')
        self.Bind(wx.EVT_MENU, self.OnFileExit, item)
        self.mainmenu.Append(menu, '&File')

        # Attach the menu bar to the window.
        self.SetMenuBar(self.mainmenu)

        # --------------------------------------------------------
        # Set up the main splitter window.
        # --------------------------------------------------------
        self.mainSplitter = wx.SplitterWindow(self)
        self.mainSplitter.SetMinimumPaneSize(1)

        # -------------------------------------------------------------
        # Create the folderTreeView on the left.
        # -------------------------------------------------------------
        dsstyle = wx.TR_LINES_AT_ROOT | wx.TR_HAS_BUTTONS
        self.dsTreeView = wx.TreeCtrl(self.mainSplitter, style=dsstyle)

        # --------------------------------------------------------
        # Create the ImageView on the right pane.
        # --------------------------------------------------------
        imstyle = wx.VSCROLL | wx.HSCROLL | wx.CLIP_CHILDREN
        self.imView = wx.Panel(self.mainSplitter, style=imstyle)

        self.imView.Bind(wx.EVT_PAINT, self.OnPaint)
        self.imView.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)

        self.imView.Bind(wx.EVT_SIZE, self.OnSize)

        # --------------------------------------------------------
        # Install the splitter panes.
        # --------------------------------------------------------
        self.mainSplitter.SplitVertically(self.dsTreeView, self.imView)
        self.mainSplitter.SetSashPosition(300, True)

        # --------------------------------------------------------
        # Initialize some values
        # --------------------------------------------------------
        self.dcmdsRoot = False
        self.foldersRoot = False
        self.loadCentered = True
        self.bitmap = None
        self.Show(True)

    def OnFileExit(self, event):
        """Exits the program."""
        self.Destroy()
        event.Skip()

    def OnSize(self, event):
        """Window 'size' event."""
        self.Refresh()

    def OnEraseBackground(self, event):
        """Window 'erase background' event."""
        pass

    def populateTree(self, ds):
        """ Populate the tree in the left window with the [desired]
        dataset values"""
        if not self.dcmdsRoot:
            self.dcmdsRoot = self.dsTreeView.AddRoot(text="DICOM Objects")
        else:
            self.dsTreeView.DeleteChildren(self.dcmdsRoot)
        self.recurse_tree(ds, self.dcmdsRoot)
        self.dsTreeView.ExpandAll()

    def recurse_tree(self, ds, parent, hide=False):
        """ order the dicom tags """
        for data_element in ds:
            if isinstance(data_element.value, str):
                text = str(data_element)
                ip = self.dsTreeView.AppendItem(parent, text=text)
            else:
                ip = self.dsTreeView.AppendItem(parent, text=str(data_element))

            if data_element.VR == "SQ":
                for i, ds in enumerate(data_element.value):
                    item_describe = data_element.name.replace(" Sequence", "")
                    item_text = "%s %d" % (item_describe, i + 1)
                    rjust = item_text.rjust(128)
                    parentNodeID = self.dsTreeView.AppendItem(ip, text=rjust)
                    self.recurse_tree(ds, parentNodeID)

    # --- Most of what is important happens below this line ---------------------

    def OnFileOpen(self, event):
        """Opens a selected file."""
        msg = 'Choose a file to add.'
        dlg = wx.FileDialog(self, msg, '', '', '*.*', wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            fullPath = dlg.GetPath()
            imageFile = dlg.GetFilename()
            # checkDICMHeader()
            self.show_file(imageFile, fullPath)

    def OnPaint(self, event):
        """Window 'paint' event."""
        dc = wx.PaintDC(self.imView)
        dc = wx.BufferedDC(dc)

        # paint a background just so it isn't *so* boring.
        dc.SetBackground(wx.Brush("WHITE"))
        dc.Clear()
        dc.SetBrush(wx.Brush("GREY", wx.CROSSDIAG_HATCH))
        windowsize = self.imView.GetSize()
        dc.DrawRectangle(0, 0, windowsize[0], windowsize[1])
        bmpX0 = 0
        bmpY0 = 0
        if self.bitmap is not None:
            if self.loadCentered:
                bmpX0 = (windowsize[0] - self.bitmap.Width) / 2
                bmpY0 = (windowsize[1] - self.bitmap.Height) / 2
            dc.DrawBitmap(self.bitmap, bmpX0, bmpY0, False)

    # ------------------------------------------------------------
    #  ImFrame.ConvertWXToPIL()
    #  Expropriated from Andrea Gavana's
    #  ShapedButton.py in the wxPython dist
    # ------------------------------------------------------------
    def ConvertWXToPIL(self, bmp):
        """ Convert wx.Image Into PIL Image. """
        width = bmp.GetWidth()
        height = bmp.GetHeight()
        im = wx.EmptyImage(width, height)
        im.fromarray("RGBA", (width, height), bmp.GetData())
        return im

    # ------------------------------------------------------------
    #  ImFrame.ConvertPILToWX()
    #  Expropriated from Andrea Gavana's
    #  ShapedButton.py in the wxPython dist
    # ------------------------------------------------------------
    def ConvertPILToWX(self, pil, alpha=True):
        """ Convert PIL Image Into wx.Image. """
        if alpha:
            image = wx.Image(pil.size[0], pil.size[1], clear=True)
            image.SetData(pil.convert("RGB").tobytes())
            image.SetAlpha(pil.convert("RGBA").tobytes()[3::4])
        else:
            image = wx.Image(pil.size[0], pil.size[1], clear=True)
            new_image = pil.convert('RGB')
            data = new_image.tobytes()
            image.SetData(data)
        return image

    def get_LUT_value(self, data, window, level):
        """Apply the RGB Look-Up Table for the given
           data and window/level value."""
        if not have_numpy:
            raise ImportError("Numpy is not available. "
                              "See http://numpy.scipy.org/ "
                              "to download and install")

        win = window
        lvl = level

        e = [
            0, 255,
            lambda data: ((data - (lvl - 0.5)) / (win - 1) + 0.5) * (255 - 0)
        ]
        return np.piecewise(data, [
            data <= (lvl - 0.5 - (win - 1) / 2),
            data > (lvl - 0.5 + (win - 1) / 2)
        ], e)

    # -----------------------------------------------------------
    # ImFrame.loadPIL_LUT(dataset)
    # Display an image using the Python Imaging Library (PIL)
    # -----------------------------------------------------------
    def loadPIL_LUT(self, dataset):
        if not have_PIL:
            raise ImportError("Python Imaging Library is not available."
                              " See http://www.pythonware.com/products/pil/"
                              " to download and install")
        if 'PixelData' not in dataset:
            raise TypeError("Cannot show image -- "
                            "DICOM dataset does not have pixel data")

        # can only apply LUT if these values exist
        if ('WindowWidth' not in dataset) or ('WindowCenter' not in dataset):
            bits = dataset.BitsAllocated
            samples = dataset.SamplesPerPixel
            if bits == 8 and samples == 1:
                mode = "L"
            elif bits == 8 and samples == 3:
                mode = "RGB"
            # not sure about this -- PIL source says is
            # 'experimental' and no documentation.
            elif bits == 16:
                # Also, should bytes swap depending
                # on endian of file and system??
                mode = "I;16"
            else:
                msg = "Don't know PIL mode for %d BitsAllocated" % (bits)
                msg += " and %d SamplesPerPixel" % (samples)
                raise TypeError(msg)
            size = (dataset.Columns, dataset.Rows)

            # Recommended to specify all details by
            # http://www.pythonware.com/library/pil/handbook/image.htm
            im = PIL.Image.frombuffer(mode, size, dataset.PixelData, "raw",
                                      mode, 0, 1)
        else:
            ew = dataset['WindowWidth']
            ec = dataset['WindowCenter']
            ww = int(ew.value[0] if ew.VM > 1 else ew.value)
            wc = int(ec.value[0] if ec.VM > 1 else ec.value)
            image = self.get_LUT_value(dataset.pixel_array, ww, wc)

            # Convert mode to L since LUT has only 256 values:
            # http://www.pythonware.com/library/pil/handbook/image.htm
            im = PIL.Image.fromarray(image).convert('L')
        return im

    def show_file(self, imageFile, fullPath):
        """ Load the DICOM file, make sure it contains at least one
        image, and set it up for display by OnPaint().  ** be
        careful not to pass a unicode string to read_file or it will
        give you 'fp object does not have a defer_size attribute,
        or some such."""
        ds = pydicom.dcmread(str(fullPath))

        # change strings to unicode
        ds.decode()
        self.populateTree(ds)
        if 'PixelData' in ds:
            self.dImage = self.loadPIL_LUT(ds)
            if self.dImage is not None:
                tmpImage = self.ConvertPILToWX(self.dImage, False)
                self.bitmap = wx.Bitmap(tmpImage)
                self.Refresh()


# ------ This is just the initialization of the App  ----

# =======================================================
# The main App Class.
# =======================================================


class App(wx.App):
    """Image Application."""

    def OnInit(self):
        """Create the Image Application."""
        ImFrame(None, 'wxImage Example')
        return True


# ------------------------------------------------------
# If this file is running as main or a
# standalone test, begin execution here.
# ------------------------------------------------------

if __name__ == '__main__':
    app = App(0)
    app.MainLoop()
