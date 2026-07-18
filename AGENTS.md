# AGENTS.md

## Python 3 Development Environment

This repository is set up for Python 3 development on a system-managed Python installation (Python 3.14.4).

### Key Facts for Agents

- **Python version**: 3.14.4 (system managed)
- **Environment status**: Externally managed - direct package installations blocked by PEP 668
- **No virtual environment created**: Due to missing `python3-venv` package and sudo access
- **Installation approach required**: Use `--break-system-packages` flag for pip operations when necessary

### Development Commands

- **Run Python code directly**: `python3 script.py`
- **Update pip**: `python3 -m pip install --upgrade pip --break-system-packages` (if needed)
- **Install packages with user scope**: `python3 -m pip install --user package_name`

### Project Structure

The structure was initialized with:
```
src/           # Source code
tests/         # Test files  
docs/          # Documentation
```

### Special Considerations

1. System-managed Python environment requires special flags for package installations
2. Virtual environments cannot be created without `python3-venv` package and sudo access
3. All development should work within the existing Python 3.14 installation
4. When installing packages, use `--break-system-packages` flag to bypass restrictions

### Testing Approach

Since standard virtual environment setup is not available:
- Direct execution of Python scripts using system-provided interpreter
- Tests can be run in the current environment
- Package dependencies must be handled carefully due to system restrictions

### Workflow Notes

This repository is configured for development, with focus on:
- Direct Python 3.14 development
- System-level package management constraints
- Minimal external tooling requirements