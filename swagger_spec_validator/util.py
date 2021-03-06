import json
import logging
import urllib2

from swagger_spec_validator import validator12, validator20
from swagger_spec_validator.common import SwaggerValidationError, TIMEOUT_SEC


log = logging.getLogger(__name__)


def get_validator(spec_json, origin='unknown'):
    """
    :param spec_json: Dict representation of the json API spec
    :param origin: filename or url of the spec - only use for error messages
    :return: module responsible for validation based on Swagger version in the
        spec
    """
    swagger12_version = spec_json.get('swaggerVersion')
    swagger20_version = spec_json.get('swagger')

    if swagger12_version and swagger20_version:
        raise SwaggerValidationError(
            "You've got conflicting keys for the Swagger version in your spec. "
            "Expected `swaggerVersion` or `swagger`, but not both.")
    elif swagger12_version and swagger12_version == '1.2':
        # we don't care about versions prior to 1.2
        return validator12
    elif swagger20_version and swagger20_version == '2.0':
        return validator20
    elif swagger12_version is None and swagger20_version is None:
        raise SwaggerValidationError(
            "Swagger spec {0} missing version. Expected "
            "`swaggerVersion` or `swagger`".format(origin))
    else:
        raise SwaggerValidationError(
            'Swagger version {0} not supported.'.format(
                swagger12_version or swagger20_version))


def validate_spec_url(spec_url):
    """Validates a Swagger spec given its URL.

    :param spec_url:
      For Swagger 1.2, this is the URL to the resource listing in api-docs.
      For Swagger 2.0, this is the URL to swagger.json in api-docs.
    """
    spec_json = json.load(urllib2.urlopen(spec_url, TIMEOUT_SEC))
    validator = get_validator(spec_json, spec_url)
    validator.validate_spec_url(spec_url)
