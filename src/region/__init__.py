from __future__ import absolute_import
from region.isere import Isere

_instances = (
    Isere(),
)

# Helpers for Models
ALL = [(r.slug, str(r)) for r in _instances]
DEFAULT = _instances[0].slug  # isere

def get(name):
    """
    Get a loaded Region instance
    """
    out = dict([(i.slug, i) for i in _instances])
    if name not in out:
        raise Exception('No region {}'.format(name))
    return out[name]
