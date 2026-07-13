from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Optional

from .models import ScanError, ScanResult


class PyBetterleaksError(Exception):
    """Base exception for PyBetterleaks errors."""


class NativeLibraryError(PyBetterleaksError):
    """Raised when the native Betterleaks bridge cannot be used."""


class NativeLibraryNotFoundError(NativeLibraryError):
    """Raised when no bundled native library exists for the current platform."""

    def __init__(self, *, path: Path, system: str, machine: str) -> None:
        self.path = path
        self.system = system
        self.machine = machine
        super().__init__(
            "Missing bundled Betterleaks native library for "
            f"{system or 'unknown'} {machine or 'unknown'}: {path}. "
            "Build it with `uv run python scripts/build_native.py` or install a "
            "wheel matching this platform."
        )


class NativeCallError(NativeLibraryError):
    """Raised when a native call fails before a structured scan response exists."""


class ConfigFormatError(PyBetterleaksError, ValueError):
    """Raised when a typed Betterleaks config cannot be serialized safely."""


class ScanFailedError(PyBetterleaksError):
    """Raised when a scan returns structured Betterleaks errors."""

    def __init__(
        self,
        errors: Sequence[ScanError],
        *,
        result: Optional[ScanResult] = None,
    ) -> None:
        self.errors = tuple(errors)
        self.result = result
        self.primary_error = self.errors[0] if self.errors else None
        self.code = self.primary_error.code if self.primary_error is not None else "scan_failed"
        super().__init__(_format_scan_errors(self.errors))


class ScanConfigError(ScanFailedError):
    """Raised when Betterleaks cannot load or initialize scan configuration."""


class ScanTargetError(ScanFailedError):
    """Raised when the scan target is invalid or cannot be inspected."""


class ScanTimeoutError(ScanFailedError):
    """Raised when a scan times out."""


class UnsupportedScanError(ScanFailedError):
    """Raised when the native bridge reports an unsupported scan mode or scope."""


class InvalidScanRequestError(ScanFailedError):
    """Raised when the native bridge rejects a malformed scan request."""


class NativeScanError(ScanFailedError):
    """Raised for structured native scan failures without a more specific class."""


def scan_exception_from_result(result: ScanResult) -> ScanFailedError:
    """Build the most specific exception for a failed scan result."""
    if result.ok:
        raise ValueError("cannot build a scan exception for a successful ScanResult")
    exception_type = _exception_type_for_errors(result.errors)
    return exception_type(result.errors, result=result)


def raise_for_errors(result: ScanResult) -> ScanResult:
    """Return a scan result or raise a typed exception for structured scan errors."""
    if not result.ok:
        raise scan_exception_from_result(result)
    return result


def _exception_type_for_errors(errors: Sequence[ScanError]) -> type[ScanFailedError]:
    if not errors:
        return NativeScanError
    code = errors[0].code
    if code in {"detector_init_failed", "config_load_failed"}:
        return ScanConfigError
    if code in {"target_stat_failed", "target_not_directory", "target_not_git_repository"}:
        return ScanTargetError
    if code in {"invalid_timeout", "scan_timeout"}:
        return ScanTimeoutError
    if code in {"unsupported_mode", "unsupported_git_scope"}:
        return UnsupportedScanError
    if code in {"invalid_request", "invalid_json", "scan_not_found"}:
        return InvalidScanRequestError
    return NativeScanError


def _format_scan_errors(errors: Sequence[ScanError]) -> str:
    if not errors:
        return "Betterleaks scan failed"
    return "; ".join(_format_scan_error(error) for error in errors)


def _format_scan_error(error: ScanError) -> str:
    message = f"{error.code}: {error.message}"
    return f"{message}: {error.detail}" if error.detail else message
