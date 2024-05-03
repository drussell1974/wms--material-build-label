# man-material_build_label

SKU label including Bill of Material

## dependencies

sudo apt install python3.10

python -m venv material-build-label
venv\Scripts\activate

python -m pip install fitz
python -m pip install pandas

## test

cd test
python3 -m unittest test_component_JobCardDocument.py

## build

### for linux
### for windows

## deploy

### for linux

Choose python

### Windows Client

"Installing Python on a windows client"

Download the installer

https://www.python.org/downloads/release/python-31014/

## virtualenv

### for linux

Install virtual environment

> pip install virtualenv

### for Windows

Select pip when installing python using the installer

### Create a virtual environment

### for linux

> cd <root>/src/teacher_web/

> mkdir -p .venv/django

> virtualenv -p [python executable] .venv/django

> source .venv/django/bin/activate

### for Windows

> cd <root>/src/teacher_web/

> mkdir -p .venv/django

> python -m venv c:\path\to\myenv

> source .venv/django/Scripts/activate

# folder structure

'''
-   <SOLUTION>
    - build
        - <application>.cmd
    - releases
        - <application>_v1.0
        - <application>_v2.2
        ...
    - src
        - <application>     
            - app               (UI)
            - models            (BLL)
            - dataaccess        (DAL)
    - test
        - data
        - unit
'''

# REFERENCES

Virtual Environment A Primer - https://realpython.com/python-virtual-environments-a-primer/
