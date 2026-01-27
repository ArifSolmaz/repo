#!/usr/bin/env python3
"""
discovery.py - The Finder (v4)
==============================
Discovers high-quality GitHub repositories from:
1. GitHub Trending page (scraping - daily & weekly)
2. GitHub Trending by language (Python, TypeScript, Rust, Go, etc.)
3. Hacker News (top stories with GitHub links)
4. Astronomy/Astrophysics repositories
5. HuggingFace trending models

v4 CHANGES:
- REMOVED round-robin reordering (was causing astronomy spam)
- New repos are simply APPENDED to queue
- Category rotation is now handled by autoposter.py
- Discovery just ensures minimum stock per category
"""

import os
import re
import json
import random
import logging
from datetime import datetime, timedelta
from pathlib import Path
from collections import Counter

import requests
from bs4 import BeautifulSoup
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
GITHUB_TRENDING_URL = "https://github.com/trending"
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
HF_API_BASE = "https://huggingface.co/api"
QUEUE_FILE = Path("queue.txt")
HISTORY_FILE = Path("history.txt")

# Minimum stars/likes
MIN_STARS_HN = 50
MIN_STARS_ASTRO = 3
MIN_LIKES_HF = 100

# Category targets - minimum stock per category
MIN_STOCK_PER_CATEGORY = 3

# Languages to check for trending
TRENDING_LANGUAGES = [
    "",  # All languages
    "python",
    "typescript", 
    "javascript",
    "rust",
    "go",
    "swift",
    "kotlin",
]

# Time ranges for trending
TRENDING_RANGES = ["daily", "weekly"]

# Astronomy search keywords
ASTRO_KEYWORDS = [
    "exoplanet", "astronomy", "astrophysics",
    "TESS", "JWST", "Kepler", "CHEOPS", "Gaia",
    "radial velocity", "light curve", "spectroscopy",
    "astropy", "lightkurve", "transit photometry",
    "habitable zone", "stellar activity", "planetary transit"
]


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
        
        self.web_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        self.history = self._load_history()
        
    def _load_history(self) -> set:
        if HISTORY_FILE.exists():
            return set(HISTORY_FILE.read_text().strip().split('\n'))
        return set()
    
    def _load_queue(self) -> list:
        if QUEUE_FILE.exists():
            content = QUEUE_FILE.read_text().strip()
            return content.split('\n') if content else []
        return []
    
    def _save_queue(self, urls: list):
        QUEUE_FILE.write_text('\n'.join(urls) + '\n' if urls else '')
    
    def _is_already_processed(self, url: str) -> bool:
        current_queue = self._load_queue()
        url_clean = url.rstrip('/')
        return (url_clean in self.history or 
                url_clean + '/' in self.history or
                any(url_clean in q for q in current_queue))
    
    def _count_queue_categories(self) -> dict:
        queue = self._load_queue()
        counts = {"astronomy": 0, "huggingface": 0, "general": 0}
        
        for entry in queue:
            if "|" in entry:
                _, category = entry.rsplit("|", 1)
                if category in counts:
                    counts[category] += 1
                else:
                    counts["general"] += 1
            else:
                counts["general"] += 1
        
        return counts
    
    def discover_github_trending(self) -> list:
        logger.info("🔥 Scraping GitHub Trending page...")
        
        repos = []
        seen_urls = set()
        
        languages_to_check = random.sample(TRENDING_LANGUAGES, min(3, len(TRENDING_LANGUAGES)))
        time_range = random.choice(TRENDING_RANGES)
        
        for language in languages_to_check:
            url = f"{GITHUB_TRENDING_URL}/{language}?since={time_range}"
            
            try:
                logger.info(f"  📡 Fetching: {url}")
                response = requests.get(url, headers=self.web_headers, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                articles = soup.select('article.Box-row')
                
                for article in articles[:10]:
                    try:
                        h2 = article.select_one('h2 a')
                        if not h2:
                            continue
                        
                        repo_path = h2.get('href', '').strip('/')
                        if not repo_path or '/' not in repo_path:
                            continue
                        
                        repo_url = f"https://github.com/{repo_path}"
                        
                        if repo_url in seen_urls:
                            continue
                        seen_urls.add(repo_url)
                        
                        desc_elem = article.select_one('p.col-9')
                        description = desc_elem.get_text(strip=True) if desc_elem else "No description"
                        
                        stars_elem = article.select_one('a[href*="/stargazers"]')
                        stars_text = stars_elem.get_text(strip=True) if stars_elem else "0"
                        stars = self._parse_stars(stars_text)
                        
                        lang_elem = article.select_one('[itemprop="programmingLanguage"]')
                        lang = lang_elem.get_text(strip=True) if lang_elem else "Unknown"
                        
                        repos.append({
                            "url": repo_url,
                            "name": repo_path,
                            "description": description,
                            "stars": stars,
                            "language": lang,
                            "topics": [],
                            "source": f"trending/{language or 'all'}/{time_range}"
                        })
                        
                    except Exception as e:
                        continue
                
            except requests.RequestException as e:
                logger.warning(f"  ⚠️ Failed to fetch {url}: {e}")
                continue
        
        logger.info(f"✅ Found {len(repos)} trending repositories")
        return repos
    
    def _parse_stars(self, stars_text: str) -> int:
        stars_text = stars_text.lower().replace(',', '').strip()
        try:
            if 'k' in stars_text:
                return int(float(stars_text.replace('k', '')) * 1000)
            elif 'm' in stars_text:
                return int(float(stars_text.replace('m', '')) * 1000000)
            else:
                return int(stars_text)
        except (ValueError, AttributeError):
            return 0
    
    def discover_hackernews(self) -> list:
        logger.info("🔍 Scanning Hacker News for GitHub projects...")
        
        repos = []
        
        try:
            response = requests.get(f"{HN_API_BASE}/topstories.json", timeout=30)
            response.raise_for_status()
            story_ids = response.json()[:30]
            
            github_pattern = re.compile(r'https?://github\.com/([^/]+/[^/]+)/?')
            
            for story_id in story_ids:
                try:
                    story_response = requests.get(f"{HN_API_BASE}/item/{story_id}.json", timeout=10)
                    story = story_response.json()
                    
                    if not story or story.get("type") != "story":
                        continue
                    
                    url = story.get("url", "")
                    match = github_pattern.match(url)
                    
                    if match:
                        repo_path = match.group(1)
                        repo_info = self._fetch_repo_info(repo_path)
                        if repo_info and repo_info["stars"] >= MIN_STARS_HN:
                            repo_info["source"] = "hackernews"
                            repo_info["hn_points"] = story.get("score", 0)
                            repos.append(repo_info)
                            logger.info(f"  ✅ HN: {repo_info['name']} ({repo_info['stars']}⭐)")
                            
                except (requests.RequestException, json.JSONDecodeError):
                    continue
            
            logger.info(f"✅ Found {len(repos)} GitHub projects from Hacker News")
            return repos
            
        except requests.RequestException as e:
            logger.error(f"❌ Hacker News API error: {e}")
            return []
    
    def _fetch_repo_info(self, repo_path: str) -> dict | None:
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
    
    def discover_huggingface(self) -> list:
        logger.info("🤗 Scanning HuggingFace for trending models...")
        
        models = []
        
        try:
            params = {"sort": "likes", "direction": -1, "limit": 20, "full": "true"}
            
            response = requests.get(f"{HF_API_BASE}/models", params=params,
                                   headers=self.web_headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            for item in data:
                try:
                    model_id = item.get("modelId", "")
                    likes = item.get("likes", 0)
                    downloads = item.get("downloads", 0)
                    
                    if likes < MIN_LIKES_HF:
                        continue
                    
                    pipeline_tag = item.get("pipeline_tag", "unknown")
                    tags = item.get("tags", [])
                    
                    description = f"{pipeline_tag.replace('-', ' ').title()} model"
                    if "library_name" in item:
                        description += f" ({item['library_name']})"
                    
                    models.append({
                        "url": f"https://huggingface.co/{model_id}",
                        "name": model_id,
                        "description": description,
                        "stars": likes,
                        "downloads": downloads,
                        "language": item.get("library_name", "Unknown"),
                        "topics": tags[:5],
                        "pipeline_tag": pipeline_tag,
                        "source": "huggingface",
                        "category": "huggingface"
                    })
                    
                    logger.info(f"  ✅ HF: {model_id} ({likes}❤️)")
                    
                except Exception as e:
                    continue
            
            logger.info(f"✅ Found {len(models)} HuggingFace models")
            return models
            
        except requests.RequestException as e:
            logger.error(f"❌ HuggingFace API error: {e}")
            return []
    
    def is_good_hf_model(self, model: dict) -> bool:
        if model.get('stars', 0) >= 1000:
            logger.info(f"  ✅ Auto-approved (high likes): {model['name']}")
            return True
        
        prompt = f"""Analyze this HuggingFace model and determine if it would be interesting for developers.

Model: {model['name']}
Type: {model.get('pipeline_tag', 'unknown')}
Likes: {model['stars']}
Downloads: {model.get('downloads', 0)}
Tags: {', '.join(model['topics']) if model['topics'] else 'None'}

YES if: Useful AI/ML model, popular open-source model, practical applications, innovative.
NO if: Very niche fine-tune, test/demo model, duplicate, low quality, NSFW.

Answer ONLY "YES" or "NO"."""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.content[0].text.strip().upper()
            is_approved = answer == "YES"
            logger.info(f"  {'✅' if is_approved else '❌'} {model['name']}: {answer}")
            return is_approved
        except Exception as e:
            logger.error(f"❌ Claude API error: {e}")
            return False
    
    def is_english_content(self, repo: dict) -> bool:
        description = repo.get('description', '') or ''
        name = repo.get('name', '')
        
        non_ascii_chars = sum(1 for c in description if ord(c) > 127)
        if len(description) > 0 and non_ascii_chars / len(description) > 0.3:
            logger.info(f"  🌐 Skipped (non-English detected): {name}")
            return False
        
        prompt = f"""Is this GitHub repository primarily in ENGLISH?

Repository: {name}
Description: {description}

YES if English. NO if Chinese/Japanese/Korean/Russian/etc.
Answer ONLY "YES" or "NO"."""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.content[0].text.strip().upper()
            is_english = answer == "YES"
            if not is_english:
                logger.info(f"  🌐 Skipped (non-English): {repo['name']}")
            return is_english
        except Exception as e:
            return True
    
    def is_greater_good(self, repo: dict) -> bool:
        if repo.get('stars', 0) >= 5000:
            logger.info(f"  ✅ Auto-approved (high stars): {repo['name']}")
            return True
        
        prompt = f"""Is this GitHub repo useful for a general developer audience?

Repository: {repo['name']}
Description: {repo['description']}
Language: {repo['language']}
Stars: {repo['stars']}

YES if: Dev tools, useful libraries, open source tools, AI/ML, CLI tools.
NO if: Crypto/meme coins, very niche, abandoned, spam, unclear purpose.

Answer ONLY "YES" or "NO"."""

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
            return False
    
    def is_astronomy_repo(self, repo: dict) -> bool:
        prompt = f"""Is this GitHub repository GENUINELY about astronomy/astrophysics?

Repository: {repo['name']}
Description: {repo['description']}
Topics: {', '.join(repo['topics']) if repo['topics'] else 'None'}

YES ONLY if: Astronomical data analysis, exoplanet tools, telescope software, stellar physics.
NO if: "transit" = deployment, "stellar" = excellent, "orbit" = architecture, space-themed games.

Be STRICT. When in doubt, NO.
Answer ONLY "YES" or "NO"."""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}]
            )
            answer = response.content[0].text.strip().upper()
            is_astro = answer == "YES"
            logger.info(f"  🔭 {'✅' if is_astro else '❌'} Astronomy: {repo['name']}: {answer}")
            return is_astro
        except Exception as e:
            return False
    
    def discover_astronomy_repos(self) -> list:
        logger.info("🔭 Searching for astronomy/astrophysics repositories...")
        
        repos = []
        seen_urls = set()
        
        keywords_to_check = random.sample(ASTRO_KEYWORDS, min(8, len(ASTRO_KEYWORDS)))
        
        for keyword in keywords_to_check:
            search_url = f"{GITHUB_API_BASE}/search/repositories"
            params = {
                "q": f"{keyword} in:name,description,readme stars:>={MIN_STARS_ASTRO}",
                "sort": "updated",
                "order": "desc",
                "per_page": 10
            }
            
            try:
                response = requests.get(search_url, headers=self.headers, params=params, timeout=30)
                
                if response.status_code != 200:
                    continue
                    
                data = response.json()
                
                for item in data.get("items", []):
                    url = item["html_url"]
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    
                    repos.append({
                        "url": url,
                        "name": item["full_name"],
                        "description": item.get("description") or "No description",
                        "stars": item["stargazers_count"],
                        "language": item.get("language") or "Unknown",
                        "topics": item.get("topics", []),
                        "category": "astronomy",
                        "source": "astronomy_search"
                    })
                    
            except requests.RequestException:
                continue
        
        logger.info(f"✅ Found {len(repos)} potential astronomy repositories")
        return repos
    
    def _filter_and_add_repos(self, candidates: list, category: str, needed: int) -> list:
        approved = []
        
        for repo in candidates:
            if len(approved) >= needed:
                break
            
            if self._is_already_processed(repo["url"]):
                logger.info(f"  ⏭️ Skipping (already processed): {repo['name']}")
                continue
            
            if category != "huggingface":
                logger.info(f"🌐 Checking language: {repo['name']}")
                if not self.is_english_content(repo):
                    continue
            
            if category == "astronomy":
                logger.info(f"🔭 Evaluating: {repo['name']} ({repo['stars']}⭐)")
                if self.is_astronomy_repo(repo):
                    approved.append(f"{repo['url']}|astronomy")
                    logger.info(f"  ✨ Added astronomy repo")
            elif category == "huggingface":
                logger.info(f"🤗 Evaluating: {repo['name']} ({repo['stars']}❤️)")
                if self.is_good_hf_model(repo):
                    approved.append(f"{repo['url']}|huggingface")
                    logger.info(f"  ✨ Added HF model")
            else:
                logger.info(f"🤖 Evaluating: {repo['name']} ({repo['stars']}⭐)")
                if self.is_greater_good(repo):
                    approved.append(f"{repo['url']}|general")
                    logger.info(f"  ✨ Added to queue")
        
        return approved
    
    def run(self) -> int:
        """
        Main discovery pipeline.
        Ensures minimum stock per category, APPENDS to queue.
        NO REORDERING - category rotation handled by autoposter.py
        """
        logger.info("🚀 Starting discovery pipeline (v4 - no reorder)...")
        
        queue_counts = self._count_queue_categories()
        logger.info(f"📊 Current queue: {queue_counts['astronomy']} astro, "
                   f"{queue_counts['huggingface']} HF, {queue_counts['general']} general")
        
        needed = {
            "astronomy": max(0, MIN_STOCK_PER_CATEGORY - queue_counts["astronomy"]),
            "huggingface": max(0, MIN_STOCK_PER_CATEGORY - queue_counts["huggingface"]),
            "general": max(0, MIN_STOCK_PER_CATEGORY - queue_counts["general"])
        }
        
        logger.info(f"🎯 Need: {needed['astronomy']} astro, "
                   f"{needed['huggingface']} HF, {needed['general']} general")
        
        new_repos = []
        current_queue = self._load_queue()
        
        # 1. ASTRONOMY
        if needed["astronomy"] > 0:
            logger.info(f"🔭 Searching for {needed['astronomy']} astronomy repos...")
            candidates = self.discover_astronomy_repos()
            random.shuffle(candidates)
            approved = self._filter_and_add_repos(candidates, "astronomy", needed["astronomy"])
            new_repos.extend(approved)
        
        # 2. HUGGINGFACE
        if needed["huggingface"] > 0:
            logger.info(f"🤗 Searching for {needed['huggingface']} HF models...")
            candidates = self.discover_huggingface()
            random.shuffle(candidates)
            approved = self._filter_and_add_repos(candidates, "huggingface", needed["huggingface"])
            new_repos.extend(approved)
        
        # 3. GENERAL
        if needed["general"] > 0:
            logger.info(f"💻 Searching for {needed['general']} general repos...")
            
            general_candidates = []
            
            trending_repos = self.discover_github_trending()
            for repo in trending_repos:
                repo["category"] = "general"
            general_candidates.extend(trending_repos)
            
            hn_repos = self.discover_hackernews()
            for repo in hn_repos:
                repo["category"] = "general"
            general_candidates.extend(hn_repos)
            
            seen_urls = set()
            unique_general = []
            for repo in general_candidates:
                url_clean = repo["url"].rstrip('/')
                if url_clean not in seen_urls:
                    seen_urls.add(url_clean)
                    unique_general.append(repo)
            
            random.shuffle(unique_general)
            approved = self._filter_and_add_repos(unique_general, "general", needed["general"])
            new_repos.extend(approved)
        
        # === SIMPLY APPEND - NO REORDERING! ===
        if new_repos:
            updated_queue = current_queue + new_repos
            self._save_queue(updated_queue)
            logger.info(f"✅ Added {len(new_repos)} repos to END of queue")
        else:
            logger.info("ℹ️ No new repos needed")
        
        final_counts = self._count_queue_categories()
        final_queue = self._load_queue()
        logger.info(f"📋 Final queue: {len(final_queue)} items "
                   f"({final_counts['astronomy']} astro, {final_counts['huggingface']} HF, "
                   f"{final_counts['general']} general)")
        
        return len(new_repos)


def main():
    try:
        discovery = RepoDiscovery()
        added_count = discovery.run()
        logger.info(f"🏁 Discovery complete. {added_count} repos added.")
        return 0
    except Exception as e:
        logger.error(f"❌ Discovery failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
