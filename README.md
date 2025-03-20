# Introduction
Buhlmann ZHL-16C is commonly used in diving computers with gradient factor parameters. Selecting these parameters is not that straight forward, and same parameters should not be used for all diving profiles. This project aims to guide users to select the correct parameters for their planned dive.

If you are just looking to use the tool, you can access the [Planning app](http://ec2-54-152-31-232.compute-1.amazonaws.com/) on AWS.

You can check out the [main notebook with nbviewer](https://nbviewer.org/github/hjpulkki/gf-recommendation/blob/main/notebooks/GF_recommendation.ipynb).

Bulmann calculations are done with [pydplan](https://github.com/hjpulkki/pydplan), which has been added as a submodule. My fork has some needed functionality that the original version from eianlei does not have.

## Installation

If you are using windows, do yourself a favor and [install WSL](https://learn.microsoft.com/en-us/windows/wsl/install). After that you can follow the steps you would use in Linux.

### Install environment

You need python 3.13, and [poetry](https://python-poetry.org/docs/) 2.0.1 from

Install python environment with poetry
`poetry install`

Make sure you also clone the submodules before trying to run the code
`git submodule update --init --recursive`

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

## Build docker and run as a service

`sudo docker build -t gf-server .`

Test that it works

`sudo docker run -p 80:8050 gf-server`

Create service

`sudo cp gf-server.service /etc/systemd/system/gf-server.service`

`sudo systemctl daemon-reload`
`sudo systemctl enable gf-server`
`sudo systemctl restart gf-server`

# Disclaimer

I'm just a guy on the internet writing some code, so you shoudn't this as the only source to plan your dive.
