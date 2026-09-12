# Changelog

All notable changes to this project are documented here. This file is generated
from [Conventional Commits](https://www.conventionalcommits.org/) by
release-please — don't edit it by hand. The project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.2](https://github.com/fabiocicerchia/envdiff/compare/v0.3.1...v0.3.2) (2026-09-12)


### Documentation

* add a Features section to the README ([#83](https://github.com/fabiocicerchia/envdiff/issues/83)) ([61cc807](https://github.com/fabiocicerchia/envdiff/commit/61cc807787991c5304e5fbc0f2924ea230ddab0b))

## [0.3.1](https://github.com/fabiocicerchia/envdiff/compare/v0.3.0...v0.3.1) (2026-09-11)


### Bug Fixes

* **release:** let the release PR carry a token that isn't GITHUB_TOKEN ([#80](https://github.com/fabiocicerchia/envdiff/issues/80)) ([3c620e6](https://github.com/fabiocicerchia/envdiff/commit/3c620e6c3be1be2d76c0e4d7bd0df68accdfe6ca))

## [0.3.0](https://github.com/fabiocicerchia/envdiff/compare/v0.2.1...v0.3.0) (2026-09-09)


### Features

* **packaging:** ship a man page with the wheel ([#75](https://github.com/fabiocicerchia/envdiff/issues/75)) ([aaec7d0](https://github.com/fabiocicerchia/envdiff/commit/aaec7d0f7f4180a7eed5c5bde1baa8195efd226b))


### Bug Fixes

* **ci:** pin the editorconfig-checker binary version ([#59](https://github.com/fabiocicerchia/envdiff/issues/59)) ([3ceed30](https://github.com/fabiocicerchia/envdiff/commit/3ceed30be53683cee7e5fcff8f0bd464ab795be7))
* survive a dotenv that is not valid UTF-8 ([#74](https://github.com/fabiocicerchia/envdiff/issues/74)) ([3a8e1e4](https://github.com/fabiocicerchia/envdiff/commit/3a8e1e418645c65d3c926aae72689e997d71b694))

## [0.2.1](https://github.com/fabiocicerchia/envdiff/compare/v0.2.0...v0.2.1) (2026-08-29)

### Bug Fixes

- unblock quality and clear the Scorecard pinned-dependencies finding ([#46](https://github.com/fabiocicerchia/envdiff/issues/46)) ([e93ba88](https://github.com/fabiocicerchia/envdiff/commit/e93ba8846310f5a30e256fad7076aa2cd766674a))

## [0.2.0](https://github.com/fabiocicerchia/envdiff/compare/v0.1.2...v0.2.0) (2026-08-25)

### Features

- **docs:** build the docs site in Actions and drop Read the Docs ([#38](https://github.com/fabiocicerchia/envdiff/issues/38)) ([45e1c8d](https://github.com/fabiocicerchia/envdiff/commit/45e1c8de3b022314c22f7014fd487c0885b86c60))

### Bug Fixes

- **ci:** compute the next release PR after the draft is published ([#35](https://github.com/fabiocicerchia/envdiff/issues/35)) ([d4e037e](https://github.com/fabiocicerchia/envdiff/commit/d4e037e073aa507db5e5f1cfade74a063f5b15e4))

## [0.1.2](https://github.com/fabiocicerchia/envdiff/compare/v0.1.1...v0.1.2) (2026-08-13)

### Bug Fixes

- security and code-quality findings ([#27](https://github.com/fabiocicerchia/envdiff/issues/27)) ([4e1e9a5](https://github.com/fabiocicerchia/envdiff/commit/4e1e9a5df569d869dd5316ddc50eb830415bb007))

## [0.1.1](https://github.com/fabiocicerchia/envdiff/compare/v0.1.0...v0.1.1) (2026-08-06)

### Bug Fixes

- **pre-commit:** stop check-yaml failing on Helm templates and multi-doc manifests ([5db6351](https://github.com/fabiocicerchia/envdiff/commit/5db635139d4b2976866371cbd7fb6d025d8ef724))
- **security:** skip the SARIF upload on private repos ([3f9fe7f](https://github.com/fabiocicerchia/envdiff/commit/3f9fe7f1958b52782f97f850d12e46011ced2aea))

## [0.1.0]

### Added

- Initial release: diff environment variables between two sources
  (dotenv file, stdin, `cmd:`, `k8s:`) with secret masking on by default,
  `--ignore`, `--no-mask`, and `--fail-on-diff`.
