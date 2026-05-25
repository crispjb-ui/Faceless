from __future__ import annotations

import os
import tempfile

# Point the app at throwaway, isolated storage BEFORE any faceless import reads
# settings (all reads are lazy/at-runtime, so setting env here is sufficient).
_TMP = tempfile.mkdtemp(prefix="faceless_test_")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_TMP}/test.sqlite")
os.environ.setdefault("OUTPUT_DIR", os.path.join(_TMP, "output"))
os.environ.setdefault("FACELESS_NICHE", "self_improvement")
os.environ.setdefault("MUSIC_LIBRARY_DIR", os.path.join(_TMP, "music"))
