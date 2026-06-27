import ssl

import certifi
from django.core.mail.backends.smtp import EmailBackend as SMTPEmailBackend
from django.utils.functional import cached_property


class EmailBackend(SMTPEmailBackend):
    """SMTP backend that uses certifi's CA bundle for TLS verification."""

    @cached_property
    def ssl_context(self):
        if self.ssl_certfile or self.ssl_keyfile:
            ssl_context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.load_cert_chain(self.ssl_certfile, self.ssl_keyfile)
            return ssl_context
        return ssl.create_default_context(cafile=certifi.where())
