"""
Back to the Basics

Path is Model. Storage is Inference. Glob is Query.

The filesystem is not storage. It is a circuit.
"""

try:
    from .coherence import Coherence
except ImportError:
    # Fallback for direct execution
    from coherence import Coherence  # type: ignore

__version__ = "0.2.0"
__all__ = ["Coherence"]
