# Deprecation Policy

PyBetterleaks is still pre-`1.0.0`, so the public API may change while the
project learns from real usage. Even in alpha, changes should be deliberate and
documented.

## Compatibility Promises

The following are compatibility promises for supported APIs:

- no runtime Betterleaks CLI dependency
- no runtime `subprocess` usage
- no install-time native binary downloads
- JSON remains the native ABI boundary
- `scan_text`, `scan_dir`, `scan_git`, and their async wrappers return typed
  dataclass results
- bundled Betterleaks version is exposed through `betterleaks_version()`

## Before 1.0

Pre-`1.0.0` releases may make breaking changes, but each breaking change should
be called out in the release notes. Prefer soft migration paths where practical,
especially for config helpers and exception behavior.

## After 1.0

After `1.0.0`:

- remove or rename public APIs only in a major release
- deprecate APIs for at least one minor release before removal
- emit `DeprecationWarning` where Python can do so without noisy false positives
- document replacements in release notes and API docs
- keep old behavior in patch releases unless it is a security or correctness
  fix

## Native ABI

The native symbol surface should stay smaller and more conservative than the
Python API. New symbols can be added in minor releases. Removing or changing an
exported native symbol should wait for a major release unless the symbol was
never shipped in a published wheel.

## Breaking-Change Checklist

Before merging a breaking change:

- update docs and generated API reference
- add release-note text
- add migration guidance
- update tests for both the new behavior and the intended error path
- confirm the change does not weaken the no-runtime-subprocess promise

