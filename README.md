# contrib-pydicom

`contrib-pydicom` is a library of contributions, including extra modules, example scripts, viewers, and small applications
to supplement the [pydicom](https://www.github.com/pydicom/pydicom) repository.  For complete details, read about [how to contribute](CONTRIBUTING.md). We will review quickly what a contribution looks like:


## What is a Contribution?
This repository is intended for scripts and examples to
supplement pydicom. This might be a single script showing how to convert from dicom to nifti, or a set of scripts that uses pydicom to perform some image processing task. If your contribution is intended to modify or enhance the core
of pydicom, you should consider contribution to the [pydicom core](https://www.github.com/pydicom/pydicom)
main repository. 

## Contribution Structure

You will notice topic folders in the base of the repo, and these generally coincide with the examples
that pydicom provides:

- [databases](databases): databases specific for pydicom, or using pydicom in databases
- [input-output](input-output): working with different file formats, or anything related to io, input, or output
- [metadata-processing](metadata-processing): manipulation of image headers and metadata 
- [plotting-visualization](plotting-visualization): visualization of pydicom data, not including traditional medical viewers
- [viewers](viewers): traditional (medical) viewers that work with pydicom

And of course if there is a folder that is not yet created that would be desired for your contribution, you should add it via pull request (PR). For your contribution, you have two options. 

### Option 1: Single Script
You can either add a single script to any of the subfolders, eg:

```
input-output/
    dicom2nifti.py
```

in which case you would write usage, your contact (Github username or email if others have issue) and general documentation for your contribution. 

### Option 2: Subfolder
In the case that your contribution has many files and is more extensive than a single script example, you can add a subfolder under the topic:

```
input-output/
    dicom2nifti/
        main.py
        README.md
```

and this will give you substantial more options to provide documentation, and multiple scripts.


Currently, we will maintain a single level hierarchy, meaning that topics should all be on the first level, and subfolders should be contained contributions. If you have any questions, please [file an issue](https://www.github.com/pydicom/contrib-python).
