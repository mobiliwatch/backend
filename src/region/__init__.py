from region.isere import Isere

_instances = (
    Isere(),
)

# Helpers for Models
ALL = [(r.slug, str(r)) for r in _instances]
DEFAULT = _instances[0].slug  # isere
