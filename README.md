# Reporter

A *LOCAL* simple work tracking app that helps you log daily activities and generate standup reports with GitHub integration.

Nothing goes to the internet unless you manually send it
You own the logs you create!


The goal is to apply the advice given in `Software Engineer’s Guidebook/ Owning your career/ Keep a work log`


## Features

- **Quick Work Entry**: Autofocus text input for fast logging without mouse clicks
- **GitHub Integration**: Automatically pulls your assigned issues, PRs, and reviews
- **Clickable Links**: Click any GitHub item to open it directly in your browser
- **Organization Context**: Tag work entries with projects or organizations
- **Daily Reports**: View and copy your work log for standup meetings
- **Cross-Platform**: Available as portable executables for macOS, Windows, and Linux

## Quick Start

### Download & Run
1. Download the latest release for your platform
2. **macOS**: Extract and open `Reporter.app`
   - If you see "cannot be opened because it is from an unidentified developer":
     - Right-click the app → **"Open"**
     - Click **"Open"** in the security dialog
     - Or: System Preferences → Security & Privacy → **"Open Anyway"**
3. **Windows/Linux**: Extract and run the `Reporter` executable
4. Start logging your work!

### From Source
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

## Usage

1. **Log Work**: Type your work description and press Enter
2. **Add Context**: Select organization and GitHub issue/PR (optional)
3. **Generate Reports**: Copy your daily log to clipboard for standups
4. **Refresh GitHub Data**: Click "Refresh GitHub Data" to update issues/PRs

## Build Executables

```bash
pip install pyinstaller
pyinstaller reporter.spec
```

Executables will be created in `dist/Reporter/` (standalone) and `dist/Reporter.app` (macOS app bundle).

## GitHub Integration

The app uses the GitHub CLI (`gh`) to fetch your assigned issues, pull requests, and review requests. Make sure you have `gh` installed and authenticated:

```bash
gh auth login
```

## Code Signing Status

- **macOS**: Self-signed with ad-hoc signature (reduces but doesn't eliminate security warnings)
- **Windows**: Unsigned (Windows Defender may show warnings)
- **Linux**: No signing required

### macOS Security Notes
The app is self-signed, which means:
- ✅ **Safer than unsigned**: Basic integrity verification
- ⚠️ **Still shows warnings**: Not from identified Apple developer
- 🔓 **Easy bypass**: Right-click → Open works immediately

For a completely seamless experience, we'd need an Apple Developer Program membership ($99/year).