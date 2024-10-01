from flask import Flask, g, request


class HTMX:
    def init_app(self, app: Flask):
        @app.before_request
        def is_htmx():
            g.htmx = request.headers.get("HX-Request")
