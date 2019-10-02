import os
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = "postgresql://ed_user:ed_pass@localhost/stardrive_test"

TESTING = True
CORS_ENABLED = True
DEBUG = False
DEVELOPMENT = False
MASTER_URL = "http://localhost:5000"
MASTER_EMAIL = "daniel.h.funk@gmail.com"
MASTER_PASS = "dfunk7"

MIRRORING = False
DELETE_RECORDS = False

ELASTIC_SEARCH = {
    "index_prefix": "stardrive_test",
    "hosts": ["localhost"],
    "port": 9200,
    "timeout": 20,
    "verify_certs": False,
    "use_ssl": False,
    "http_auth_user": "",
    "http_auth_pass": ""
}

#: Default attribute map for single signon.
# This makes it a little easier to spoof the values that come back from
# Shibboleth.  One of the aspects of constructing custom headers is that
# they are automatically converted to META Keys, so we have to refer
# to them as that when pulling them out.  This is slightly different from
# the structure that actually comes back from Shibboleth.
SSO_ATTRIBUTE_MAP = {
    'HTTP_EPPN': (True, 'eppn'),  # dhf8r@virginia.edu
    'HTTP_UID': (False, 'uid'), # dhf8r
    'HTTP_GIVENNAME': (False, 'givenName'), # Daniel
    'HTTP_MAIL': (False, 'email')  # dhf8r@Virginia.EDU
}

GOOGLE_MAPS_API_KEY = "TEST_API_KEY_GOES_HERE"