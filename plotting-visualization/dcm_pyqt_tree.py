# dcm_qt_tree.py
"""View DICOM files in a tree using Qt and PyQT5"""
# Copyright (c) 2013 Padraig Looney
# Copyright (c) 2018 Aditya Panchal
# This file is released under the
# pydicom (https://github.com/pydicom/pydicom)
# license, see the file LICENSE available at
# (https://github.com/pydicom/pydicom)

import sys

import pydicom
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import (QApplication, QDesktopWidget, QTreeView,
                             QVBoxLayout, QWidget)


class DicomTree(QWidget):
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.setWindowTitle('DICOM Tree')
        self.setGeometry(0, 0, 800, 600)
        self.center()

        self.create_model()
        self.init_tree()
        self.show()

    def center(self):
        # Get geometry of the main window
        qr = self.frameGeometry()
        # Get the center point of screen
        cp = QDesktopWidget().availableGeometry().center()
        # Move rectangle's center point to screen's center point
        qr.moveCenter(cp)
        # top left of rectangle becomes top left of window centering it
        self.move(qr.topLeft())

    def create_model(self):
        model = QStandardItemModel(0, 5, self)
        model.setHeaderData(0, Qt.Horizontal, "Name")
        model.setHeaderData(1, Qt.Horizontal, "Value")
        model.setHeaderData(2, Qt.Horizontal, "Tag")
        model.setHeaderData(3, Qt.Horizontal, "VM")
        model.setHeaderData(4, Qt.Horizontal, "VR")
        parentItem = model.invisibleRootItem()

        ds = pydicom.read_file(self.filename, force=True)
        self.recurse_dicom_tree(ds, parentItem)
        self.model = model

    def init_tree(self):
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.tree)
        self.setLayout(mainLayout)
        self.tree.setAlternatingRowColors(True)
        [self.tree.resizeColumnToContents(x) for x in range(5)]

    def recurse_dicom_tree(self, ds, parent, name=None):
        for _, data_element in enumerate(ds):
            # If this is non-sequence element, add directly to parent
            # print('aa', data_element, 'bb')
            if not (data_element.VR == 'SQ'):
                self.add_item_to_tree(data_element, parent)
            else:
                # Create the parent sequence in tree
                seq_parent = self.add_item_to_tree(data_element, parent)
                # For each item in sequence create a child
                for i, seq_ds in enumerate(data_element.value):
                    # break
                    seq_item_description = data_element.name.replace(
                        " Sequence", "")
                    name = "%s %d" % (seq_item_description, i+1)
                    seq_item = self.add_item_to_tree(seq_ds, seq_parent, name)
                    # Append the contents of each sequence item as a grandchild
                    self.recurse_dicom_tree(seq_ds, seq_item, name)
        return parent

    def add_item_to_tree(self, data_element, parent, element_name=None):
        if element_name:
            cols = [element_name, '', '', '', '']
        else:
            value = '' if data_element.VR == 'SQ' else data_element.value
            if (data_element.name == 'Pixel Data'):
                value = 'Array of ' + str(len(data_element.value)) + ' bytes'
            cols = [data_element.name, str(value), str(data_element.tag), str(
                data_element.VM), str(data_element.VR)]
        parent.appendRow([QStandardItem(c) for c in cols])
        last_parent = parent.child(parent.rowCount()-1)

        return last_parent


def main():
    app = QApplication(sys.argv)
    filename = sys.argv[1]
    dicomtree = DicomTree(filename)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
