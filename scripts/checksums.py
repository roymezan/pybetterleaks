from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

RELEASE_ARTIFACT_SUFFIXES = (".whl", ".tar.gz")


def main() -> None:
    args = parse_args()
    root = Path(args.directory)
    if not root.exists():
        raise SystemExit(f"directory does not exist: {root}")

    if args.verify is not None:
        verify_checksums(root, Path(args.verify))
        return

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = root / output_path

    output_resolved = output_path.resolve()
    files = sorted(
        path
        for path in root.iterdir()
        if path.is_file() and path.resolve() != output_resolved and is_release_artifact(path.name)
    )
    if not files:
        raise SystemExit(f"no release artifacts found in {root}")

    lines = [f"{sha256(path)}  {path.name}" for path in files]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate SHA256SUMS for release artifacts.")
    parser.add_argument("directory", help="Directory containing release artifacts.")
    parser.add_argument(
        "--verify",
        default=None,
        help="Verify an existing SHA256SUMS file instead of writing one.",
    )
    parser.add_argument(
        "--output",
        default="SHA256SUMS",
        help="Output path. Relative paths are resolved inside the artifact directory.",
    )
    return parser.parse_args()


def verify_checksums(root: Path, checksum_path: Path) -> None:
    if not checksum_path.is_absolute():
        checksum_path = root / checksum_path
    if not checksum_path.exists():
        raise SystemExit(f"checksum file does not exist: {checksum_path}")

    entries = parse_checksum_file(checksum_path)
    if not entries:
        raise SystemExit(f"checksum file is empty: {checksum_path}")

    expected_names = {name for _, name in entries}
    checksum_resolved = checksum_path.resolve()
    actual_names = {
        path.name
        for path in root.iterdir()
        if path.is_file()
        and path.resolve() != checksum_resolved
        and is_release_artifact(path.name)
    }
    extra_files = actual_names - expected_names
    missing_files = expected_names - actual_names
    if extra_files:
        raise SystemExit(f"files missing from checksum file: {sorted(extra_files)!r}")
    if missing_files:
        raise SystemExit(f"checksummed files missing from directory: {sorted(missing_files)!r}")

    for expected_hash, name in entries:
        path = root / name
        actual_hash = sha256(path)
        if actual_hash != expected_hash:
            raise SystemExit(
                f"checksum mismatch for {name}: expected {expected_hash}, got {actual_hash}"
            )

    print(f"Verified {len(entries)} checksum(s) from {checksum_path}")


def parse_checksum_file(path: Path) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            raise SystemExit(f"{path}:{line_number}: invalid checksum line")
        digest, filename = parts
        if len(digest) != 64 or any(char not in "0123456789abcdef" for char in digest):
            raise SystemExit(f"{path}:{line_number}: invalid sha256 digest")
        filename = filename.strip()
        if Path(filename).name != filename:
            raise SystemExit(f"{path}:{line_number}: checksum filename must not contain paths")
        if not is_release_artifact(filename):
            raise SystemExit(f"{path}:{line_number}: checksum filename is not a release artifact")
        entries.append((digest, filename))
    return entries


def is_release_artifact(filename: str) -> bool:
    return filename.endswith(RELEASE_ARTIFACT_SUFFIXES)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


if __name__ == "__main__":
    main()
