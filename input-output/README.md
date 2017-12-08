# Input Output

These examples pertain to transformation of data, or reading inputs, or writing outputs.

 - [pydicom_series.py](pydicom_series.py): example of reading in series directories, specifically for gated data, in which case a DicomSeries instance is created for each 3D volume.

 - [dicom_zip_reader.py](dicom_zip_reader.py): example of reading a set of dicom files from a zip/tar/tgz file. A list of filenames and file-like objects is returned.

 - [dicom_model/dicom_dir.py](dicom_dir.py): example of reading a set of dicom files into a patient/study/series/image hierarchy
