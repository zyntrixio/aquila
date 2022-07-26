import logging

from os.path import splitext
from typing import TYPE_CHECKING, Any

from azure.storage.blob import BlobServiceClient

from aquila.settings import BLOB_CONTAINER, BLOB_STORAGE_DSN, FETCH_TEMPLATES

if TYPE_CHECKING:
    from azure.storage.blob import ContainerClient


class TemplateLoader:
    _templates: dict = {}

    def __init__(self) -> None:
        self.dont_fetch_templates = False

        if not FETCH_TEMPLATES:
            self.dont_fetch_templates = True
            return

        try:
            self.container_name = BLOB_CONTAINER
            self.logger = logging.getLogger("template-loader")

            # type hints are still somewhat broken for BlobServiceClient
            blob_service_client: Any = BlobServiceClient.from_connection_string(BLOB_STORAGE_DSN, logger=self.logger)
            self.container_client: "ContainerClient" = blob_service_client.get_container_client(self.container_name)
            self._load_templates()
        except Exception:  # pylint: disable=broad-except
            self.dont_fetch_templates = True
            self.logger.exception(
                (
                    "Error while trying to load templates from blob storage's container '%s', "
                    "deactivating TemplateLoader and falling back to default.html"
                ),
                BLOB_CONTAINER,
            )

    def _load_templates(self) -> None:
        self.logger.info("loading aquila templates from '%s'", self.container_name)

        for blob in self.container_client.list_blobs():
            if blob.name == "healthz":
                continue

            blob_client = self.container_client.get_blob_client(blob.name)
            template_slug, extension = splitext(blob.name)
            if extension == ".html":
                try:
                    content = blob_client.download_blob().readall()
                    if isinstance(content, bytes):
                        content = content.decode("utf-8")

                    self._templates[template_slug] = content
                except (AttributeError, UnicodeDecodeError):
                    self.logger.exception(
                        "failed to decode file '%s' from container '%s'", blob.name, self.container_name
                    )
            else:
                self.logger.warning(
                    "invalid html file '%s' found in '%s' container, skipping.", blob.name, self.container_name
                )

        self.logger.info("loaded template slugs: %s", list(self._templates))

    def get_template(self, template_slug: str) -> str | None:
        if self.dont_fetch_templates:
            self.logger.debug("FETCH_TEMPLATES set to %s, returning None", FETCH_TEMPLATES)
            return None

        self.logger.debug("available templates: %s, requested: %s", list(self._templates), template_slug)
        template = self._templates.get(template_slug)
        if not template:
            self.logger.info("template slug '%s' not found, trying to load templates again", template_slug)
            self._load_templates()
            template = self._templates.get(template_slug)

        return template


template_loader = TemplateLoader()
