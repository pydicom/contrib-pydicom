#!/usr/bin/env python
"""Recursively search a directory for DICOM datasets and generate new and
consistent UIDs for the following top-level elements:

* (0020,000D) Study Instance UID
* (0020,000E) Series Instance UID
* (0008,0018) SOP Instance UID
* (0020,0052) Frame of Reference UID

Possible uses:

* Changing the UIDs of CT studies prior to importing them into a system in
  which the original datasets have already been imported.
"""

from __future__ import print_function

import argparse
import os
import sys

from pydicom import dcmread
from pydicom.uid import generate_uid, PYDICOM_ROOT_UID


def setup_argparse():
    """Setup the CLI argument parser.

    Returns
    -------
    parser : argparse.ArgumentParser
        The CLI argument parser object.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Search a directory for DICOM datasets and generate new and "
            "consistent UIDs for (0020,000D) 'Study Instance UID', "
            "(0020,000E) 'Series Instance UID', (0008,0018) 'SOP Instance "
            "UID' and (0020,0052) 'Frame of Reference UID'"
        ),
    )

    parser.add_argument(
        'directory',
        type=str,
        help="The path to the directory containing the datasets",
    )
    parser.add_argument(
        '-nb',
        action='store_false',
        help="Don't create a backup of the original datasets"
    )
    parser.add_argument(
        '--org-root',
        type=str,
        help=(
            "Override the <org root> section of the UIDs with the "
            "supplied value (default is the pydicom root UID "
            "'1.2.826.0.1.3680043.8.498.')"
        ),
        default=PYDICOM_ROOT_UID,
    )

    return parser


args = setup_argparse().parse_args()


# Dicts to translate from the original to the new UIDs
ALL_STUDY_UIDS = {}
ALL_SERIES_UIDS = {}
ALL_FOR_UIDS = {}

# <org root> must be less than 63 characters long and warn if longer than 58
# characters
if len(args.org_root) > 63:
    sys.exit("The <org root> value must be less than 64 characters long")


# Recursively search the specified directory
all_fpath = []
for root, dirs, files in os.walk(args.directory):
    for fname in files:
        # The full path to the directory containing the file
        fdir = os.path.abspath(root)
        # The full path to each file
        all_fpath.append(os.path.abspath(os.path.join(root, fname)))

# Try and open all the files as DICOM
bad_files = []
for fpath in all_fpath:
    if os.path.isfile(fpath):
        try:
            ds = dcmread(fpath, force=True)

            if 'StudyInstanceUID' in ds:
                if ds.StudyInstanceUID not in ALL_STUDY_UIDS:
                    ALL_STUDY_UIDS[ds.StudyInstanceUID] = generate_uid(args.org_root)

                ds.StudyInstanceUID = ALL_STUDY_UIDS[ds.StudyInstanceUID]

            if 'SeriesInstanceUID' in ds:
                if ds.SeriesInstanceUID not in ALL_SERIES_UIDS:
                    ALL_SERIES_UIDS[ds.SeriesInstanceUID] = generate_uid(args.org_root)

                ds.SeriesInstanceUID = ALL_SERIES_UIDS[ds.SeriesInstanceUID]

            if 'FrameOfReferenceUID' in ds:
                if ds.FrameOfReferenceUID not in ALL_FOR_UIDS:
                    ALL_FOR_UIDS[ds.FrameOfReferenceUID] = generate_uid(args.org_root)

                ds.FrameOfReferenceUID = ALL_FOR_UIDS[ds.FrameOfReferenceUID]

            if 'SOPInstanceUID' in ds:
                ds.SOPInstanceUID = generate_uid(args.org_root)

                if hasattr(ds, 'file_meta'):
                    ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID

            opath = fpath
            if args.nb:
                opath += '.orig'

            ds.save_as(opath, write_like_original=False)
        except Exception as exc:
            bad_files.append(fpath)

# Print out the files that were not updated
if bad_files:
    msg = "The following files were not updated:\n"
    msg += '\n  '.join(bad_files)
    print(msg)
