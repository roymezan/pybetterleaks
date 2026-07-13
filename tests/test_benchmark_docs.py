from __future__ import annotations

from pathlib import Path

import pytest

from scripts import update_benchmark_docs


def test_replace_managed_section_updates_benchmark_block() -> None:
    docs = "\n".join(
        [
            "# Benchmarks",
            "",
            "Intro.",
            "",
            update_benchmark_docs.START_MARKER,
            "old table",
            update_benchmark_docs.END_MARKER,
            "",
            "Outro.",
            "",
        ]
    )
    benchmark = "\n".join(
        [
            "# PyBetterleaks Benchmark Results",
            "",
            "- Betterleaks: `v1.6.1`",
            "",
            "| Case | Mean |",
            "| --- | ---: |",
            "| pybetterleaks.scan_text | 0.10 ms |",
        ]
    )

    updated = update_benchmark_docs.replace_managed_section(
        docs,
        benchmark,
        source_label="benchmark-results/checkout-benchmark.md",
    )

    assert "old table" not in updated
    assert "### PyBetterleaks Benchmark Results" in updated
    assert "Source: benchmark-results/checkout-benchmark.md" in updated
    assert "| pybetterleaks.scan_text | 0.10 ms |" in updated
    assert updated.endswith("\nOutro.\n")


def test_replace_managed_section_rejects_missing_markers() -> None:
    with pytest.raises(ValueError, match="must contain"):
        update_benchmark_docs.replace_managed_section(
            "# Benchmarks\n",
            "# Report\n",
            source_label="report.md",
        )


def test_replace_managed_section_rejects_reversed_markers() -> None:
    docs = "\n".join(
        [
            update_benchmark_docs.END_MARKER,
            "content",
            update_benchmark_docs.START_MARKER,
        ]
    )

    with pytest.raises(ValueError, match="must appear after"):
        update_benchmark_docs.replace_managed_section(
            docs,
            "# Report\n",
            source_label="report.md",
        )


def test_format_managed_section_escapes_html_comment_breaks() -> None:
    section = update_benchmark_docs.format_managed_section(
        "# Report",
        source_label="bad --> source",
    )

    assert "bad - -> source" in section


def test_cli_check_detects_stale_docs(tmp_path: Path) -> None:
    docs = tmp_path / "benchmarks.md"
    report = tmp_path / "report.md"
    docs.write_text(
        "\n".join(
            [
                update_benchmark_docs.START_MARKER,
                "old",
                update_benchmark_docs.END_MARKER,
                "",
            ]
        ),
        encoding="utf-8",
    )
    report.write_text("# Report\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="is not current"):
        update_benchmark_docs.run([str(report), "--docs", str(docs), "--check"])
