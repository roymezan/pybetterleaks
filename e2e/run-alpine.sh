#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IMAGE="${PYBETTERLEAKS_E2E_ALPINE_IMAGE:-pybetterleaks-e2e:alpine}"
PYTHON_IMAGE="${PYBETTERLEAKS_E2E_ALPINE_PYTHON_IMAGE:-python:3.13-alpine}"

BUILD_ARGS=(
  --build-arg "PYTHON_IMAGE=${PYTHON_IMAGE}" \
  -f "${ROOT}/e2e/Dockerfile.alpine" \
  -t "${IMAGE}" \
  "${ROOT}"
)

if [[ "${PYBETTERLEAKS_DOCKER_GHA_CACHE:-}" == "1" ]]; then
  CACHE_SCOPE="${PYBETTERLEAKS_DOCKER_CACHE_SCOPE:-${IMAGE//[^A-Za-z0-9_.-]/-}}"
  docker buildx build \
    --load \
    --cache-from "type=gha,scope=${CACHE_SCOPE}" \
    --cache-to "type=gha,mode=max,scope=${CACHE_SCOPE}" \
    "${BUILD_ARGS[@]}"
else
  docker build "${BUILD_ARGS[@]}"
fi

docker run --rm "${IMAGE}"
