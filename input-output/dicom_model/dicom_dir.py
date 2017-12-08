#!/usr/bin/env python
from __future__ import print_function
import os
import argparse
import sys
import fnmatch
from pprint import pformat
import pydicom

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
                x = "Not A Dicom File"
                with open(filename, 'rb') as f:
                    x = f.read(132)
                if x[128:] == "DICM":
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
