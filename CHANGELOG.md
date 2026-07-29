# Changelog

All notable changes to this project are documented here. This file is generated
from [Conventional Commits](https://www.conventionalcommits.org/) by
release-please — don't edit it by hand. The project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.1.0 (2026-07-29)


### Features

* add --format json/markdown output ([4557761](https://github.com/fabiocicerchia/envdiff/commit/4557761e2f4ae7d05bcf188a0115d48577f1a4ec))
* add docker:, ssm: and secrets: env sources ([6a24cef](https://github.com/fabiocicerchia/envdiff/commit/6a24cef607cb8a6ba4a5e5708148070111e8ceae))
* add install.sh one-liner installer ([ce01e11](https://github.com/fabiocicerchia/envdiff/commit/ce01e11567f4befc06554ac186a95df141549975))
* add length/charset shape hints to masked diff values ([a8eb22d](https://github.com/fabiocicerchia/envdiff/commit/a8eb22d698bc0ce4ca1d36b3a641a3f27cef81af))


### Bug Fixes

* restore executable bit and use re.IGNORECASE flag constant ([#11](https://github.com/fabiocicerchia/envdiff/issues/11)) ([beb12f2](https://github.com/fabiocicerchia/envdiff/commit/beb12f2bcb9c739d1d24ddb0ab543fc54cce9a98))


### Documentation

* add GitHub Pages site, trim completed roadmap items from README ([4e388e3](https://github.com/fabiocicerchia/envdiff/commit/4e388e30bb97d998b2a1fa19e946a96db27b08d6))
* add missing README badges ([4f571c6](https://github.com/fabiocicerchia/envdiff/commit/4f571c6f5918fdd11fad28cb10431a540f44f19b))
* remove the broken FOSSA badge ([1d2e42f](https://github.com/fabiocicerchia/envdiff/commit/1d2e42fada89fb9ae0bf31f732126194a1427ef7))

## [0.1.0]

### Added

- Initial release: diff environment variables between two sources
  (dotenv file, stdin, `cmd:`, `k8s:`) with secret masking on by default,
  `--ignore`, `--no-mask`, and `--fail-on-diff`.
