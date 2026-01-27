#!/usr/bin/env python3
"""
discovery.py - The Finder (v3)
==============================
Discovers high-quality GitHub repositories from:
1. GitHub Trending page (scraping - daily & weekly)
2. GitHub Trending by language (Python, TypeScript, Rust, Go, etc.)
3. Hacker News (top stories with GitHub links)
4. Astronomy/Astrophysics repositories
5. HuggingFace trending models

NEW in v3:
- Balanced category distribution: 4 astro, 4 HF, 4 general per day
- Round-robin queue ordering: astro → hf → general → astro → ...
- Need-based discovery instead of random chance
- Fallback to general if astro/hf not available
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
MIN_LIKES_HF = 100  # Minimum likes for HuggingFace models

# === NEW: Category targets for balanced distribution ===
TARGET_PER_CATEGORY = 4  # 4 astro + 4 hf + 4 general = 12 posts/day
CATEGORY_ORDER = ["astronomy", "huggingface", "general"]  # Round-robin order

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
        
        # Web scraping headers
        self.web_headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
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
        # Check both with and without trailing slash
        url_clean = url.rstrip('/')
        return (url_clean in self.history or 
                url_clean + '/' in self.history or
                any(url_clean in q for q in current_queue))
    
    def _count_queue_categories(self) -> dict:
        """
        Count how many items of each category are in the queue.
        Returns dict like {"astronomy": 3, "huggingface": 2, "general": 10}
        """
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
    
    def _reorder_queue_round_robin(self, queue: list) -> list:
        """
        Reorder queue in round-robin fashion: astro → hf → general → astro → ...
        This ensures balanced posting throughout the day.
        """
        # Separate by category
        by_category = {"astronomy": [], "huggingface": [], "general": []}
        
        for entry in queue:
            if "|" in entry:
                url, category = entry.rsplit("|", 1)
                if category in by_category:
                    by_category[category].append(entry)
                else:
                    by_category["general"].append(entry)
            else:
                by_category["general"].append(entry)
        
        # Build round-robin order
        reordered = []
        max_len = max(len(by_category[cat]) for cat in CATEGORY_ORDER) if by_category else 0
        
        for i in range(max_len):
            for category in CATEGORY_ORDER:
                if i < len(by_category[category]):
                    reordered.append(by_category[category][i])
        
        logger.info(f"📋 Queue reordered: {len(by_category['astronomy'])} astro, "
                   f"{len(by_category['huggingface'])} HF, {len(by_category['general'])} general")
        
        return reordered
    
    def discover_github_trending(self) -> list:
        """
        Scrape GitHub Trending page for popular repositories.
        This is the main source of high-quality repos.
        """
        logger.info("🔥 Scraping GitHub Trending page...")
        
        repos = []
        seen_urls = set()
        
        # Pick random language and time range for variety
        languages_to_check = random.sample(TRENDING_LANGUAGES, min(3, len(TRENDING_LANGUAGES)))
        time_range = random.choice(TRENDING_RANGES)
        
        for language in languages_to_check:
            url = f"{GITHUB_TRENDING_URL}/{language}?since={time_range}"
            
            try:
                logger.info(f"  📡 Fetching: {url}")
                response = requests.get(url, headers=self.web_headers, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find repo articles
                articles = soup.select('article.Box-row')
                
                for article in articles[:10]:  # Top 10 per language
                    try:
                        # Get repo link
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
                        
                        # Get description
                        desc_elem = article.select_one('p.col-9')
                        description = desc_elem.get_text(strip=True) if desc_elem else "No description"
                        
                        # Get stars
                        stars_elem = article.select_one('a[href*="/stargazers"]')
                        stars_text = stars_elem.get_text(strip=True) if stars_elem else "0"
                        stars = self._parse_stars(stars_text)
                        
                        # Get language
                        lang_elem = article.select_one('[itemprop="programmingLanguage"]')
                        lang = lang_elem.get_text(strip=True) if lang_elem else "Unknown"
                        
                        # Get today's stars (if available)
                        today_elem = article.select_one('span.d-inline-block.float-sm-right')
                        today_stars = today_elem.get_text(strip=True) if today_elem else ""
                        
                        repos.append({
                            "url": repo_url,
                            "name": repo_path,
                            "description": description,
                            "stars": stars,
                            "language": lang,
                            "topics": [],
                            "today_stars": today_stars,
                            "source": f"trending/{language or 'all'}/{time_range}"
                        })
                        
                    except Exception as e:
                        logger.warning(f"  ⚠️ Failed to parse article: {e}")
                        continue
                
            except requests.RequestException as e:
                logger.warning(f"  ⚠️ Failed to fetch {url}: {e}")
                continue
        
        logger.info(f"✅ Found {len(repos)} trending repositories")
        return repos
    
    def _parse_stars(self, stars_text: str) -> int:
        """Parse star count from text like '1.2k' or '45,123'."""
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
        """
        Scrape Hacker News top stories for GitHub repository links.
        """
        logger.info("🔍 Scanning Hacker News for GitHub projects...")
        
        repos = []
        
        try:
            response = requests.get(f"{HN_API_BASE}/topstories.json", timeout=30)
            response.raise_for_status()
            story_ids = response.json()[:30]  # Check top 30 stories
            
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
                        repo_info = self._fetch_repo_info(repo_path)
                        if repo_info:
                            if repo_info["stars"] >= MIN_STARS_HN:
                                repo_info["source"] = "hackernews"
                                repo_info["hn_points"] = story.get("score", 0)
                                repos.append(repo_info)
                                logger.info(f"  ✅ HN: {repo_info['name']} ({repo_info['stars']}⭐, {repo_info['hn_points']} points)")
                            else:
                                logger.info(f"  ⏭️ HN skipped (low stars): {repo_info['name']} ({repo_info['stars']}⭐)")
                            
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
    
    def discover_huggingface(self) -> list:
        """
        Discover trending models from HuggingFace.
        Returns list of models formatted similarly to GitHub repos.
        """
        logger.info("🤗 Scanning HuggingFace for trending models...")
        
        models = []
        
        try:
            # Get trending models sorted by likes
            params = {
                "sort": "likes",
                "direction": -1,
                "limit": 20,
                "full": "true"
            }
            
            response = requests.get(
                f"{HF_API_BASE}/models",
                params=params,
                headers=self.web_headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            for item in data:
                try:
                    model_id = item.get("modelId", "")
                    likes = item.get("likes", 0)
                    downloads = item.get("downloads", 0)
                    
                    # Filter by minimum likes
                    if likes < MIN_LIKES_HF:
                        continue
                    
                    # Get pipeline tag (model type)
                    pipeline_tag = item.get("pipeline_tag", "unknown")
                    tags = item.get("tags", [])
                    
                    # Build description
                    description = f"{pipeline_tag.replace('-', ' ').title()} model"
                    if "library_name" in item:
                        description += f" ({item['library_name']})"
                    
                    models.append({
                        "url": f"https://huggingface.co/{model_id}",
                        "name": model_id,
                        "description": description,
                        "stars": likes,  # Use likes as "stars" equivalent
                        "downloads": downloads,
                        "language": item.get("library_name", "Unknown"),
                        "topics": tags[:5],  # Limit tags
                        "pipeline_tag": pipeline_tag,
                        "source": "huggingface",
                        "category": "huggingface"
                    })
                    
                    logger.info(f"  ✅ HF: {model_id} ({likes}❤️, {downloads:,} downloads)")
                    
                except Exception as e:
                    logger.warning(f"  ⚠️ Failed to parse HF model: {e}")
                    continue
            
            # Also get recently trending (sorted by trending score)
            try:
                trending_response = requests.get(
                    f"{HF_API_BASE}/models",
                    params={"sort": "trending", "direction": -1, "limit": 10},
                    headers=self.web_headers,
                    timeout=30
                )
                if trending_response.status_code == 200:
                    trending_data = trending_response.json()
                    seen_ids = {m["name"] for m in models}
                    
                    for item in trending_data:
                        model_id = item.get("modelId", "")
                        if model_id in seen_ids:
                            continue
                        
                        likes = item.get("likes", 0)
                        if likes < MIN_LIKES_HF // 2:  # Lower threshold for trending
                            continue
                        
                        pipeline_tag = item.get("pipeline_tag", "unknown")
                        
                        models.append({
                            "url": f"https://huggingface.co/{model_id}",
                            "name": model_id,
                            "description": f"{pipeline_tag.replace('-', ' ').title()} model (trending)",
                            "stars": likes,
                            "downloads": item.get("downloads", 0),
                            "language": item.get("library_name", "Unknown"),
                            "topics": item.get("tags", [])[:5],
                            "pipeline_tag": pipeline_tag,
                            "source": "huggingface_trending",
                            "category": "huggingface"
                        })
                        
                        logger.info(f"  🔥 HF Trending: {model_id} ({likes}❤️)")
                        
            except Exception as e:
                logger.warning(f"  ⚠️ Failed to fetch HF trending: {e}")
            
            logger.info(f"✅ Found {len(models)} HuggingFace models")
            return models
            
        except requests.RequestException as e:
            logger.error(f"❌ HuggingFace API error: {e}")
            return []
    
    def is_good_hf_model(self, model: dict) -> bool:
        """
        Use Claude AI to determine if the HuggingFace model is worth sharing.
        """
        # Auto-approve very popular models
        if model.get('stars', 0) >= 1000:
            logger.info(f"  ✅ Auto-approved (high likes): {model['name']} ({model['stars']}❤️)")
            return True
        
        prompt = f"""Analyze this HuggingFace model and determine if it would be interesting and useful for a Turkish developer/AI audience.

Model: {model['name']}
Type: {model.get('pipeline_tag', 'unknown')}
Likes: {model['stars']}
Downloads: {model.get('downloads', 0)}
Tags: {', '.join(model['topics']) if model['topics'] else 'None'}

Criteria for YES:
- Useful AI/ML models (text generation, image generation, embeddings, etc.)
- Popular open-source models (Llama, Mistral, Stable Diffusion variants, etc.)
- Models with practical applications
- Turkish language models (high priority!)
- Innovative or state-of-the-art models

Criteria for NO:
- Fine-tunes with very specific/niche use cases
- Test or demo models
- Duplicate/copy models
- Low quality or incomplete models
- NSFW models

Answer with ONLY "YES" or "NO" - nothing else."""

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
            logger.error(f"❌ Claude API error for {model['name']}: {e}")
            return False
    
    def is_english_content(self, repo: dict) -> bool:
        """
        Use Claude AI to determine if the repository content is primarily in English.
        Filters out Chinese, Russian, Japanese, Korean and other non-English repos.
        """
        # Build context from available data
        description = repo.get('description', '') or ''
        name = repo.get('name', '')
        topics = repo.get('topics', [])
        
        # Quick check: if description contains significant non-ASCII characters
        # that are clearly from non-English languages, we can filter early
        non_ascii_chars = sum(1 for c in description if ord(c) > 127)
        if len(description) > 0 and non_ascii_chars / len(description) > 0.3:
            logger.info(f"  🌐 Skipped (non-English detected): {name}")
            return False
        
        prompt = f"""Analyze this GitHub repository and determine if its content is primarily in ENGLISH.

Repository: {name}
Description: {description}
Topics: {', '.join(topics) if topics else 'None'}

Criteria for YES (English):
- Description is in English
- Repository name uses English words or common programming terms
- Topics are in English

Criteria for NO (Not English):
- Description contains significant Chinese (中文), Japanese (日本語), Korean (한국어), Russian (русский), or other non-English text
- Repository clearly targets non-English speaking audience based on description
- Name or description has non-ASCII characters from non-English alphabets (excluding common programming symbols)

Note: Repositories with minimal/no description should be considered English if the name is in English.
Code/programming language keywords don't count as non-English.
A few non-English words in an otherwise English description is OK (answer YES).

Answer with ONLY "YES" or "NO" - nothing else."""

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
            logger.error(f"❌ Claude API error for language check {repo['name']}: {e}")
            # Default to True to avoid blocking repos on API errors
            return True
    
    def is_greater_good(self, repo: dict) -> bool:
        """
        Use Claude AI to determine if the repository serves the "greater good".
        Filters out meme coins, niche backend libraries, and low-value projects.
        """
        # For trending repos with very high stars, be more lenient
        min_stars_for_auto_approve = 5000
        if repo.get('stars', 0) >= min_stars_for_auto_approve:
            logger.info(f"  ✅ Auto-approved (high stars): {repo['name']} ({repo['stars']}⭐)")
            return True
        
        prompt = f"""Analyze this GitHub repository and determine if it would be useful and interesting for a general developer audience.

Repository: {repo['name']}
Description: {repo['description']}
Language: {repo['language']}
Stars: {repo['stars']}
Topics: {', '.join(repo['topics']) if repo['topics'] else 'None'}
Source: {repo.get('source', 'unknown')}

Criteria for YES:
- Developer tools that boost productivity
- Useful libraries/frameworks with broad appeal
- Open source tools that serve the "greater good"
- Educational or learning resources
- Innovative projects that solve real problems
- AI/ML tools and models
- CLI tools and utilities
- Web frameworks and tools

Criteria for NO:
- Cryptocurrency/meme coins/NFT projects (unless genuinely useful dev tools)
- Highly niche backend libraries with very limited appeal
- Abandoned or low-quality projects
- Spam or self-promotional repos
- Projects with unclear purpose
- Personal config files or dotfiles

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
    
    def is_astronomy_repo(self, repo: dict) -> bool:
        """
        STRICT verification that a repository is genuinely about astronomy/astrophysics.
        """
        prompt = f"""You are an expert astronomer. Analyze this GitHub repository and determine if it is GENUINELY related to astronomy, astrophysics, or space science.

Repository: {repo['name']}
Description: {repo['description']}
Language: {repo['language']}
Stars: {repo['stars']}
Topics: {', '.join(repo['topics']) if repo['topics'] else 'None'}

STRICT Criteria for YES (must be genuinely astronomical):
- Software for analyzing astronomical data (TESS, Kepler, JWST, etc.)
- Exoplanet detection/analysis tools
- Stellar physics or stellar activity analysis
- Light curve analysis for astronomical purposes
- Spectroscopy tools for astronomical observations
- Orbital mechanics for celestial bodies
- Telescope control or astronomical instrumentation
- Astronomical catalogs or databases

STRICT Criteria for NO:
- "Transit" referring to software deployment or transportation
- "Stellar" meaning excellent/outstanding performance
- "Light" referring to lightweight software
- "Orbit" referring to software architecture patterns
- General physics that's not specifically astronomical
- Space-themed games or entertainment

Be VERY strict. When in doubt, answer NO.

Answer with ONLY "YES" or "NO" - nothing else."""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                messages=[{"role": "user", "content": prompt}]
            )
            
            answer = response.content[0].text.strip().upper()
            is_astro = answer == "YES"
            
            logger.info(f"  🔭 {'✅' if is_astro else '❌'} Astronomy check for {repo['name']}: {answer}")
            return is_astro
            
        except Exception as e:
            logger.error(f"❌ Claude API error for astronomy check {repo['name']}: {e}")
            return False
    
    def discover_astronomy_repos(self) -> list:
        """
        Search GitHub for astronomy and astrophysics repositories.
        """
        logger.info("🔭 Searching for astronomy/astrophysics repositories...")
        
        repos = []
        seen_urls = set()
        
        # Use MORE keywords for better coverage
        keywords_to_check = random.sample(ASTRO_KEYWORDS, min(8, len(ASTRO_KEYWORDS)))
        
        for keyword in keywords_to_check:
            search_url = f"{GITHUB_API_BASE}/search/repositories"
            params = {
                "q": f"{keyword} in:name,description,readme stars:>={MIN_STARS_ASTRO}",
                "sort": "updated",
                "order": "desc",
                "per_page": 10  # Increased from 5
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
                        "description": item.get("description") or "No description provided",
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
        """
        Filter candidates and return up to 'needed' approved repos for the given category.
        """
        approved = []
        
        for repo in candidates:
            if len(approved) >= needed:
                break
            
            # Skip if already processed
            if self._is_already_processed(repo["url"]):
                logger.info(f"  ⏭️ Skipping (already processed): {repo['name']}")
                continue
            
            # Check English content (skip for HuggingFace)
            if category != "huggingface":
                logger.info(f"🌐 Checking language: {repo['name']}")
                if not self.is_english_content(repo):
                    continue
            
            # Apply category-specific filter
            if category == "astronomy":
                logger.info(f"🔭 Evaluating astronomy repo: {repo['name']} ({repo['stars']}⭐)")
                if self.is_astronomy_repo(repo):
                    approved.append(f"{repo['url']}|astronomy")
                    logger.info(f"  ✨ Added astronomy repo: {repo['name']}")
            elif category == "huggingface":
                logger.info(f"🤗 Evaluating HF model: {repo['name']} ({repo['stars']}❤️)")
                if self.is_good_hf_model(repo):
                    approved.append(f"{repo['url']}|huggingface")
                    logger.info(f"  ✨ Added HF model: {repo['name']}")
            else:
                logger.info(f"🤖 Evaluating: {repo['name']} ({repo['stars']}⭐) [{repo.get('source', 'unknown')}]")
                if self.is_greater_good(repo):
                    approved.append(f"{repo['url']}|general")
                    logger.info(f"  ✨ Added to queue: {repo['name']}")
        
        return approved
    
    def run(self) -> int:
        """
        Main discovery pipeline with balanced category distribution.
        Targets: 4 astronomy, 4 HuggingFace, 4 general repos in queue.
        Uses round-robin ordering for balanced daily posting.
        """
        logger.info("🚀 Starting repository discovery pipeline (v3 - balanced mode)...")
        
        # Check current queue composition
        queue_counts = self._count_queue_categories()
        logger.info(f"📊 Current queue: {queue_counts['astronomy']} astro, "
                   f"{queue_counts['huggingface']} HF, {queue_counts['general']} general")
        
        # Calculate how many we need for each category
        needed = {
            "astronomy": max(0, TARGET_PER_CATEGORY - queue_counts["astronomy"]),
            "huggingface": max(0, TARGET_PER_CATEGORY - queue_counts["huggingface"]),
            "general": max(0, TARGET_PER_CATEGORY - queue_counts["general"])
        }
        
        logger.info(f"🎯 Need to find: {needed['astronomy']} astro, "
                   f"{needed['huggingface']} HF, {needed['general']} general")
        
        new_repos = []
        current_queue = self._load_queue()
        
        # === 1. ASTRONOMY: Search if needed ===
        if needed["astronomy"] > 0:
            logger.info(f"🔭 Searching for {needed['astronomy']} astronomy repos...")
            astro_candidates = self.discover_astronomy_repos()
            random.shuffle(astro_candidates)
            astro_approved = self._filter_and_add_repos(astro_candidates, "astronomy", needed["astronomy"])
            new_repos.extend(astro_approved)
            
            # If we couldn't find enough astronomy, note for fallback
            astro_shortfall = needed["astronomy"] - len(astro_approved)
            if astro_shortfall > 0:
                logger.warning(f"⚠️ Could only find {len(astro_approved)} astronomy repos "
                             f"(needed {needed['astronomy']}). Will fill with general.")
                needed["general"] += astro_shortfall
        
        # === 2. HUGGINGFACE: Search if needed ===
        if needed["huggingface"] > 0:
            logger.info(f"🤗 Searching for {needed['huggingface']} HuggingFace models...")
            hf_candidates = self.discover_huggingface()
            random.shuffle(hf_candidates)
            hf_approved = self._filter_and_add_repos(hf_candidates, "huggingface", needed["huggingface"])
            new_repos.extend(hf_approved)
            
            # If we couldn't find enough HF, note for fallback
            hf_shortfall = needed["huggingface"] - len(hf_approved)
            if hf_shortfall > 0:
                logger.warning(f"⚠️ Could only find {len(hf_approved)} HF models "
                             f"(needed {needed['huggingface']}). Will fill with general.")
                needed["general"] += hf_shortfall
        
        # === 3. GENERAL: GitHub Trending + HackerNews ===
        if needed["general"] > 0:
            logger.info(f"💻 Searching for {needed['general']} general repos...")
            
            # Collect from multiple sources
            general_candidates = []
            
            # GitHub Trending
            trending_repos = self.discover_github_trending()
            for repo in trending_repos:
                repo["category"] = "general"
            general_candidates.extend(trending_repos)
            
            # Hacker News
            hn_repos = self.discover_hackernews()
            for repo in hn_repos:
                repo["category"] = "general"
            general_candidates.extend(hn_repos)
            
            # Deduplicate
            seen_urls = set()
            unique_general = []
            for repo in general_candidates:
                url_clean = repo["url"].rstrip('/')
                if url_clean not in seen_urls:
                    seen_urls.add(url_clean)
                    unique_general.append(repo)
            
            random.shuffle(unique_general)
            general_approved = self._filter_and_add_repos(unique_general, "general", needed["general"])
            new_repos.extend(general_approved)
        
        # === 4. Update queue with new repos ===
        if new_repos:
            updated_queue = current_queue + new_repos
            
            # === 5. REORDER queue in round-robin fashion ===
            reordered_queue = self._reorder_queue_round_robin(updated_queue)
            
            self._save_queue(reordered_queue)
            logger.info(f"✅ Added {len(new_repos)} new repos to queue")
        else:
            logger.info("ℹ️ No new repos added to queue")
        
        # Log final stats
        final_counts = self._count_queue_categories()
        final_queue = self._load_queue()
        logger.info(f"📋 Final queue: {len(final_queue)} items "
                   f"({final_counts['astronomy']} astro, {final_counts['huggingface']} HF, "
                   f"{final_counts['general']} general)")
        
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
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())