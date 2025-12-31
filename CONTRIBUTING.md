# Contributing to Pi Monitor

Thank you for your interest in contributing to Pi Monitor! This document provides guidelines for contributing.

## Design Philosophy

Pi Monitor is designed to be:

1. **Zero-dependency** — Only Python standard library, no pip packages
2. **Lightweight** — Minimal RAM and CPU usage
3. **Simple** — Easy to understand, modify, and deploy
4. **Self-contained** — Each component is a single Python file

Please keep these principles in mind when contributing.

## How to Contribute

### Reporting Bugs

1. Check existing issues first
2. Include your Pi model and OS version
3. Provide steps to reproduce
4. Include relevant log output

### Suggesting Features

1. Open an issue describing the feature
2. Explain the use case
3. Consider the zero-dependency constraint

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Test on actual Raspberry Pi hardware if possible
5. Commit with clear messages: `git commit -m 'Add feature X'`
6. Push to your fork: `git push origin feature/my-feature`
7. Open a Pull Request

## Code Style

- Follow PEP 8
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small
- Comment complex logic

## Testing

Since we avoid dependencies, testing is manual:

1. Test the agent on various Pi models (Zero, 3, 4, 5)
2. Test the dashboard in multiple browsers
3. Verify metrics accuracy against `htop` and `df`
4. Test offline/online state transitions

## Areas for Contribution

- [ ] Additional metrics (network I/O, GPU temp for Pi 4/5)
- [ ] Dark/light theme toggle
- [ ] Historical data graphing (in-memory, no database)
- [ ] Auto-discovery via mDNS
- [ ] Alert thresholds
- [ ] Documentation improvements

## Questions?

Open an issue with the "question" label.

Thank you for helping make Pi Monitor better! 🍓
