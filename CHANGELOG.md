# Changelog

All notable changes to this project are documented here. This file is generated
from [Conventional Commits](https://www.conventionalcommits.org/) by
release-please — don't edit it by hand. The project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1](https://github.com/fabiocicerchia/envdiff/compare/v0.1.0...v0.1.1) (2026-08-06)


### Bug Fixes

* **pre-commit:** stop check-yaml failing on Helm templates and multi-doc manifests ([5db6351](https://github.com/fabiocicerchia/envdiff/commit/5db635139d4b2976866371cbd7fb6d025d8ef724))
* **security:** skip the SARIF upload on private repos ([3f9fe7f](https://github.com/fabiocicerchia/envdiff/commit/3f9fe7f1958b52782f97f850d12e46011ced2aea))

## [0.1.0]

### Added

- Initial release: diff environment variables between two sources
  (dotenv file, stdin, `cmd:`, `k8s:`) with secret masking on by default,
  `--ignore`, `--no-mask`, and `--fail-on-diff`.
