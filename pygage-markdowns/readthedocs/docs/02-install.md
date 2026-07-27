# Install PyGAGE

*Page 2 of 31*

On this page, you will make a project folder, create a private Python
environment, and install the PyGAGE 1.2.1 source used by every example.

## Words used on this page

- **Terminal** is the text window used to enter commands.
- **Project folder** keeps the scripts, data, and results for one analysis.
- **Virtual environment** is a private collection of Python packages for that
  project.
- **Repository** is the official project folder stored on GitHub.
- **Package** is reusable Python software installed into an environment.

## 1. Check Python

Open Terminal on macOS or Linux, or PowerShell on Windows.

On macOS or Linux:

```bash
python3 --version
```

On Windows:

```powershell
python --version
```

PyGAGE supports Python 3.8 and newer. A result such as `Python 3.12.4` is
ready for the guide.

## 2. Check Git

Git downloads the official source repository:

```bash
git --version
```

If Git needs to be installed, follow the download instructions at
[git-scm.com](https://git-scm.com/downloads), then reopen Terminal or
PowerShell.

## 3. Create a project folder

Type these commands one at a time:

```bash
mkdir my-pygage-project
cd my-pygage-project
```

`mkdir` creates the folder. `cd` moves the Terminal session into it.

## 4. Create a virtual environment

On macOS or Linux:

```bash
python3 -m venv .venv
```

On Windows:

```powershell
python -m venv .venv
```

This creates a folder named `.venv` containing the private Python environment.

## 5. Activate the environment

On macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

An active environment usually displays `(.venv)` at the beginning of the
Terminal line.

## 6. Download the official PyGAGE repository

```bash
git clone https://github.com/raw-lab/pygage.git
```

This creates:

```text
my-pygage-project/
├── .venv/
└── pygage/
```

The `pygage` folder contains Dr. White's official source.

## 7. Select the source version used by this guide

Move into the downloaded repository:

```bash
cd pygage
```

Select the exact reviewed source:

```bash
git checkout 486e0b800778ec03fe03764aa9dccbe904cfd70b
```

This commit contains PyGAGE 1.2.1.

## 8. Install PyGAGE

```bash
python -m pip install .
```

The dot means “install the package from this folder.” The command also installs
the required table, statistics, plotting, and file-reading packages.

Install notebook support used on page 25:

```bash
python -m pip install jupyterlab
```

Install AnnData support only when your project uses an `.h5ad` object:

```bash
python -m pip install anndata
```

## 9. Return to the project folder

```bash
cd ..
```

Your Terminal is now inside `my-pygage-project`.

## 10. Check the installation

```bash
python -c "import pygage; print(pygage.__version__)"
```

The guide version prints:

```text
1.2.1
```

Check the command-line program:

```bash
pygage --help
```

The first line begins with:

```text
usage: pygage
```

## Returning to the project later

Each new Terminal window needs the environment activated again.

On macOS or Linux:

```bash
cd my-pygage-project
source .venv/bin/activate
```

On Windows:

```powershell
cd my-pygage-project
.\.venv\Scripts\Activate.ps1
```

## Installation checklist

You are ready when:

- the project contains `.venv` and `pygage`;
- the environment is active;
- the version command prints `1.2.1`; and
- `pygage --help` displays the command menu.

[<- Previous: Before you begin](01-before-you-begin.md) | [Home](index.md) | [Next: Run your first enrichment ->](03-first-enrichment.md)
