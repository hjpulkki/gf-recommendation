# Introduction
Buhlmann ZHL-16C is commonly used in diving computers with gradient factor parameters. Selecting these parameters is not that straight forward, and same parameters should not be used for all diving profiles. This project aims to guide users to select the correct parameters for their planned dive.

If you are just looking to use the tool, you can access the planning app [in heroku](https://gf-recommendation-b3ee67272911.herokuapp.com/)

You can check out the [main notebook with nbviewer](https://nbviewer.org/github/hjpulkki/gf-recommendation/blob/main/notebooks/GF_recommendation.ipynb).

Bulmann calculations are done with [pydplan](https://github.com/hjpulkki/pydplan), which has been added as a submodule. My fork has some needed functionality that the original version from eianlei does not have.

## Installation

If you are using windows, do yourself a favor and [install WSL](https://learn.microsoft.com/en-us/windows/wsl/install). After that you can follow the steps you would use in Linux.

### Install environment

You need python 3.13, and [poetry](https://python-poetry.org/docs/) 2.0.1 from

Install python environment with poetry
`poetry install`

## Run code

### Jupyter notebooks

Run jupyter notebook

`poetry run jupyter notebook`

You can now navigate to the notebooks dictionary and run the notebooks yourself.

### Dash app

You can start the dash application with command

`poetry run python -m src.app`

Follow the instructions and open a browser to use the app

## Deploy to Heroku

Install Heroku

`curl https://cli-assets.heroku.com/install.sh | sh`

Login to Heroku. Follow instructions and create an account if you don't already have one

`heroku login`

Push the Docker image to Heroku:

`heroku create`

Release the app:

`git push heroku main`

Open the app:
`heroku open`


# Disclaimer

I'm just a guy on the internet writing some code, so you shoudn't this as the only source to plan your dive.
