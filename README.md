# PWP SPRING 2026
# WEBSTORE API
# Group information
* Student 1. Jani Nivalainen jnivalai19@students.oulu.fi
* Student 2. Reko Tornberg rtornber21@studenst.oamk.fi


__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint, instructions on how to setup and run the client, instructions on how to setup and run the axiliary service and instructions on how to deploy the api in a production environment__

# Quick start

## Create and activate venv (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## Install dependencies:

```powershell
pip install -r requirements.txt
```

## Seed database:

```powershell
python test\mockdata.py
```

## Run API and client:

### Run Flask API

```powershell
flask --app webstore run
```

### Run Client

```powershell
python client.py
```


Entry point: `http://127.0.0.1:5000/`  
API base: `http://127.0.0.1:5000/api/`
Client UI: `http://127.0.0.1:5000/client/`


