#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This example will read a zip/tar/tgz of files and
print a list of filenames and the dicom patientID for
that file (if available)

run with
dicom_zip_reader.py --input-file test.zip
dicom_zip_reader.py --input-file test.tar
dicom_zip_reader.py --input-file test.tgz
"""

# Copyright (c) 2017 Robert Haxton
# This file is part of pydicom, released under a modified MIT license.
#    See the file LICENSE included with this distribution, also
#    available at https://github.com/pydicom/pydicom

import argparse
import logging
import os
import sys
import tarfile
import zipfile
from io import StringIO
from tarfile import TarFile

import pydicom


def show_patient_IDs(file_list=None):
    logger = logging.getLogger("show_patient_IDs")
    if file_list is None:
        file_list = []
    for file_name, file_object in file_list:
        try:
            logger.info(f'reading: {file_name}')
            f = pydicom.dcmread(fp=file_object)
            logger.info("finished reading")
            patient_id = f.get("PatientID", "No ID")
            print(file_name, "has patient id of", patient_id)
        except Exception:
            print(file_name, "had no patient id for some reason")


def unzip(zip_archive):
    """
    zip_archive is a zipfile object (from
        zip_archive = zipfile.ZipFile(filename, 'r') for example)

    Returns a dictionary of file names and file like objects (StringIO's)

    The filter in the if statement skips directories and dot files
    """
    logger = logging.getLogger("unzip")
    logger.debug("Unzipping...")
    file_list = []
    for file_name in zip_archive.namelist():
        logger.debug(f"Unzipping {file_name}")
        if (not os.path.basename(file_name).startswith('.') and
                not file_name.endswith('/')):
            file_object = zip_archive.open(file_name, 'rU')
            file_like_object = StringIO(file_object.read())
            file_object.close()
            file_like_object.seek(0)
            name = os.path.basename(file_name)
            file_list.append((name, file_like_object))
    logging.debug("Unzip complete!")
    return file_list


def untar(tar_archive):
    """
    tar_archive is a TarFile object (from
        tar_archive = TarFile.open(fileobj=file_object, mode='r') for example)

    Returns a dictionary of file names and file like objects (StringIO's)

    The filter in the if statement skips directories and dot files

    """
    logger = logging.getLogger("untar")
    logger.debug("Untarring...")
    file_list = []
    for file_info in tar_archive.getmembers():
        logging.debug(f"Found: {file_info.name}")
        if (file_info.isfile() and
                not os.path.basename(file_info.name).startswith('.')):
            file_object = tar_archive.extractfile(file_info)
            file_like_object = StringIO(file_object.read())
            file_object.close()
            file_like_object.seek(0)
            name = os.path.basename(file_info.name)
            file_list.append((name, file_like_object))
    logging.debug("Untar complete!")
    return file_list


def parse_args():
    """Argument parser for load series"""
    parser = argparse.ArgumentParser(
        description='Read a zip/tar/gz of dicom files')
    parser.add_argument('--input-file',
                        '-i',
                        dest='input_file',
                        type=str,
                        help='zip')
    _args = parser.parse_args()
    return _args


def main():
    args = parse_args()
    try:
        if zipfile.is_zipfile(args.input_file):
            zip_archive = zipfile.ZipFile(args.input_file, 'r')
            file_list = unzip(zip_archive)
            show_patient_IDs(file_list)
        elif tarfile.is_tarfile(args.input_file):
            tar_archive = TarFile.open(name=args.input_file, mode='r')
            file_list = untar(tar_archive)
            show_patient_IDs(file_list)
        else:
            print("Unknown format")
    except KeyboardInterrupt:
        logging.info("Interrupt detected, quiting")
    except Exception as e:
        logging.warning("Unknown Error, exiting", exc_info=e)
        sys.exit(1)


if __name__ == "__main__":
    main()
