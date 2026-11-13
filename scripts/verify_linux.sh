#!/bin/sh
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
image=${KLEAN_PYTHON_IMAGE:-python:3.10-slim}

docker run --rm \
  -v "$repo_root:/work:ro" \
  -w /work \
  -e PYTHONDONTWRITEBYTECODE=1 \
  "$image" \
  sh -c '
    set -eu
    uname -a
    cat /etc/os-release
    python3 --version
    python3 -m unittest discover -s tests -v
    python3 -m klean examples/report_examples.kln
  '
