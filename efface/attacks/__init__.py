"""Attack catalogue: one interface, one module per tactic.

Importing the package registers every tactic, so ``available()`` and ``get()``
cover the catalogue. Model-backed tactics are built through `factory.build`,
which is where the chat model and the filler are injected.
"""

from efface.attacks import local, mlm, model  # noqa: F401  (registration)
from efface.attacks.base import Attack, available, get, register
from efface.attacks.factory import LOCAL, MODEL_BACKED, build, needs_model

__all__ = [
    "Attack",
    "LOCAL",
    "MODEL_BACKED",
    "available",
    "build",
    "get",
    "needs_model",
    "register",
]
