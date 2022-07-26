import logging

from os.path import splitext
from typing import TYPE_CHECKING, Any

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient

from app.settings import BLOB_CONTAINER, BLOB_STORAGE_DSN, FETCH_TEMPLATES

if TYPE_CHECKING:
    from azure.storage.blob import ContainerClient


class TemplateLoader:
    _templates: dict = {}

    def __init__(self) -> None:

        if not FETCH_TEMPLATES:
            return

        self.container_name = BLOB_CONTAINER
        self.logger = logging.getLogger("template-loader")

        # type hints are still somewhat broken for BlobServiceClient
        self.blob_service_client: Any = BlobServiceClient.from_connection_string(BLOB_STORAGE_DSN, logger=self.logger)
        try:
            self.blob_service_client.create_container(self.container_name)
            self.logger.info("created container '%s'.", self.container_name)
        except ResourceExistsError:
            self.logger.debug("container '%s' already exists.", self.container_name)

        self.container_client: "ContainerClient" = self.blob_service_client.get_container_client(self.container_name)
        self._load_templates()

    def _load_templates(self) -> None:
        self.logger.info("loading aquila templates from '%s'", self.container_name)

        for blob in self.container_client.list_blobs():
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

    def get_template(self, template_slug: str) -> str | None:
        if not FETCH_TEMPLATES:
            self.logger.debug("FETCH_TEMPLATES set to %s, returning None", FETCH_TEMPLATES)
            return None

        self.logger.debug("available templates: %s, requested: %s", self._templates, template_slug)
        template = self._templates.get(template_slug)
        if not template:
            self.logger.info("template slug '%s' not found, trying to load templates again", template_slug)
            self._load_templates()
            template = self._templates.get(template_slug)

        return template


template_loader = TemplateLoader()
