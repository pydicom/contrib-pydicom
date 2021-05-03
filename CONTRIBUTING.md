
# Contributing to contrib-pydicom

This is the summary for contributing code to the pydicom contribution
repository, contrib-pydicom. This repository is intended for scripts and examples to
supplement pydicom. If your contribution is intended to modify or enhance the core
of pydicom, you should consider contribution to the [pydicom](https://www.github.com/pydicom/pydicom)
main repository. Please read it carefully to help making the code review process go as
smoothly as possible and maximize the likelihood of your contribution being
merged.

## Steps to Contribute

1. Add your contribution script(s) to the appropriate topic folder, either as a script or subfolder (see below)
2. Make sure you have provided some documentation (usage, details of the implementation), and your Github or email to give credit for authorship.
3. Add a link to the contribution script or folder in it's appropriate topic folder `README.md` 


## Contribution Structure

You will notice topic folders in the base of the repo, and these coincide with the examples
that pydicom provides:

- [databases](databases): databases specific for pydicom, or using pydicom in databases
- [input-output](input_output): working with different file formats, or anything related to io, input, or output
- [metadata-processing](metadata-processing): manipulation of image headers and metadata 
- [plotting-visualization](plotting-visualization): visualization of pydicom data, not including traditional medical viewers
- [viewers](viewers): traditional (medical) viewers that work with pydicom


For your contribution, you have two options. You can either add a single script to any of the subfolders, eg:

```
input-output/
    dicom2nifti.py
```

in which case you would write usage, your contact (Github username or email if others have issue) and general documentation for your contribution. In the case that your contribution has many files and is more extensive than a single script example, you can add a subfolder under the topic:

```
input-output/
    dicom2nifti/
        main.py
        README.md
```

and this will give you substantial more options to provide documentation, and multiple scripts.

Currently, we will maintain a single level hierarchy, meaning that topics should all be on the first level, and subfolders should be contained contributions.


## Documentation

It is important if a future user has questions about your contribution that
he or she is able to contact you. We are encouraging of contributions to
include documentation, which should be done in a README.md associated with
the subfolder, or for smaller (single) scripts, in the top comment header of the
file.

## How to contribute

The preferred workflow for contributing to pydicom is to fork the
[main repository](https://github.com/pydicom/contrib-pydicom) on
GitHub, clone, and develop on a branch. Steps:

1. Fork the [project repository](https://github.com/pydicom/contrib-pydicom)
   by clicking on the 'Fork' button near the top right of the page. This creates
   a copy of the code under your GitHub user account. For more details on
   how to fork a repository see [this guide](https://help.github.com/articles/fork-a-repo/).

2. Clone your fork of the `contrib-pydicom` repo from your GitHub account to your local disk:

   ```bash
   $ git clone git@github.com:YourLogin/contrib-pydicom.git
   $ cd contib-pydicom
   ```

3. Create a ``feature`` branch to hold your development changes:

   ```bash
   $ git checkout -b my-feature
   ```

   Always use a ``feature`` branch. It's good practice to never work on the ``master`` branch!

4. Develop the feature on your feature branch. Add changed files using ``git add`` and then ``git commit`` files:

   ```bash
   $ git add modified_files
   $ git commit
   ```

   to record your changes in Git, then push the changes to your GitHub account with:

   ```bash
   $ git push -u origin my-feature
   ```

5. Follow [these instructions](https://help.github.com/articles/creating-a-pull-request-from-a-fork)
to create a pull request from your fork. This will send an email to the committers.

(If any of the above seems like magic to you, please look up the
[Git documentation](https://git-scm.com/documentation) on the web, or ask a friend or another contributor for help.)

## Pull Request Checklist

We recommend that your contribution complies with the following rules before you
submit a pull request:

-  Follow the
   [coding-guidelines](https://pydicom.github.io/pydicom/stable/tutorials/contributing_code.html).

-  Use, when applicable, the validation tools and scripts in the
   `pydicom.util` submodule.

-  If your pull request addresses an issue with another contribution, 
   please use the pull request title to describe the issue and mention 
   the issue number in the pull request
   description. This will make sure a link back to the original issue is
   created. Use "closes #PR-NUM" or "fixes #PR-NUM" to indicate github to
   automatically close the related issue. Use any other keyword (i.e: works on,
   related) to avoid github to close the referenced issue.

-  All public methods should have informative docstrings with sample
   usage presented as doctests when appropriate.

-  Please prefix the title of your pull request with `[MRG]` (Ready for Merge),
   if the contribution is complete and ready for a detailed review. Two core
   developers will review your code and change the prefix of the pull request to
   `[MRG + 1]` on approval, making it eligible for merging. An incomplete
   contribution -- where you expect to do more work before receiving a full
   review -- should be prefixed `[WIP]` (to indicate a work in progress) and
   changed to `[MRG]` when it matures. WIPs may be useful to: indicate you are
   working on something to avoid duplicated work, request broad review of
   functionality or API, or seek collaborators. WIPs often benefit from the
   inclusion of a
   [task list](https://github.com/blog/1375-task-lists-in-gfm-issues-pulls-comments)
   in the PR description.

-  The documentation should also include expected time and space
   complexity of the algorithm and scalability, e.g. "this algorithm
   can scale to a large number of samples > 100000, but does not
   scale in dimensionality: n_features is expected to be lower than
   100".

You can also check for common programming errors with the following
tools:

-  Code with good unittest **coverage** (at least 80%), check with:

  ```bash
  $ pip install pytest pytest-cov
  $ py.test --cov=pydicom path/to/test_for_package
  ```

-  No pyflakes warnings, check with:

  ```bash
  $ pip install pyflakes
  $ pyflakes path/to/module.py
  ```

-  No PEP8 warnings, check with:

  ```bash
  $ pip install pep8
  $ pep8 path/to/module.py
  ```

-  AutoPEP8 can help you fix some of the easy redundant errors:

  ```bash
  $ pip install autopep8
  $ autopep8 path/to/pep8.py
  ```

Bonus points for contributions that include a performance analysis with
a benchmark script and profiling output (please report on the mailing
list or on the GitHub issue).

## Filing bugs

We use Github issues to track all bugs and feature requests; feel free to
open an issue if you have found a bug or wish to see a feature implemented.

It is recommended to check that your issue complies with the
following rules before submitting:

-  Verify that your issue is not being currently addressed by other
   [issues](https://github.com/pydicom/contrib-pydicom/issues?q=)
   or [pull requests](https://github.com/pydicom/contrib-pydicom/pulls?q=).

-  Please ensure all code snippets and error messages are formatted in
   appropriate code blocks.
   See [Creating and highlighting code blocks](https://help.github.com/articles/creating-and-highlighting-code-blocks).

-  Please include your operating system type and version number, as well
   as your Python, pydicom and numpy versions. This information
   can be found by running the following code snippet:

  ```python
  import platform; print(platform.platform())
  import sys; print("Python", sys.version)
  import numpy; print("numpy", numpy.__version__)
  import pydicom; print("pydicom", pydicom.__version__)
  ```

-  please include a [reproducible](http://stackoverflow.com/help/mcve) code
   snippet or link to a [gist](https://gist.github.com). If an exception is
   raised, please provide the traceback. (use `%xmode` in ipython to use the
   non beautified version of the trackeback)


## New contributor tips

A great way to start contributing to pydicom is to pick an item
from the list of [Easy issues](https://github.com/pydicom/pydicom/issues?labels=Easy)
in the issue tracker. Resolving these issues allow you to start
contributing to the project without much prior knowledge. Your
assistance in this area will be greatly appreciated by the more
experienced developers as it helps free up their time to concentrate on
other issues.
