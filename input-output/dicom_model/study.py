# -*- coding: utf-8 -*-
"""
Dicom Study IOD
"""
from pydicom.config import logger

from series import Series


class Study(object):
    def __init__(self, dicom_dataset=None):
        self.series = list()
        self.dicom_dataset = dicom_dataset
        self.series.append(Series(dicom_dataset=dicom_dataset))

    def __repr__(self):
        try:
            output = f"\tStudyIUID = {self.dicom_dataset.StudyInstanceUID}:\n"
            for x in self.series:
                output += repr(x)
            return output
        except Exception as e:
            logger.debug("trouble getting Study data", exc_info=e)
            return "\tStudyIUID = None\n"

    def __str__(self):
        try:
            return self.dicom_dataset.StudyInstanceUID
        except Exception as e:
            logger.debug("trouble getting image StudyInstanceUID", exc_info=e)
            return "None"

    def __eq__(self, other):
        try:
            return self.dicom_dataset.StudyInstanceUID == other.dicom_dataset.StudyInstanceUID
        except Exception as e:
            logger.debug("trouble comparing two Studies", exc_info=e)
            return False

    def __ne__(self, other):
        try:
            return self.dicom_dataset.StudyInstanceUID != other.dicom_dataset.StudyInstanceUID
        except Exception as e:
            logger.debug("trouble comparing two Studies", exc_info=e)
            return True

    def __getattr__(self, name):
        return getattr(self.dicom_dataset, name)

    def add_dataset(self, dataset):
        try:
            if self.dicom_dataset.StudyInstanceUID == dataset.StudyInstanceUID:
                for x in self.series:
                    try:
                        x.add_dataset(dataset)
                        logger.debug("Part of this series")
                        break
                    except Exception as e:
                        logger.debug("Not part of this series")
                else:
                    self.series.append(Series(dicom_dataset=dataset))
            else:
                raise KeyError("Not the same StudyInstanceUIDs")
        except Exception as e:
            logger.debug("trouble adding series to study", exc_info=e)
            raise KeyError("Not the same StudyInstanceUIDs")
