"""Compatibility entry point: regenerate verified tables into a new directory.

Status reports are curated technical documentation. The earlier generator is
preserved in audit/ and run snapshots. It emitted outdated access/test claims.
"""
from finalize_results import main

if __name__ == '__main__':
    raise SystemExit(main())
