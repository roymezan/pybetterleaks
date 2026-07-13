from __future__ import annotations

import argparse
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

PACKAGE_NAME = "pybetterleaks"
NATIVE_PREFIX = f"{PACKAGE_NAME}/native/"
NATIVE_SUFFIXES = (".dll", ".dylib", ".so")


@dataclass(frozen=True)
class WheelName:
    path: Path
    distribution: str
    version: str
    python_tag: str
    abi_tag: str
    platform_tag: str


def main() -> None:
    args = parse_args()
    root = Path(args.directory)
    if not root.exists():
        raise SystemExit(f"directory does not exist: {root}")

    wheels = sorted(root.glob("*.whl"))
    if not wheels:
        raise SystemExit(f"no wheel files found in {root}")

    expected_version = args.expected_version or read_project_version()
    for wheel in wheels:
        inspect_wheel(
            wheel,
            package_name=args.package_name,
            expected_version=expected_version,
        )

    print(f"Inspected {len(wheels)} wheel(s) in {root}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Inspect PyBetterleaks wheel artifacts.")
    parser.add_argument("directory", help="Directory containing wheel artifacts.")
    parser.add_argument("--package-name", default=PACKAGE_NAME)
    parser.add_argument("--expected-version", default=None)
    return parser.parse_args()


def inspect_wheel(
    path: Path,
    *,
    package_name: str = PACKAGE_NAME,
    expected_version: Optional[str] = None,
) -> None:
    name = parse_wheel_name(path)
    expected_distribution = normalize_distribution(package_name)
    if normalize_distribution(name.distribution) != expected_distribution:
        raise SystemExit(f"{path.name}: expected distribution {package_name!r}")
    if expected_version is not None and name.version != expected_version:
        raise SystemExit(f"{path.name}: expected version {expected_version}, got {name.version}")
    if name.platform_tag == "any":
        raise SystemExit(f"{path.name}: native wheels must not be universal")
    if "musllinux" in name.platform_tag:
        raise SystemExit(f"{path.name}: musllinux wheels are not supported")

    with zipfile.ZipFile(path) as wheel:
        entries = set(wheel.namelist())
        require_entry(path, entries, f"{package_name}/py.typed")
        require_entry(path, entries, dist_info_path(name, "WHEEL"))

        native_entries = [
            entry
            for entry in entries
            if entry.startswith(f"{package_name}/native/") and entry.endswith(NATIVE_SUFFIXES)
        ]
        if len(native_entries) != 1:
            raise SystemExit(
                f"{path.name}: expected exactly one native library, got {sorted(native_entries)!r}"
            )
        native_entry = native_entries[0]
        native_info = wheel.getinfo(native_entry)
        if native_info.file_size <= 0:
            raise SystemExit(f"{path.name}: native library is empty: {native_entry}")
        if not native_suffix_matches_platform(native_entry, name.platform_tag):
            raise SystemExit(
                f"{path.name}: native library suffix does not match platform: {native_entry}"
            )

        forbidden_headers = [
            entry for entry in entries if entry.startswith(NATIVE_PREFIX) and entry.endswith(".h")
        ]
        if forbidden_headers:
            raise SystemExit(f"{path.name}: native headers must not ship: {forbidden_headers!r}")

        wheel_metadata = wheel.read(dist_info_path(name, "WHEEL")).decode("utf-8")
        if "Root-Is-Purelib: false" not in wheel_metadata:
            raise SystemExit(f"{path.name}: WHEEL metadata must mark Root-Is-Purelib as false")
        expected_tag = f"Tag: {name.python_tag}-{name.abi_tag}-{name.platform_tag}"
        if expected_tag not in wheel_metadata:
            raise SystemExit(f"{path.name}: WHEEL metadata is missing {expected_tag!r}")


def parse_wheel_name(path: Path) -> WheelName:
    if path.suffix != ".whl":
        raise SystemExit(f"not a wheel file: {path}")
    parts = path.name[:-4].split("-")
    if len(parts) < 5:
        raise SystemExit(f"invalid wheel filename: {path.name}")
    return WheelName(
        path=path,
        distribution=parts[0],
        version=parts[1],
        python_tag=parts[-3],
        abi_tag=parts[-2],
        platform_tag=parts[-1],
    )


def require_entry(path: Path, entries: set[str], entry: str) -> None:
    if entry not in entries:
        raise SystemExit(f"{path.name}: missing {entry}")


def dist_info_path(name: WheelName, filename: str) -> str:
    return f"{name.distribution}-{name.version}.dist-info/{filename}"


def native_suffix_matches_platform(native_entry: str, platform_tag: str) -> bool:
    if platform_tag.startswith("macosx"):
        return native_entry.endswith(".dylib")
    if platform_tag.startswith("win"):
        return native_entry.endswith(".dll")
    if "linux" in platform_tag:
        return native_entry.endswith(".so")
    return False


def normalize_distribution(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def read_project_version() -> str:
    pyproject = Path(__file__).resolve().parents[1] / "pyproject.toml"
    for line in pyproject.read_text(encoding="utf-8").splitlines():
        if line.startswith("version = "):
            return line.split("=", 1)[1].strip().strip('"')
    raise RuntimeError(f"could not find project version in {pyproject}")


if __name__ == "__main__":
    main()
