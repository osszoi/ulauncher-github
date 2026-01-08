# ULauncher GitHub Repositories

A ULauncher extension for quickly browsing and opening your GitHub repositories.

## Features

- Search through all your GitHub repositories (personal and organization repos)
- Fast, cached search results with automatic background updates
- Open repositories directly in your browser
- Configurable cache refresh interval

## Requirements

- [ULauncher 5.x](https://ulauncher.io/)
- [GitHub CLI](https://cli.github.com/) (authenticated)

## Installation

### Via ULauncher

1. Open ULauncher preferences
2. Go to Extensions > Add extension
3. Paste the repository URL: `https://github.com/osszoi/ulauncher-github`
4. Click Add

### Manual Installation

```bash
git clone https://github.com/osszoi/ulauncher-github ~/.local/share/ulauncher/extensions/ulauncher-github
```

Then restart ULauncher or reload extensions.

## Setup

Before using the extension, ensure GitHub CLI is authenticated:

```bash
gh auth login
```

## Usage

1. Open ULauncher (default: `Ctrl+Space`)
2. Type the keyword `gh` followed by your search query
3. Browse results and press Enter to open a repository

### Examples

- `gh` - Show all repositories
- `gh classroom` - Find repositories matching "classroom"
- `gh dawere/analytics` - Search by owner and name

The extension searches in repository names, owners, and descriptions.

## Configuration

In ULauncher preferences for this extension:

- **GitHub Repos**: The keyword to trigger the extension (default: `gh`)
- **Cache Refresh Interval**: How often to update the repository cache in minutes (default: 5)

## How It Works

On first use, the extension fetches all your accessible repositories using the GitHub CLI and caches them locally. Subsequent searches use the cached data for instant results. The cache automatically refreshes in the background based on your configured interval.

## License

MIT
