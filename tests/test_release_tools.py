from __future__ import annotations

import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_inspect_wheels_accepts_native_platform_wheel(tmp_path: Path) -> None:
    wheel = tmp_path / "pybetterleaks-0.5.0-cp313-cp313-macosx_11_0_arm64.whl"
    write_wheel(
        wheel,
        native_name="pybetterleaks/native/libbetterleaks_py.dylib",
        tag="cp313-cp313-macosx_11_0_arm64",
        version="0.5.0",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "inspect_wheels.py"),
            str(tmp_path),
            "--expected-version",
            "0.5.0",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Inspected 1 wheel" in result.stdout


def test_inspect_wheels_accepts_py3_none_platform_wheel(tmp_path: Path) -> None:
    wheel = tmp_path / "pybetterleaks-0.5.0-py3-none-manylinux_2_28_x86_64.whl"
    write_wheel(
        wheel,
        native_name="pybetterleaks/native/libbetterleaks_py.so",
        tag="py3-none-manylinux_2_28_x86_64",
        version="0.5.0",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "inspect_wheels.py"),
            str(tmp_path),
            "--expected-version",
            "0.5.0",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Inspected 1 wheel" in result.stdout


def test_inspect_wheels_accepts_compressed_platform_tags(tmp_path: Path) -> None:
    wheel = (
        tmp_path
        / "pybetterleaks-0.5.0-cp313-cp313-manylinux1_x86_64."
        "manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl"
    )
    write_wheel(
        wheel,
        native_name="pybetterleaks/native/libbetterleaks_py.so",
        tags=[
            "cp313-cp313-manylinux1_x86_64",
            "cp313-cp313-manylinux_2_28_x86_64",
            "cp313-cp313-manylinux_2_5_x86_64",
        ],
        version="0.5.0",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "inspect_wheels.py"),
            str(tmp_path),
            "--expected-version",
            "0.5.0",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert "Inspected 1 wheel" in result.stdout


def test_inspect_wheels_rejects_universal_wheel(tmp_path: Path) -> None:
    wheel = tmp_path / "pybetterleaks-0.5.0-py3-none-any.whl"
    write_wheel(
        wheel,
        native_name="pybetterleaks/native/libbetterleaks_py.so",
        tag="py3-none-any",
        version="0.5.0",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "inspect_wheels.py"),
            str(tmp_path),
            "--expected-version",
            "0.5.0",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "must not be universal" in result.stderr


def test_checksums_verify_round_trip(tmp_path: Path) -> None:
    (tmp_path / "artifact.whl").write_bytes(b"wheel bytes")
    (tmp_path / ".gitignore").write_text("*\n", encoding="utf-8")
    checksum_path = tmp_path / "SHA256SUMS"

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "checksums.py"),
            str(tmp_path),
            "--output",
            "SHA256SUMS",
        ],
        check=True,
    )
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "checksums.py"),
            str(tmp_path),
            "--verify",
            "SHA256SUMS",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert checksum_path.exists()
    assert "Verified 1 checksum" in result.stdout
    assert ".gitignore" not in checksum_path.read_text(encoding="utf-8")


def test_checksums_verify_detects_mismatch(tmp_path: Path) -> None:
    (tmp_path / "artifact.whl").write_bytes(b"wheel bytes")
    (tmp_path / "SHA256SUMS").write_text(
        "0" * 64 + "  artifact.whl\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "checksums.py"),
            str(tmp_path),
            "--verify",
            "SHA256SUMS",
        ],
        capture_output=True,
        text=True,
    )

    assert result.returncode != 0
    assert "checksum mismatch" in result.stderr


def write_wheel(
    path: Path,
    *,
    native_name: str,
    version: str,
    tag: str | None = None,
    tags: list[str] | None = None,
) -> None:
    metadata_tags = tags or [tag]
    if any(metadata_tag is None for metadata_tag in metadata_tags):
        raise AssertionError("write_wheel requires tag or tags")

    dist_info = f"pybetterleaks-{version}.dist-info"
    with zipfile.ZipFile(path, "w") as wheel:
        wheel.writestr("pybetterleaks/__init__.py", "")
        wheel.writestr("pybetterleaks/py.typed", "")
        wheel.writestr(native_name, b"native")
        wheel.writestr(
            f"{dist_info}/WHEEL",
            "\n".join(
                [
                    "Wheel-Version: 1.0",
                    "Root-Is-Purelib: false",
                    *(f"Tag: {metadata_tag}" for metadata_tag in metadata_tags),
                    "",
                ]
            ),
        )
