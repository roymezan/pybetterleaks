#!/usr/bin/env bash
set -euo pipefail

GO_VERSION="${GO_VERSION:-1.26.5}"
ARCH="$(uname -m)"

case "${ARCH}" in
  x86_64)
    GO_ARCH="amd64"
    ;;
  aarch64|arm64)
    GO_ARCH="arm64"
    ;;
  *)
    echo "Unsupported Linux architecture for Go install: ${ARCH}" >&2
    exit 1
    ;;
esac

CACHE_DIR="${PYBETTERLEAKS_GO_DIST_CACHE:-${PWD}/.cache/go-dist}"
TARBALL="${CACHE_DIR}/go${GO_VERSION}.linux-${GO_ARCH}.tar.gz"

mkdir -p "${CACHE_DIR}"
if [ ! -s "${TARBALL}" ]; then
  TMP_TARBALL="${TARBALL}.tmp"
  curl -fsSL "https://go.dev/dl/go${GO_VERSION}.linux-${GO_ARCH}.tar.gz" -o "${TMP_TARBALL}"
  mv "${TMP_TARBALL}" "${TARBALL}"
fi

rm -rf /usr/local/go
tar -C /usr/local -xzf "${TARBALL}"
/usr/local/go/bin/go version
