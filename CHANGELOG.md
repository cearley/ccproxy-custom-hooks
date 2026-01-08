# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-01-08

### Added
- Initial release of ccproxy-custom-hooks
- `max_tokens_adjuster` hook for dynamic max_tokens adjustment based on model capabilities
- `tool_filter` hook for removing tools from models with small context windows
- Standalone installer script supporting local and GitHub installation
- Single-source versioning system
- Configuration templates for ccproxy.yaml and config.yaml
- Support for Claude (OAuth), OpenAI, Gemini, and GitHub Copilot models
- Comprehensive documentation and development guides
- Pre-commit hooks with Ruff for code quality

[Unreleased]: https://github.com/cearley/ccproxy-custom-hooks/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/cearley/ccproxy-custom-hooks/releases/tag/v0.1.0
