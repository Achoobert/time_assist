# Reporter App Tests

This directory contains all tests for the Reporter application.

## Running Tests

### Run All Tests
```bash
python scripts/tests/run_all_tests.py
```

### Run Individual Tests
```bash
python scripts/tests/test_llm_functionality.py
python scripts/tests/test_llm_integration.py
python scripts/tests/test_worklog_preservation.py
python scripts/tests/test_ui_llm_disabled.py
python scripts/tests/test_ui_visual.py
```

## Test Files

### Core Functionality Tests
- **`test_llm_functionality.py`** - Comprehensive LLM functionality testing
  - Configuration loading
  - Various worklog formats
  - Error handling (Ollama not running, timeouts, API errors)
  - Chunking behavior with large logs
  - Prompt customization
  - Disabled state handling
  - Clipboard functionality structure

- **`test_worklog_preservation.py`** - Critical data preservation tests
  - Ensures worklog entries are never erased
  - Tests append-only behavior
  - Validates file structure integrity

### Integration Tests
- **`test_llm_integration.py`** - Real-world LLM integration
  - Tests with actual Ollama service when available
  - Validates end-to-end LLM report generation
  - Graceful handling when service unavailable

### UI Tests
- **`test_ui_llm_disabled.py`** - UI behavior testing
  - Tests UI with LLM enabled/disabled
  - Validates proper widget visibility
  - Tests graceful method handling

- **`test_ui_visual.py`** - UI improvements demonstration
  - Validates text visibility fixes
  - Confirms button placement
  - Tests configuration-aware UI

## Test Coverage

✅ **LLM Functionality** - 7 test functions  
✅ **Data Preservation** - Critical worklog safety  
✅ **Integration** - Real-world Ollama testing  
✅ **UI Behavior** - Configuration-aware interface  
✅ **Visual Improvements** - User experience validation  

## Requirements

Tests require the same dependencies as the main application:
- `pyyaml`
- `pyqt5` (for UI tests)
- `requests` (for LLM tests)

## Test Results

All tests are designed to pass in both development and production environments:
- Tests gracefully handle missing dependencies
- UI tests work in headless environments
- LLM tests work with or without Ollama running
- Configuration tests adapt to different setups