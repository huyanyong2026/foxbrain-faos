from wsgiref.simple_server import make_server
from packages.vafox_foundation.http import service_app

app = service_app("memory")
if __name__ == "__main__":
    make_server("0.0.0.0", 8080, app).serve_forever()
