# Introduction
Buhlmann ZHL-16C is commonly used in diving computers with gradient factor parameters. Selecting these parameters is not that straight forward, and same parameters should not be used for all diving profiles. This project aims to guide users to select the correct parameters for their planned dive.

You can check out the [main notebook with nbviewer](https://nbviewer.org/github/hjpulkki/gf-recommendation/blob/main/notebooks/GF_recommendation.ipynb).

## Installation

If you are using windows, do yourself a favor and [install WSL](https://learn.microsoft.com/en-us/windows/wsl/install). After that you can follow the steps you would use in Linux.

### Clone pydplan

Move to the project folder and clone pydplan. It is used to calculate Buhlmann dive profiles. My fork has some needed functionality that the original version from eianlei does not have.

`git clone https://github.com/hjpulkki/pydplan.git`

### Install environment

You need python 3.13, and poetry 8.0 from https://python-poetry.org/docs/

Install python environment with poetry
`poetry install --no-root`

Run jupyter notebook

`poetry run jupyter notebook`

You can now navigate to the notebooks dictionary and run the notebooks yourself.

# Disclaimer

I'm just a guy on the internet writing some code, so you shoudn't this as the only source to plan your dive.
