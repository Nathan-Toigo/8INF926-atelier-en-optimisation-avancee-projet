import uvicorn

from api import app


def run_server(host: str = "0.0.0.0", port: int = 8000) -> None:
	uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
	run_server()
