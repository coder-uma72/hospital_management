from io import BytesIO
from urllib.parse import parse_qs


class MethodOverrideMiddleware:

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):

        if environ.get("REQUEST_METHOD") != "POST":
            return self.app(environ, start_response)

        content_type = environ.get("CONTENT_TYPE", "")

        if "application/x-www-form-urlencoded" not in content_type:
            return self.app(environ, start_response)

        content_length = environ.get("CONTENT_LENGTH")

        if not content_length:
            return self.app(environ, start_response)

        length = int(content_length)

        body = environ["wsgi.input"].read(length)

        form_data = parse_qs(
            body.decode("utf-8")
        )

        method = form_data.get("_method", [None])[0]

        if method:
            environ["REQUEST_METHOD"] = method.upper()

        # Put the body back so Flask can read the form normally
        environ["wsgi.input"] = BytesIO(body)

        return self.app(environ, start_response)