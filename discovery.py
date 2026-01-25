#!/usr/bin/env python3
"""
discovery.py - The Finder
=========================
Discovers high-quality GitHub repositories from:
1. GitHub Trending (high-star repos created in last 7 days)
2. Hacker News (top stories with GitHub links)

Filters them using Claude AI to ensure "greater good" tools only.
"""

import os
import re
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

import requests
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Constants
GITHUB_API_BASE = "https://api.github.com"
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
QUEUE_FILE = Path("queue.txt")
HISTORY_FILE = Path("history.txt")
MIN_STARS = 50  # Minimum stars for consideration
MAX_CANDIDATES = 20  # Max repos to evaluate per run


class RepoDiscovery:
    """Discovers and filters GitHub repositories."""
    
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        if self.github_token:
            self.headers["Authorization"] = f"Bearer {self.github_token}"
        
        # Load history to avoid duplicates
        self.history = self._load_history()
        
    def _load_history(self) -> set:
        """Load previously processed repo URLs."""
        if HISTORY_FILE.exists():
            return set(HISTORY_FILE.read_text().strip().split('\n'))
        return set()
    
    def _load_queue(self) -> list:
        """Load current queue."""
        if QUEUE_FILE.exists():
            content = QUEUE_FILE.read_text().strip()
            return content.split('\n') if content else []
        return []
    
    def _save_queue(self, urls: list):
        """Save URLs to queue file."""
        QUEUE_FILE.write_text('\n'.join(urls) + '\n' if urls else '')
    
    def _is_already_processed(self, url: str) -> bool:
        """Check if repo URL is in history or queue."""
        current_queue = self._load_queue()
        return url in self.history or url in current_queue
    
    def discover_github_trending(self) -> list:
        """
        Find trending repositories created in the last 7 days with high stars.
        Uses GitHub Search API since there's no official trending API.
        """
        logger.info("🔍 Searching GitHub for trending repositories...")
        
        # Calculate date 7 days ago
        week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Search for repos created in last 7 days, sorted by stars
        search_url = f"{GITHUB_API_BASE}/search/repositories"
        params = {
            "q": f"created:>{week_ago} stars:>{MIN_STARS}",
            "sort": "stars",
            "order": "desc",
            "per_page": MAX_CANDIDATES
        }
        
        try:
            response = requests.get(search_url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            repos = []
            for item in data.get("items", []):
                repos.append({
                    "url": item["html_url"],
                    "name": item["full_name"],
                    "description": item.get("description") or "No description provided",
                    "stars": item["stargazers_count"],
                    "language": item.get("language") or "Unknown",
                    "topics": item.get("topics", [])
                })
            
            logger.info(f"✅ Found {len(repos)} trending repositories from GitHub")
            return repos
            
        except requests.RequestException as e:
            logger.error(f"❌ GitHub API error: {e}")
            return []
    
    def discover_hackernews(self) -> list:
        """
        Scrape Hacker News top stories for GitHub repository links.
        """
        logger.info("🔍 Scanning Hacker News for GitHub projects...")
        
        repos = []
        
        try:
            # Get top story IDs
            response = requests.get(f"{HN_API_BASE}/topstories.json", timeout=30)
            response.raise_for_status()
            story_ids = response.json()[:50]  # Check top 50 stories
            
            github_pattern = re.compile(r'https?://github\.com/([^/]+/[^/]+)/?')
            
            for story_id in story_ids:
                try:
                    story_response = requests.get(
                        f"{HN_API_BASE}/item/{story_id}.json", 
                        timeout=10
                    )
                    story = story_response.json()
                    
                    if not story or story.get("type") != "story":
                        continue
                    
                    url = story.get("url", "")
                    match = github_pattern.match(url)
                    
                    if match:
                        repo_path = match.group(1)
                        # Fetch repo details from GitHub API
                        repo_info = self._fetch_repo_info(repo_path)
                        if repo_info:
                            repos.append(repo_info)
                            
                except (requests.RequestException, json.JSONDecodeError):
                    continue
            
            logger.info(f"✅ Found {len(repos)} GitHub projects from Hacker News")
            return repos
            
        except requests.RequestException as e:
            logger.error(f"❌ Hacker News API error: {e}")
            return []
    
    def _fetch_repo_info(self, repo_path: str) -> dict | None:
        """Fetch repository information from GitHub API."""
        try:
            response = requests.get(
                f"{GITHUB_API_BASE}/repos/{repo_path}",
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code != 200:
                return None
            
            item = response.json()
            return {
                "url": item["html_url"],
                "name": item["full_name"],
                "description": item.get("description") or "No description provided",
                "stars": item["stargazers_count"],
                "language": item.get("language") or "Unknown",
                "topics": item.get("topics", [])
            }
            
        except requests.RequestException:
            return None
    
    def is_greater_good(self, repo: dict) -> bool:
        """
        Use Claude AI to determine if the repository serves the "greater good".
        Filters out meme coins, niche backend libraries, and low-value projects.
        """
        prompt = f"""Analyze this GitHub repository and determine if it would be useful and interesting for a general developer audience.

Repository: {repo['name']}
Description: {repo['description']}
Language: {repo['language']}
Stars: {repo['stars']}
Topics: {', '.join(repo['topics']) if repo['topics'] else 'None'}

Criteria for YES:
- Developer tools that boost productivity
- Useful libraries/frameworks with broad appeal
- Open source tools that serve the "greater good"
- Educational or learning resources
- Innovative projects that solve real problems

Criteria for NO:
- Cryptocurrency/meme coins/NFT projects
- Highly niche backend libraries with limited appeal
- Abandoned or low-quality projects
- Spam or self-promotional repos
- Projects with unclear purpose

Answer with ONLY "YES" or "NO" - nothing else."""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}]
            )
            
            answer = response.content[0].text.strip().upper()
            is_approved = answer == "YES"
            
            logger.info(f"  {'✅' if is_approved else '❌'} {repo['name']}: {answer}")
            return is_approved
            
        except Exception as e:
            logger.error(f"❌ Claude API error for {repo['name']}: {e}")
            return False
    
    def run(self) -> int:
        """
        Main discovery pipeline.
        Returns the number of new repos added to queue.
        """
        logger.info("🚀 Starting repository discovery pipeline...")
        
        # Collect candidates from all sources
        candidates = []
        
        # GitHub Trending
        github_repos = self.discover_github_trending()
        candidates.extend(github_repos)
        
        # Hacker News
        hn_repos = self.discover_hackernews()
        candidates.extend(hn_repos)
        
        # Deduplicate by URL
        seen_urls = set()
        unique_candidates = []
        for repo in candidates:
            if repo["url"] not in seen_urls:
                seen_urls.add(repo["url"])
                unique_candidates.append(repo)
        
        logger.info(f"📊 Total unique candidates: {len(unique_candidates)}")
        
        # Filter and queue
        new_repos = []
        current_queue = self._load_queue()
        
        for repo in unique_candidates:
            # Skip if already processed
            if self._is_already_processed(repo["url"]):
                logger.info(f"  ⏭️  Skipping (already processed): {repo['name']}")
                continue
            
            # AI Filter
            logger.info(f"🤖 Evaluating: {repo['name']} ({repo['stars']}⭐)")
            if self.is_greater_good(repo):
                new_repos.append(repo["url"])
                logger.info(f"  ✨ Added to queue: {repo['name']}")
            
            # Limit queue additions per run
            if len(new_repos) >= 1:
                logger.info("📦 Queue limit reached for this run")
                break
        
        # Update queue
        if new_repos:
            updated_queue = current_queue + new_repos
            self._save_queue(updated_queue)
            logger.info(f"✅ Added {len(new_repos)} new repos to queue")
        else:
            logger.info("ℹ️  No new repos added to queue")
        
        return len(new_repos)


def main():
    """Entry point for discovery script."""
    try:
        discovery = RepoDiscovery()
        added_count = discovery.run()
        logger.info(f"🏁 Discovery complete. {added_count} repos added to queue.")
        return 0
    except Exception as e:
        logger.error(f"❌ Discovery failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
