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