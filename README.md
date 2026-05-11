# PWP SPRING 2026
# PROJECT NAME
# Group information
* Student 1. Name and email
* Student 2. Name and email
* Student 3. Name and email
* Student 4. Name and email

__Remember to include all required documentation and HOWTOs, including how to create and populate the database, how to run and test the API, the url to the entrypoint, instructions on how to setup and run the client, instructions on how to setup and run the axiliary service and instructions on how to deploy the api in a production environment__

## Quick start (dev)

1. Create and activate venv (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Seed database:

```powershell
python test\mockdata.py
```

4. Run API:

```powershell
flask --app webstore run
```

Entry point: `http://127.0.0.1:5000/`  
API base: `http://127.0.0.1:5000/api/`
Client UI: `http://127.0.0.1:5000/client/`


