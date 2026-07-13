# Install Pathview Plus

*Page 2 of 14*

On this page, you will create a small project folder and install the software
used by every example.

## Words used on this page

- **Python** is the programming language used to run Pathview Plus.
- **Package** is reusable Python software that you install into a project.
- **Terminal** is the text window where you type commands.
- **Project folder** is the folder that will hold your data, scripts, and images.
- **Virtual environment** is a private Python setup for one project.

## 1. Check Python

If Python is not installed yet, use the beginner download instructions at
[python.org](https://www.python.org/downloads/), then return to this page.

Open Terminal on macOS or Linux, or PowerShell on Windows. Type:

```bash
python3 --version
```

On Windows, this command may be:

```powershell
python --version
```

The guide uses Python 3.10 or newer. A version such as `Python 3.12.4` is ready
to use.

## 2. Create a project folder

Type these commands one at a time:

```bash
mkdir my-pathview-project
cd my-pathview-project
```

What the commands mean:

- `mkdir` creates a new folder named `my-pathview-project`.
- `cd` moves Terminal into that folder.

Your files will stay together inside this folder.

## 3. Create a virtual environment

On macOS or Linux:

```bash
python3 -m venv .venv
```

On Windows:

```powershell
python -m venv .venv
```

The command creates a folder named `.venv`. That folder holds this project's
Python packages.

## 4. Activate the environment

On macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

When the environment is active, the beginning of the Terminal line usually
shows `(.venv)`.

## 5. Install the packages

Type:

```bash
python -m pip install "pathview-plus==2.0.2" polars
```

This command has four pieces:

| Piece | Meaning |
| --- | --- |
| `python -m pip` | use Python's package installer |
| `install` | add packages to the environment |
| `pathview-plus==2.0.2` | install the Pathview Plus version used here |
| `polars` | install the table library used by the examples |

## 6. Check the installation

Type:

```bash
python -c "from pathview import pathview; print('Pathview Plus is ready')"
```

You should see:

```text
Pathview Plus is ready
```

## Your project at this point

```text
my-pathview-project/
└── .venv/
```

On the next page, you will add two small Python files and create your first
image.

## Returning to the project later

Each time you open a new Terminal window, move into the project folder and
activate the environment again.

On macOS or Linux:

```bash
cd my-pathview-project
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
cd my-pathview-project
.\.venv\Scripts\Activate.ps1
```

[<- Previous: Before you begin](01-before-you-begin.md) | [Home](../README.md) | [Next: Make your first pathway ->](03-first-pathway.md)
