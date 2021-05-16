# -*- coding: utf-8 -*-
"""
Dicom Image IOD
"""
from pydicom.config import logger


class Image(object):
    def __init__(self, dicom_dataset=None):
        self.dicom_dataset = dicom_dataset

    def __repr__(self):
        try:
            output = f"\t\t\tSOPInstanceUID = {self.dicom_dataset.SOPInstanceUID}:\n"
            return output
        except Exception as e:
            logger.debug("trouble getting Series data", exc_info=e)
            return "\t\t\tSOPInstanceUID = None\n"

    def __str__(self):
        try:
            return self.dicom_dataset.SOPInstanceUID
        except Exception as e:
            logger.debug("trouble getting image SOPInstanceUID", exc_info=e)
            return "None"

    def __eq__(self, other):
        try:
            return self.dicom_dataset.SOPInstanceUID == other.dicom_dataset.SOPInstanceUID
        except Exception as e:
            logger.debug("trouble comparing two Images", exc_info=e)
            return False

    def __ne__(self, other):
        try:
            return self.dicom_dataset.SOPInstanceUID != other.dicom_dataset.SOPInstanceUID
        except Exception as e:
            logger.debug("trouble comparing two Images", exc_info=e)
            return True

    def __getattr__(self, name):
        return getattr(self.dicom_dataset, name)
