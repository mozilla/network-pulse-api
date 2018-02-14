from rest_framework.versioning import URLPathVersioning
from rest_framework import exceptions


class PulseAPIVersioning(URLPathVersioning):
    def determine_version(self, request, *args, **kwargs):
        """
        We override the super class' determine_version function because
        we want the version in the url to be optional. The difference between the
        functions is that along with using the default version if
        the version_param IS NOT present in the kwargs, we also use
        the default version if the version_param IS present in the kwargs
        but is None. Hence, if a version is not specified in the url, the version_param
        is passed in the kwargs but is set to None and will result in the
        version being set to the default_version.

        See https://groups.google.com/forum/#!topic/django-rest-framework/r7s9M-VQX_k
        for information on whether DRF will do this on its own.
        """
        version = kwargs.get(self.version_param, self.default_version)
        if version is None:
            version = self.default_version

        if not self.is_allowed_version(version):
            raise exceptions.NotFound(self.invalid_version_message)

        return version
