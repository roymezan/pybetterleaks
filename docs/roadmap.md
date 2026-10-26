# Roadmap

Updated October 27, 2026. The priorities below guide upcoming work; they are
planned, not shipped, and release numbers and dates remain open.

PyBetterleaks continues to focus on an importable Python SDK with bundled native
libraries, typed APIs, and in-process scanning. Contributions and proposals to
combine efforts are welcome. The priorities incorporate the
[upstream Python distribution discussion](https://github.com/betterleaks/betterleaks/issues/46)
and our review of
[betterleaks-py](https://github.com/as1605/betterleaks-py). Collaboration is being
[discussed](https://github.com/roymezan/pybetterleaks/issues/6); no merger or shared
maintenance arrangement has been agreed.

## Next Release: Engine Refresh And Performance Baseline

- Upgrade the bundled Betterleaks engine from `v1.6.1` to a verified current
  stable release, updating module checksums, bridge code, and version docs.
- Prove compatibility for typed configuration, validation, redaction, structured
  errors, timeouts, and async cancellation. Add fixtures for newly supported
  detections and run Python, Go, wheel, and Docker E2E release checks.
- Measure default-rule scans as well as the existing synthetic-rule benchmark.
  Separate process startup, first-scan setup, and repeated calls; include clean
  and secret-containing inputs, directories, large inputs, and large result sets.
- Assess upstream v2 API, configuration, and finding-model changes before
  committing to a reusable scanner API or freezing our public API for v1.0.
  A stable-engine update does not imply adopting a prerelease engine.

## Following Priorities: Reuse And Platform Coverage

- Investigate reusable compiled configuration or an explicit `Scanner` object,
  using the baseline above to establish whether it improves repeated scans.
- Preserve per-call validation settings, redaction, deadlines, and cancellation.
  Define concurrency safety, bounded resource use, cleanup, and config-change
  invalidation before introducing caching.
- Add repeated-scan, concurrent-scan, cancellation, and memory-growth checks.
  Repeated scans without a crash alone do not establish that memory is bounded.
- Promote Linux arm64 manylinux wheels from the long-term backlog. Evaluate a
  native ARM CI runner and require installed-wheel smoke tests and a no-Go Docker
  runtime check before documenting support.

## Design Work: Newer Findings And Terminal Usage

- Plan additive Python access to upstream v2 confidence, correlated component
  sets, encoding information, and structured match details where supported.
  Preserve existing finding fields and verify nested secrets are redacted.
- Evaluate distributing the upstream CLI to serve terminal, `uvx`, and `pipx`
  workflows. Decide between bundling it with the SDK and a companion
  distribution before implementation; installation commands remain undecided.
- If a CLI is distributed, align its engine version with the SDK, expose version
  information clearly, and test command arguments, exit codes, platform assets,
  checksums, and license notices. Preserve in-process execution for SDK scans.
- Document Python and terminal workflows separately once terminal support ships.

## Path To v1.0

Complete the engine compatibility assessment and settle any public scanner/model
API changes before an API freeze. Then follow the
[v1.0 readiness checklist](https://github.com/roymezan/pybetterleaks/blob/main/docs/v1-readiness.md),
run a release-candidate rehearsal, and validate real usage before declaring the
API stable. CLI distribution and Linux arm64 support do not block v1.0.

## Deferred

- Streaming scan result APIs for very large scans.
- Git history/diff scopes and GitHub/GitLab/Hugging Face/S3 source wrappers.
- Further Alpine/musllinux work until there is a credible fix for the Go/musl
  shared-library loader failure.
- SBOM generation, additional artifact signing, and a cross-platform benchmark
  dashboard, subject to the release-readiness decisions.

## Released Milestones

The sections below record the features delivered through v0.6.

## v0.1

- `scan_text`
- `scan_dir`
- `betterleaks_version`
- Typed dataclass results
- Self-contained platform wheels
- GitHub Actions wheel builds

## v0.2

- Typed `BetterleaksConfig`, `Rule`, `Extend`, `Expr`, and `RequiredRule`
  dataclasses.
- Programmatic config serialization for `scan_text` and `scan_dir`.
- Async `scan_text_async` and `scan_dir_async` wrappers with native
  cooperative cancellation.
- Validation env var bridging for Betterleaks Expr validators.
- Native scan tests against a curated fake-secret fixture suite.
- Reproducible synthetic benchmarks with an optional Betterleaks CLI baseline.
- Release artifact checksums.
- Better wheel smoke coverage for typed config and async.
- Musllinux/Alpine investigation. Official wheels are unsupported and remain
  blocked by the current Go/musl `initial-exec TLS` loader failure.

See [v0.2 plan](https://github.com/roymezan/pybetterleaks/blob/main/docs/v0.2-plan.md) for implementation details and acceptance
criteria.

## v0.3

- Git worktree scan mode for local repository workflows, with tracked/staged
  scopes planned only if they can preserve the no-runtime-subprocess promise.
- Release hardening: PyPI trusted publishing, post-publish PyPI smoke tests,
  v1 readiness docs, benchmark docs, and stronger wheel smoke coverage.

See [v0.3 plan](https://github.com/roymezan/pybetterleaks/blob/main/docs/v0.3-plan.md) for implementation details and open decisions.

## v0.4

- Config ergonomics:
  - `Expr.min_entropy(...)`
  - `Expr.token_efficiency(...)`
  - allowlist-replacement helpers such as `Expr.path_matches_any(...)`,
    `Expr.git_commit_in(...)`, and `Expr.finding_contains_any(...)`
  - expression composition helpers: `Expr.any_of(...)`, `Expr.all_of(...)`,
    and `Expr.not_(...)`
  - `Validation.valid(...)`, `Validation.invalid(...)`,
    `Validation.unknown(...)`, `Validation.needs_validation(...)`, and
    `Validation.bearer_get(...)`
  - `Rule.regex_rule(...)`
  - `Rule.path_rule(...)`
  - `Rule.prefixed_token_rule(...)`
  - `Rule.pem_private_key_rule(...)`
  - `Rule.entropy` compatibility serialization
- Relative `extend.path` handling for inline configs through
  `extend_base_path`.
- Async cancellation hardening so cancelled Python tasks shield and drain the
  executor future after requesting native cancellation.
- Roadmap/backlog cleanup now that config coverage for Betterleaks `v1.6.1`
  stable fields is closed.

See [v0.4 plan](https://github.com/roymezan/pybetterleaks/blob/main/docs/v0.4-plan.md) for implementation details and acceptance
criteria.

## v0.5

- Release artifact inspection before wheel upload and again before PyPI
  publishing.
- Checksum verification after `SHA256SUMS` generation.
- GitHub release notes generated from tags with `SHA256SUMS` attached.
- GitHub artifact attestations for wheels and checksums.
- Documented supply-chain story, deprecation policy, and SBOM decision.

See [v0.5 plan](https://github.com/roymezan/pybetterleaks/blob/main/docs/v0.5-plan.md) for implementation details and acceptance
criteria.

## v0.6

- Release branch workflow for `release/*`.
- Version automation that defaults to patch bumps unless maintainers choose a
  different release level.
- Automatic tag creation when a reviewed `release/vX.Y.Z` branch is merged to
  `main`.
- Post-release audit automation for PyPI, GitHub release assets, checksums, and
  install smoke tests.
- GitHub Actions maintenance, including Node deprecation cleanup where possible.
- CI benchmark artifacts and wheel-installed benchmark smoke tests.
- Project hygiene files: issue templates, PR template, and `SECURITY.md`.
- README visual polish and dedicated Git scanning docs.

See [v0.6 plan](https://github.com/roymezan/pybetterleaks/blob/main/docs/v0.6-plan.md) for implementation details and open decisions.
