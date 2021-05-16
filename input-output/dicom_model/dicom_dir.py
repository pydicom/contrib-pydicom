#!/usr/bin/env python
"""
This example will read a directory of dicom files and parse them into
a list of Patients with Studies, Series, and Instances for each.

run with
./dicom_dir -d directory --recursive

This example just prints out the patient/study/series/instance hierarchy
"""

# Copyright (c) 2017 Robert Haxton
# This file is part of pydicom, released under a modified MIT license.
#    See the file LICENSE included with this distribution, also
#    available at https://github.com/pydicom/pydicom

import argparse
import fnmatch
import os
import sys
from pprint import pformat

import pydicom
from pydicom.misc import is_dicom

from patient import Patient


def find_dicom_files(directory, pattern="*", directory_exclude_pattern='', recursive=True):
    """
    search a root directory for all files matching a given pattern (in Glob format - *.dcm etc)
    and that have the "DICM" magic number
    returns a full path name
    """
    for root, dirs, files in os.walk(directory):
        if not recursive:
            dirs = []
        for x in dirs:
            if fnmatch.fnmatch(x, directory_exclude_pattern):
                try:
                    dirs.remove(x)
                except Exception:
                    pass
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                if is_dicom(filename):
                    yield filename


def parse_args(argv=None):
    """Argument parser for Dicom Tools"""
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(
        description="Scan a directory of dicom files "
                    "and assemble a list of patient, "
                    "study, series, image sets")
    parser.add_argument("-d", "--dicom-dir",
                        dest='dicom_dir',
                        type=str,
                        help="Directory of dicom files ",
                        default=".")
    parser.add_argument("-r", "--recursive",
                        dest='recursive',
                        action='store_true',
                        help="Process recursively")
    parser.add_argument("--no-recursive",
                        dest='recursive',
                        action='store_false',
                        help="Do not process recursively")
    parser.set_defaults(recursive=True)
    return parser.parse_args()


def main(argv=None):
    """main for dicom_dir"""
    if argv is None:
        argv = sys.argv
    args = parse_args(argv=argv[1:])
    print(pformat(args))
    patients = list()
    for x in find_dicom_files(directory=args.dicom_dir,
                              pattern="*.dcm",
                              directory_exclude_pattern=".*",
                              recursive=args.recursive):
        f = pydicom.dcmread(x)
        for p in patients:
            try:
                p.add_dataset(f)
            except Exception as e:
                pass
            else:
                break
        else:
            print("New patient!")
            patients.append(Patient(dicom_dataset=f))
    print("Found", len(patients), "patients")
    for x in patients:
        print(repr(x))
        print("\n")


if __name__ == "__main__":
    main()
