import json
import os
import subprocess
import time
import threading
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction


class GithubReposExtension(Extension):
    def __init__(self):
        super().__init__()
        self.cache_dir = Path(__file__).parent / '.cache'
        self.cache_file = self.cache_dir / 'repos.json'
        self.cache_dir.mkdir(exist_ok=True)
        self.refresh_lock = threading.Lock()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())

    def get_cache_refresh_interval(self):
        minutes = self.preferences.get('cache_refresh_minutes', '5')
        try:
            return int(minutes)
        except ValueError:
            return 5

    def is_cache_valid(self):
        if not self.cache_file.exists():
            return False

        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                cache_time = datetime.fromisoformat(data.get('cached_at', '2000-01-01T00:00:00'))
                refresh_interval = self.get_cache_refresh_interval()
                return datetime.now() - cache_time < timedelta(minutes=refresh_interval)
        except (json.JSONDecodeError, KeyError, ValueError):
            return False

    def load_repos_from_cache(self):
        if not self.cache_file.exists():
            return []

        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                return data.get('repos', [])
        except (json.JSONDecodeError, KeyError):
            return []

    def fetch_repos_from_github(self):
        try:
            result = subprocess.run(
                ['gh', 'api', '/user/repos', '--paginate', '--jq',
                 '.[] | {name: .name, url: .html_url, owner: .owner.login, description: .description}'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return []

            repos = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        repo = json.loads(line)
                        repos.append(repo)
                    except json.JSONDecodeError:
                        continue

            return repos
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []

    def save_repos_to_cache(self, repos):
        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'repos': repos
        }

        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)

    def refresh_cache(self, force=False):
        if not force and self.refresh_lock.locked():
            return

        with self.refresh_lock:
            repos = self.fetch_repos_from_github()
            if repos:
                self.save_repos_to_cache(repos)

    def ensure_cache_exists(self):
        if not self.cache_file.exists():
            self.refresh_cache(force=True)

    def trigger_background_refresh(self):
        if not self.is_cache_valid():
            thread = threading.Thread(target=self.refresh_cache, daemon=True)
            thread.start()


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument() or ''

        extension.ensure_cache_exists()
        extension.trigger_background_refresh()

        repos = extension.load_repos_from_cache()

        if not repos:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/icon.png',
                    name='No repositories found',
                    description='Make sure gh CLI is authenticated (run: gh auth login)',
                    on_enter=OpenUrlAction('https://cli.github.com/manual/gh_auth_login')
                )
            ])

        filtered_repos = self.filter_repos(repos, query)

        if not filtered_repos:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/icon.png',
                    name=f'No repositories matching "{query}"',
                    description='Try a different search term'
                )
            ])

        items = []
        for repo in filtered_repos[:15]:
            owner = repo.get('owner', '')
            name = repo.get('name', '')
            description = repo.get('description') or 'No description'
            url = repo.get('url', '')

            items.append(ExtensionResultItem(
                icon='images/icon.png',
                name=f"{owner}/{name}",
                description=description,
                on_enter=OpenUrlAction(url)
            ))

        return RenderResultListAction(items)

    def filter_repos(self, repos, query):
        if not query:
            return repos

        query_lower = query.lower()
        filtered = []

        for repo in repos:
            owner = repo.get('owner', '').lower()
            name = repo.get('name', '').lower()
            description = (repo.get('description') or '').lower()

            if (query_lower in name or
                query_lower in owner or
                query_lower in f"{owner}/{name}" or
                query_lower in description):
                filtered.append(repo)

        return filtered


if __name__ == '__main__':
    GithubReposExtension().run()
