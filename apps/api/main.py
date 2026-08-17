from fastapi import FastAPI

from gps import __version__

app = FastAPI(title="Governed Support Platform", version=__version__)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    """Side-effect-free local readiness endpoint."""
    return {"status": "ok", "version": __version__}
