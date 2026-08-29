# Changelog

All notable changes to this project are documented here. This file is generated
from [Conventional Commits](https://www.conventionalcommits.org/) by
release-please — don't edit it by hand. The project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1](https://github.com/fabiocicerchia/envdiff/compare/v0.2.0...v0.2.1) (2026-08-29)


### Bug Fixes

* unblock quality and clear the Scorecard pinned-dependencies finding ([#46](https://github.com/fabiocicerchia/envdiff/issues/46)) ([e93ba88](https://github.com/fabiocicerchia/envdiff/commit/e93ba8846310f5a30e256fad7076aa2cd766674a))

## [0.2.0](https://github.com/fabiocicerchia/envdiff/compare/v0.1.2...v0.2.0) (2026-08-25)


### Features

* **docs:** build the docs site in Actions and drop Read the Docs ([#38](https://github.com/fabiocicerchia/envdiff/issues/38)) ([45e1c8d](https://github.com/fabiocicerchia/envdiff/commit/45e1c8de3b022314c22f7014fd487c0885b86c60))


### Bug Fixes

* **ci:** compute the next release PR after the draft is published ([#35](https://github.com/fabiocicerchia/envdiff/issues/35)) ([d4e037e](https://github.com/fabiocicerchia/envdiff/commit/d4e037e073aa507db5e5f1cfade74a063f5b15e4))

## [0.1.2](https://github.com/fabiocicerchia/envdiff/compare/v0.1.1...v0.1.2) (2026-08-13)


### Bug Fixes

* security and code-quality findings ([#27](https://github.com/fabiocicerchia/envdiff/issues/27)) ([4e1e9a5](https://github.com/fabiocicerchia/envdiff/commit/4e1e9a5df569d869dd5316ddc50eb830415bb007))

## [0.1.1](https://github.com/fabiocicerchia/envdiff/compare/v0.1.0...v0.1.1) (2026-08-06)


### Bug Fixes

* **pre-commit:** stop check-yaml failing on Helm templates and multi-doc manifests ([5db6351](https://github.com/fabiocicerchia/envdiff/commit/5db635139d4b2976866371cbd7fb6d025d8ef724))
* **security:** skip the SARIF upload on private repos ([3f9fe7f](https://github.com/fabiocicerchia/envdiff/commit/3f9fe7f1958b52782f97f850d12e46011ced2aea))

## [0.1.0]

### Added

- Initial release: diff environment variables between two sources
  (dotenv file, stdin, `cmd:`, `k8s:`) with secret masking on by default,
  `--ignore`, `--no-mask`, and `--fail-on-diff`.
