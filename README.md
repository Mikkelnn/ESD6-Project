# ESD6-Project

This is the code repo for 6th semester project for Electronics and Systemdesign

## Modules

Each module has its own directory where it is as selfcontained as possible.

First `cd` to the desired module and wollow directions in README.md

### Python modules

If a folder contains Python code, a virtual enviorment must be used within the folder named '.venv'

0. Fix execution policy in Powershell
   - Windows: `Set-ExecutionPolicy unrestricted`

1. Intall virtial enviorment (if not alredy):

   - Windows: `py -m pip install virtualenv`
   - Linux: `pip install virtualenv`

2. If not already created, create the virtual enviorment:

   - Windows: `py -m venv .venv`
   - Linux: `python3 -m venv .venv`

3. Activate the virtual enviorment:

   - Windows: `.venv\Scripts\activate`
   - Linux: `source .venv/bin/activate`

4. Install packages listed in associated README.md

   - Windows: `py -m pip install <modules>`
   - Linux: `pip install <modules>`

5. To deactivate the enviorment (after use):
   - Windows: `deactivate`
   - Linux: `source .venv/bin/deactivate`
