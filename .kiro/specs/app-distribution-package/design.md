# Design Document

## Overview

The Reporter application distribution package will be built using PyInstaller for creating standalone executables, combined with platform-specific packaging tools to create native installers. The design focuses on creating a unified application that launches the PyQt dashboard by default while providing CLI access to underlying functionality.

## Architecture

### Application Structure
```
Reporter App/
├── main.py (Entry point - launches PyQt dashboard)
├── cli/
│   ├── github_data.py (GitHub data collection)
│   └── worklog.py (Work logging utilities)
├── ui/
│   ├── dashboard.py (Main PyQt interface)
│   └── resources/ (Icons, assets)
├── data/
│   ├── models.py (Data structures)
│   └── storage.py (File I/O operations)
└── config/
    └── settings.py (Application configuration)
```

### Build Pipeline Architecture
```
Source Code → PyInstaller → Platform Packager → Distribution Package
     ↓              ↓              ↓                    ↓
   Python       Executable    Native Package      DMG/EXE/AppImage
```

## Components and Interfaces

### 1. Main Application Entry Point
- **File**: `main.py`
- **Purpose**: Primary executable entry point that launches the PyQt dashboard
- **Interface**: Command-line arguments for different modes (GUI/CLI)
- **Dependencies**: PyQt5, application modules

### 2. PyInstaller Configuration
- **File**: `reporter.spec`
- **Purpose**: PyInstaller specification for building executables
- **Features**:
  - One-file executable generation
  - Hidden imports for PyQt5 and dependencies
  - Resource bundling (icons, assets)
  - Platform-specific configurations

### 3. Platform-Specific Packaging

#### macOS (DMG)
- **Tool**: create-dmg or dmgbuild
- **Output**: Reporter.dmg with drag-to-Applications interface
- **Features**:
  - Code signing with developer certificate
  - Notarization for Gatekeeper compatibility
  - Custom DMG background and layout

#### Windows (EXE Installer)
- **Tool**: Inno Setup or NSIS
- **Output**: ReporterSetup.exe installer
- **Features**:
  - Start Menu integration
  - Desktop shortcut creation
  - Uninstaller generation
  - Windows registry integration

#### Linux (AppImage/DEB)
- **Tools**: linuxdeploy for AppImage, dpkg-deb for DEB
- **Output**: Reporter.AppImage and reporter.deb
- **Features**:
  - Desktop file integration
  - Icon installation
  - Dependency management

### 4. Data Management
- **Local Storage**: `~/.reporter/` directory for user data
- **Files**:
  - `github_data.yml` (GitHub status cache)
  - `worklog_YYYY-MM-DD.txt` (Daily work logs)
  - `config.yml` (User preferences)

### 5. CLI Integration
- **Access Method**: Command-line flags or separate CLI executables
- **Commands**:
  - `--cli github` (Run GitHub data collection)
  - `--cli worklog` (Access work logging functions)
  - Default: Launch GUI dashboard

## Data Models

### GitHub Data Structure
```yaml
account_name: string
my_issues:
  issue_id: "title [url]"
my_prs:
  pr_id: "title [url]"
my_reviews:
  review_id: "title [url]"
```

### Work Log Structure
```
YYYY-MM-DD HH:MM [MegaCorp] [13# fix bug] - Work entry description
YYYY-MM-DD HH:MM [personal project] [45# merge pr] - Another work entry
```

### Configuration Structure
```yaml
github:
  auto_refresh: boolean
  refresh_interval: integer
ui:
  theme: string
  window_size: [width, height]
data:
  storage_path: string
```

## Error Handling

### Build-Time Errors
- Missing dependencies detection
- Platform-specific build failures
- Code signing/notarization failures
- Resource bundling issues

### Runtime Errors
- Missing GitHub CLI (`gh` command)
- File permission issues
- Network connectivity problems
- PyQt initialization failures

### Error Recovery
- Graceful degradation when GitHub CLI unavailable
- Fallback to local data when network fails
- User-friendly error messages with suggested solutions
- Logging to `~/.reporter/logs/` for debugging

## Testing Strategy

### Unit Testing
- Data parsing functions (GitHub status, work logs)
- File I/O operations
- Configuration management
- CLI argument processing

### Integration Testing
- PyQt UI functionality
- GitHub data collection workflow
- Work log persistence
- Cross-platform file operations

### Distribution Testing
- Package installation on clean systems
- Application launch and basic functionality
- Desktop integration verification
- Uninstallation cleanup

### Platform Testing Matrix
```
         | macOS | Windows | Linux |
---------|-------|---------|-------|
Build    |   ✓   |    ✓    |   ✓   |
Install  |   ✓   |    ✓    |   ✓   |
Launch   |   ✓   |    ✓    |   ✓   |
Features |   ✓   |    ✓    |   ✓   |
```

## Build Configuration

### PyInstaller Spec File
- Hidden imports for PyQt5 modules
- Data file inclusion (icons, templates)
- Platform-specific executable options
- Console/windowed mode configuration

### GitHub Actions Workflow
- Matrix build for multiple platforms
- Dependency caching for faster builds
- Artifact upload and release creation
- Code signing integration (macOS/Windows)

### Signing and Notarization
- macOS: Developer ID certificate + notarization
- Windows: Code signing certificate
- Linux: GPG signing for repositories

## Deployment Strategy

### Release Process
1. Version tag creation triggers build
2. Automated testing on all platforms
3. Package creation and signing
4. Upload to GitHub Releases
5. Optional: Distribution to app stores/repositories

### Update Mechanism
- GitHub Releases API for version checking
- In-app update notifications
- Download and install guidance
- Automatic update capability (future enhancement)