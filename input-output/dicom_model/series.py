# -*- coding: utf-8 -*-
"""
Dicom Study IOD
"""
from pydicom.config import logger

from image import Image


class Series(object):
    def __init__(self, dicom_dataset=None):
        self.images = list()
        self.dicom_dataset = dicom_dataset
        self.images.append(Image(dicom_dataset=dicom_dataset))

    def __repr__(self):
        try:
            output = f"\t\tSeriesIUID = {self.dicom_dataset.SeriesInstanceUID}:\n"
            for x in self.images:
                output += repr(x)
            return output
        except Exception as e:
            logger.debug("trouble getting Series data", exc_info=e)
            return "\t\tSeriesIUID = None\n"

    def __str__(self):
        try:
            return self.dicom_dataset.SeriesInstanceUID
        except Exception as e:
            logger.debug("trouble getting image SeriesInstanceUID", exc_info=e)
            return "None"

    def __eq__(self, other):
        try:
            return self.dicom_dataset.SeriesInstanceUID == other.dicom_dataset.SeriesInstanceUID
        except Exception as e:
            logger.debug("trouble comparing two Series", exc_info=e)
            return False

    def __ne__(self, other):
        try:
            return self.dicom_dataset.SeriesInstanceUID != other.dicom_dataset.SeriesInstanceUID
        except Exception as e:
            logger.debug("trouble comparing two Series", exc_info=e)
            return True

    def __getattr__(self, name):
        return getattr(self.dicom_dataset, name)

    def add_dataset(self, dataset):
        try:
            if self.dicom_dataset.SeriesInstanceUID == dataset.SeriesInstanceUID:
                for x in self.images:
                    if x.SOPInstanceUID == dataset.SOPInstanceUID:
                        logger.debug("Image is already part of this series")
                        break
                else:
                    self.images.append(Image(dicom_dataset=dataset))

            else:
                raise KeyError("Not the same SeriesInstanceUIDs")
        except Exception as e:
            logger.debug("trouble adding image to series", exc_info=e)
            raise KeyError("Not the same SeriesInstanceUIDs")
