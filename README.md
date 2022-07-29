# Aquila
Microsite for providing access to reward's info to the end user.


## Install
- `poetry install`
- create `.env` or .`settings.ini` file in the root folder and fill in the required env vars from `aquila/settings.py`

## Running (DEV)
- Polaris API must be running and the `POLARIS_HOST` env var should point to it.
- `BLOB_STORAGE_DSN` env var must be provided
- `poetry run python wsgi.py`

## Usage
- send http `GET` request to `[host][port]/reward?retailer=[retailer_slug]$reward=[reward_uuid]`

## NB:
- Aquila's `/readyz` endpoint will check for the existance of a `heathz` file in the blob storage and will try to contact polaris' `/livez` endpoint.
- Aquila implements dynamic versioning so please leave the `__version__` set to `"0.0.0"`