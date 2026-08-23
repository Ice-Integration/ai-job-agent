from app.api import app
from app.core.observability import configure_observability

configure_observability()

__all__ = ["app"]
