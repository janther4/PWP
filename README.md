# PWP SPRING 2026
# WEBSTORE API
# Group information
* Student 1. Jani Nivalainen jnivalai19@student.oulu.fi
* Student 2. Reko Tornberg rtornber21@students.oamk.fi

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
flask --app webstore run --host 127.0.0.1 --port 5000
```

### Run Client

```powershell
python client.py
```

Entry point: `http://127.0.0.1:5000/`  
API base: `http://127.0.0.1:5000/api/`
Client UI: `http://127.0.0.1:5000/client/`

## Auxiliary service:
- `auxiliary_service.py` provides `GET /summary/` and reads data from the main REST API
- Start in a second terminal:
  ```powershell
  python auxiliary_service.py
  ```
- Local URL: `http://127.0.0.1:5001/summary/`

## Dependencies (external libraries)
- Flask
- Flask-RESTful
- Flask-SQLAlchemy
- jsonschema
- requests
- PySide6
- pytest
- pytest-cov
- coverage
- pylint
- black
- isort

## Run tests

### Functional REST API tests

```powershell
.\scripts\run_functional_tests.ps1
```

or

```powershell
python -m pytest -v test/test_rest_api_functional.py
```

### Auxiliary service tests

```powershell
python -m pytest -v test/test_auxiliary_service.py
```

### All tests

```powershell
.\scripts\run_all_tests.ps1
```

or

```powershell
python -m pytest -v test
```

## Functional testing summary
- Functional test suite: `test/test_rest_api_functional.py`
- Each test case is commented to describe what is being tested.
- The suite includes forced error inputs and validates API error responses.

Main error scenarios validated by functional tests:
- `415 Unsupported media type` when payload is not JSON.
- `400 Invalid JSON document` when input violates schema.
- `404 Not found` when referenced resources do not exist.
- `409 Conflict` for duplicate values or insufficient stock.

## REST client plugin input/output examples

### Create user (success)
- Method: `POST`
- URL: `http://127.0.0.1:5000/api/users/`
- Input:
  ```json
  {
    "email": "maija.mehilainen@example.com",
    "name": "Maija Mehiläinen"
  }
  ```
- Expected output:
  - Status: `201 Created`
  - Header: `Location: /api/users/{id}/`

### Create user (error: duplicate email)
- Method: `POST`
- URL: `http://127.0.0.1:5000/api/users/`
- Input:
  ```json
  {
    "email": "maija.mehilainen@example.com",
    "name": "Matti Meikäläinen"
  }
  ```
- Expected output:
  - Status: `409 Conflict`
  - Body includes `@error` details.

### Create product (error: invalid price)
- Method: `POST`
- URL: `http://127.0.0.1:5000/api/products/`
- Input:
  ```json
  {
    "sku": "SKU-NEG-001",
    "product_name": "Invalid Product",
    "price": -1.0
  }
  ```
- Expected output:
  - Status: `400 Bad Request`
  - Body includes validation error details.

### Auxiliary summary (success)
- Method: `GET`
- URL: `http://127.0.0.1:5001/summary/`
- Expected output:
  - Status: `200 OK`
  - JSON with `counts`, `metrics`, and `source_api_base`.

## Server settings (condensed)
- Hosting: Hetzner VPS, Ubuntu 24.04.3 LTS
- Hostname: `ubuntu-4gb-hel1-1`
- Public IPv4: `62.238.24.78`
- IPv6: `2a01:4f9:c015:49ac::1`
- Management: SSH on port `22`

## Network and ports (condensed)
- Open/used ports:
  - `22` SSH
  - `80` HTTP (Nginx)
  - `443` HTTPS
  - `5000` application/Docker
  - `5001` Docker auxiliary
- Docker forwards server ports `5000` and `5001` to containers.
- Nginx listens on port `80` and can proxy traffic to the application.

## Firewall (UFW, condensed)
- UFW is active.
- Default policy:
  - Incoming: deny
  - Outgoing: allow
- Allowed ports (IPv4 + IPv6):
  - `22/tcp`
  - `80/tcp`
  - `443/tcp`
  - `5000/tcp`

## DNS (condensed)
- DNS is managed outside the server (for example domain registrar or Cloudflare).
- A record should point to: `62.238.24.78`
- AAAA record can point to: `2a01:4f9:c015:49ac::1`

## Run with Docker

### Build and start:

```powershell
docker compose up --build
```

### Run in background:

```powershell
docker compose up --build -d
```

### Stop:

```powershell
docker compose down
```


