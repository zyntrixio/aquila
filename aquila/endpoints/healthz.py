from typing import TYPE_CHECKING

import requests

from azure.storage.blob import BlobServiceClient
from flask import Blueprint

from aquila.settings import BLOB_CONTAINER, BLOB_STORAGE_DSN, POLARIS_HOST

if TYPE_CHECKING:
    from azure.storage.blob import BlobClient

bp = Blueprint("healthz", __name__)


@bp.get("/livez")
def livez() -> tuple[dict, int]:
    return {}, 200


@bp.get("/readyz")
def readyz() -> tuple[dict, int]:
    errors: dict = {}

    try:
        blob_name = "healthz"
        blob_service_client: BlobServiceClient = BlobServiceClient.from_connection_string(BLOB_STORAGE_DSN)
        blob: "BlobClient" = blob_service_client.get_blob_client(BLOB_CONTAINER, blob_name)
        assert blob.exists(), "blob does not exists"
    except Exception as ex:  # pylint: disable=broad-except
        errors["azure-blob-storage"] = f"failed to retrieve '{blob_name}' from '{BLOB_CONTAINER}': {repr(ex)}"

    try:
        url = f"{POLARIS_HOST}/livez"
        resp = requests.get(url, timeout=(3.05, 10))
        resp.raise_for_status()
    except Exception as ex:  # pylint: disable=broad-except
        errors["polaris-request"] = f"failed to contact polaris at {url}: {repr(ex)}"

    return errors, 500 if errors else 200
