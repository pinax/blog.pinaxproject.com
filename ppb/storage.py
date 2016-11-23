import base64
import json
import os

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from gapc_storage.storage import GoogleCloudStorage
from oauth2client.client import SERVICE_ACCOUNT
from oauth2client.service_account import ServiceAccountCredentials


class ECGoogleCloudStorage(GoogleCloudStorage):
    """
    Custom subclass of GoogleCloudStorage to interact with Eldarion Cloud

    To create:

        ec instances env GCS_CREDENTIALS=$(cat key.json | base64) GCS_BUCKET=<bucket>

    """

    path_prefix = settings.MEDIA_PREFIX

    def get_oauth_credentials(self):
        client_credentials = json.loads(base64.b64decode(os.environ["GCS_CREDENTIALS"]))
        if client_credentials["type"] == SERVICE_ACCOUNT:
            creds = ServiceAccountCredentials.from_json_keyfile_dict(client_credentials)
        else:
            raise ImproperlyConfigured("non-service accounts are not supported")
        return self.create_scoped(creds)