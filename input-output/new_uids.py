#!/usr/bin/env python
"""Recursively search a directory for DICOM datasets and generate new and
consistent UIDs for the following top-level elements:

* (0020,000D) Study Instance UID (without --series)
* (0020,000E) Series Instance UID
* (0008,0018) SOP Instance UID
* (0020,0052) Frame of Reference UID (without --series or with --force-for)

Possible uses:

* Changing the UIDs of CT studies prior to importing them into a system in
  which the original datasets have already been imported.
"""

from __future__ import print_function

import argparse
import os
import shutil
import sys

from pydicom import dcmread
from pydicom.uid import generate_uid, PYDICOM_ROOT_UID, UID


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
            "(0020,000E) 'Series Instance UID', (0008,0018) "
            "'SOP Instance UID' and (0020,0052) 'Frame of Reference UID' "
        ),
    )

    parser.add_argument(
        'directory',
        type=str,
        help="The path to the directory containing the datasets",
    )
    parser.add_argument(
        '-nb',
        action='store_true',
        help="Don't create a backup of the original datasets",
        default=False,
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
    parser.add_argument(
        '--uid-length',
        type=int,
        help=(
            "Limit the generated UID lengths to the specified number of "
            "characters (maximum 64)"
        ),
        default=64,
    )
    parser.add_argument(
        '--series',
        action='store_true',
        help=(
            "Generate new UIDs at the Series level rather than the Study "
            "level (i.e. only change (0020,000E) 'Series Instance UID' and "
            "(0008,0018) 'SOP Instance UID')"
        ),
        default=False,
    )
    parser.add_argument(
        '--force-for',
        action='store_true',
        help=(
            "With --series, force a new (0020,0052) 'Frame of Reference UID' "
            "value"
        ),
        default=False,
    )

    return parser


args = setup_argparse().parse_args()


# Dicts to translate from the original to the new UIDs
ALL_STUDY_UIDS = {}
ALL_SERIES_UIDS = {}
ALL_FOR_UIDS = {}


def _generate_uids(org_root, length):
    """Return a generated pydicom UID with `length` characters."""
    uid = UID(generate_uid(args.org_root)[:length])
    if not uid.is_valid:
        sys.exit("Unable to generate valid UIDs with the supplied arguments")

    return uid


# Recursively search the specified directory
all_fpath = []
for root, dirs, files in os.walk(args.directory):
    for fname in files:
        # The full path to each file
        all_fpath.append(os.path.abspath(os.path.join(root, fname)))

# Try and open all the files as DICOM
bad_files = []
for fpath in all_fpath:
    if os.path.isfile(fpath):
        try:
            ds = dcmread(fpath, force=True)

            if not args.series and 'StudyInstanceUID' in ds:
                if ds.StudyInstanceUID not in ALL_STUDY_UIDS:
                    ALL_STUDY_UIDS[ds.StudyInstanceUID] = _generate_uids(
                        args.org_root, args.uid_length
                    )

                ds.StudyInstanceUID = ALL_STUDY_UIDS[ds.StudyInstanceUID]

            if 'SeriesInstanceUID' in ds:
                if ds.SeriesInstanceUID not in ALL_SERIES_UIDS:
                    ALL_SERIES_UIDS[ds.SeriesInstanceUID] = _generate_uids(
                        args.org_root, args.uid_length
                    )

                ds.SeriesInstanceUID = ALL_SERIES_UIDS[ds.SeriesInstanceUID]

            # Frame of Reference may be related to one or more Series
            #   so a new Study UID requires a new FoR UID (Part 3, A.1.2.5)
            if (not args.series or args.force_for) and 'FrameOfReferenceUID' in ds:
                if ds.FrameOfReferenceUID not in ALL_FOR_UIDS:
                    ALL_FOR_UIDS[ds.FrameOfReferenceUID] = _generate_uids(
                        args.org_root, args.uid_length
                    )

                ds.FrameOfReferenceUID = ALL_FOR_UIDS[ds.FrameOfReferenceUID]

            if 'SOPInstanceUID' in ds:
                ds.SOPInstanceUID = _generate_uids(args.org_root,
                                                   args.uid_length)

                if hasattr(ds, 'file_meta'):
                    ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID

            if not args.nb:
                shutil.copy(fpath, "{}.orig".format(fpath))

            ds.save_as(fpath, write_like_original=False)
        except Exception as exc:
            bad_files.append(fpath)

# Print out the files that were not updated
if bad_files:
    msg = "The following files were not updated:\n"
    msg += '\n  '.join(bad_files)
    print(msg)
