import urllib2
import cgi

from google.appengine.ext import blobstore
from google.appengine.api import app_identity

from argeweb.libs import wtforms
from argeweb.core import settings


class Upload(object):
    """
    Automatically handles file upload fields that need to use the blobstore/cloud storage.

    With the default configuration, this will upload to the application's default Google Cloud Storage bucket. This behavior is configurable in ``app/settings.py``.

    This works by:

     * Detecting if you're on an add or edit action (you can add additional actions with ``upload_actions``, or set ``process_uploads`` to True)
     * Adding the ``upload_url`` template variable that points to the blobstore / cloud storage.
     * Updating the ``form_action`` and ``form_encoding`` scaffolding variables to use the new upload url.
     * Processing uploads when the upload handler redirects back to your action.
     * Adding each upload's key to the form data so that it can be saved to the model.

    Does not require that the controller subclass ``BlobstoreUploadHandler``, however to serve blobs you must
    either use the built-in Download controller or create a custom controller that subclasses ``BlobstoreDownloadHandler``.
    """

    def __init__(self, controller):
        self.controller = controller
        self.__uploads = None
        self.process_uploads = False
        self.upload_actions = ('add', 'edit')
        if not hasattr(self.controller.meta, 'upload_actions'):
            setattr(self.controller.meta, 'upload_actions', ('add', 'edit',))
        self.cloud_storage_bucket = controller.Meta.cloud_storage_bucket if hasattr(controller.Meta, 'cloud_storage_bucket') else None

        if not self.cloud_storage_bucket and settings.get('upload').get('use_cloud_storage'):
            self.cloud_storage_bucket = settings.get('upload', {}).get('bucket') or app_identity.get_default_gcs_bucket_name()

        controller.events.before_startup += self.on_before_startup
        controller.events.scaffold_before_apply += self.on_scaffold_before_apply
        controller.events.after_dispatch += self.on_after_dispatch

    def on_before_startup(self, controller):
        if controller.route.action in controller.meta.upload_actions:
            self.process_uploads = True

    def on_scaffold_before_apply(self, controller, container, item):
        if self.process_uploads and isinstance(container, wtforms.Form):
            self.process(container)

    def on_after_dispatch(self, controller, response):
        """
        This will additionally check if ?start is the query string. If so, it will return just the upload url. This is
        great for rest apis.
        """
        if self.process_uploads:
            if not 'upload_url' in controller.context:
                controller.context.set(upload_url=self.generate_upload_url())
                if hasattr(controller, 'scaffold'):
                    controller.scaffold.form_action = controller.context['upload_url']
                    controller.scaffold.form_encoding = 'multipart/form-data'

            if 'start' in controller.request.params:
                if not response:
                    controller.context['data'] = controller.context['upload_url']
                    if 'json' in controller.components:
                        controller.components.json.render()

    def process(self, form, item=None):
        """
        Process all of the incoming file upload and populates the current model form with them.

        Additionally, if using cloudstorage and there is a field present with the name
        "x_cloud_storage" that corresponds to the file, then the cloud storage object
        name will be saved to that field.
        """
        uploads = self.get_uploads()
        for field in [x for x in form if isinstance(x, wtforms.fields.FileField)]:
            files = uploads.get(field.name)
            if files and files[0]:
                getattr(form, field.name).data = files[0].key()
                if hasattr(form, "%s_cloud_storage" % field.name):
                    getattr(form, "%s_cloud_storage" % field.name).data = files[0].cloud_storage.gs_object_name
            #else:
            #    delattr(form, field.name)

    def generate_upload_url(self, uri=None):
        url = urllib2.unquote(uri if uri else self.controller.request.uri)

        return blobstore.create_upload_url(
            success_path=url,
            gs_bucket_name=self.cloud_storage_bucket)

    def serve(self, item, property):
        if not item:
            return 404

        self.controller.send_blob(getattr(item, property))

        return self.controller.response

    def get_uploads(self):
        """Get all uploads sent to this controller.

        Returns:
        A dictionary mapping field names to a list of blobinfo objects. This blobinfos
        will have an additional cloud_storage property if they have been uploaded
        to cloud storage but be aware that this will not be persisted.
        """
        if self.__uploads is None:
            self.__uploads = {}
            for key, value in self.controller.request.params.items():
                if isinstance(value, cgi.FieldStorage):
                    if 'blob-key' in value.type_options:
                        blob_info = blobstore.parse_blob_info(value)
                        cloud_info = blobstore.parse_file_info(value)

                        # work around mangled names
                        blob_info = blobstore.BlobInfo.get(blob_info.key())

                        # Add cloud storage data
                        setattr(blob_info, 'cloud_storage', cloud_info)

                        self.__uploads.setdefault(key, []).append(blob_info)

        return self.__uploads
