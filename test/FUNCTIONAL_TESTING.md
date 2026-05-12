# REST API Functional Testing

## What is included
- `test/test_rest_api_functional.py`
  - HTTP-level functional tests for `/api/users/`, `/api/products/`, and `/api/orders/`
  - Success scenarios and forced error scenarios (`400`, `404`, `409`, `415`)
  - Each test case is commented in code with the scenario being tested

## External libraries used
- `pytest`
- `Flask` test client (`app.test_client()`)

## Scripts to run tests
- Functional tests only:
  - `.\scripts\run_functional_tests.ps1`
- All tests under `test/`:
  - `.\scripts\run_all_tests.ps1`
