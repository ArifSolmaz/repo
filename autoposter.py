#!/usr/bin/env python3
"""
autoposter.py - The Creator
===========================
Processes repositories from the queue:
1. Extracts hero image from README
2. Generates Turkish content using Claude AI
3. Posts to Twitter/X with image
4. Archives to Jekyll site
"""

import os
import re
import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup
from anthropic import Anthropic
import tweepy
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
QUEUE_FILE = Path("queue.txt")
HISTORY_FILE = Path("history.txt")
DOCS_DIR = Path("docs")
IMAGES_DIR = DOCS_DIR / "assets" / "images"
POSTS_DIR = DOCS_DIR / "_posts"

# Ensure directories exist
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
POSTS_DIR.mkdir(parents=True, exist_ok=True)


class AutoPoster:
    """Processes repos from queue and posts to Twitter + Jekyll."""
    
    def __init__(self):
        # Initialize Anthropic client
        self.anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        # Initialize Twitter clients (hybrid approach: v2 for tweets, v1.1 for media)
        self.twitter_client = tweepy.Client(
            consumer_key=os.getenv("TWITTER_API_KEY"),
            consumer_secret=os.getenv("TWITTER_API_SECRET"),
            access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
            access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        
        # v1.1 API for media upload
        auth = tweepy.OAuth1UserHandler(
            os.getenv("TWITTER_API_KEY"),
            os.getenv("TWITTER_API_SECRET"),
            os.getenv("TWITTER_ACCESS_TOKEN"),
            os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
        )
        self.twitter_api_v1 = tweepy.API(auth)
        
        # GitHub headers
        self.github_headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            self.github_headers["Authorization"] = f"Bearer {github_token}"
    
    def _load_queue(self) -> list:
        """Load URLs from queue file."""
        if QUEUE_FILE.exists():
            content = QUEUE_FILE.read_text().strip()
            return [url for url in content.split('\n') if url.strip()]
        return []
    
    def _save_queue(self, urls: list):
        """Save URLs to queue file."""
        QUEUE_FILE.write_text('\n'.join(urls) + '\n' if urls else '')
    
    def _add_to_history(self, url: str):
        """Add URL to history file."""
        with open(HISTORY_FILE, 'a') as f:
            f.write(url + '\n')
    
    def _parse_repo_url(self, url: str) -> tuple[str, str]:
        """Extract owner and repo name from GitHub URL."""
        parsed = urlparse(url)
        parts = parsed.path.strip('/').split('/')
        if len(parts) >= 2:
            return parts[0], parts[1]
        raise ValueError(f"Invalid GitHub URL: {url}")
    
    def fetch_repo_data(self, url: str) -> dict:
        """Fetch repository metadata and README content."""
        owner, repo = self._parse_repo_url(url)
        
        # Fetch repo metadata
        api_url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(api_url, headers=self.github_headers, timeout=30)
        response.raise_for_status()
        repo_data = response.json()
        
        # Fetch README content
        readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
        readme_response = requests.get(readme_url, headers=self.github_headers, timeout=30)
        
        readme_content = ""
        readme_html_url = ""
        if readme_response.status_code == 200:
            readme_data = readme_response.json()
            readme_html_url = readme_data.get("html_url", "")
            # Decode base64 content
            import base64
            readme_content = base64.b64decode(readme_data["content"]).decode("utf-8", errors="ignore")
        
        return {
            "url": url,
            "owner": owner,
            "repo": repo,
            "full_name": repo_data["full_name"],
            "description": repo_data.get("description") or "No description",
            "stars": repo_data["stargazers_count"],
            "language": repo_data.get("language") or "Unknown",
            "topics": repo_data.get("topics", []),
            "readme_content": readme_content,
            "readme_html_url": readme_html_url,
            "default_branch": repo_data.get("default_branch", "main")
        }
    
    def extract_hero_image(self, repo_data: dict) -> str | None:
        """
        Extract the first significant image from README.
        Returns the downloaded local path or None.
        """
        readme_content = repo_data["readme_content"]
        owner = repo_data["owner"]
        repo = repo_data["repo"]
        branch = repo_data["default_branch"]
        
        # Patterns to find images in markdown
        patterns = [
            # Standard markdown: ![alt](url)
            r'!\[([^\]]*)\]\(([^)]+)\)',
            # HTML img tags
            r'<img[^>]+src=["\']([^"\']+)["\']',
        ]
        
        image_urls = []
        
        # Find markdown images
        for match in re.finditer(patterns[0], readme_content):
            img_url = match.group(2)
            # Skip badges and shields
            if not any(skip in img_url.lower() for skip in ['badge', 'shield', 'travis', 'codecov', 'github.com/badges']):
                image_urls.append(img_url)
        
        # Find HTML img tags
        for match in re.finditer(patterns[1], readme_content, re.IGNORECASE):
            img_url = match.group(1)
            if not any(skip in img_url.lower() for skip in ['badge', 'shield', 'travis', 'codecov']):
                image_urls.append(img_url)
        
        if not image_urls:
            logger.warning("⚠️  No hero image found in README")
            return None
        
        # Try to download the first valid image
        for img_url in image_urls[:5]:  # Try first 5 candidates
            try:
                # Resolve relative URLs
                if img_url.startswith('./') or img_url.startswith('../') or not img_url.startswith(('http://', 'https://')):
                    # Convert to raw GitHub URL
                    clean_path = img_url.lstrip('./')
                    img_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{clean_path}"
                
                # Handle GitHub user-content URLs
                if 'github.com' in img_url and '/blob/' in img_url:
                    img_url = img_url.replace('github.com', 'raw.githubusercontent.com').replace('/blob/', '/')
                
                logger.info(f"📥 Downloading image: {img_url[:80]}...")
                
                response = requests.get(img_url, timeout=30, stream=True)
                response.raise_for_status()
                
                # Check content type
                content_type = response.headers.get('content-type', '')
                if not content_type.startswith('image/'):
                    continue
                
                # Generate filename
                ext = self._get_image_extension(content_type, img_url)
                filename = f"{repo}-hero{ext}"
                local_path = IMAGES_DIR / filename
                
                # Save image
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                logger.info(f"✅ Hero image saved: {local_path}")
                return str(local_path)
                
            except Exception as e:
                logger.warning(f"⚠️  Failed to download {img_url[:50]}...: {e}")
                continue
        
        return None
    
    def _get_image_extension(self, content_type: str, url: str) -> str:
        """Determine image file extension."""
        type_map = {
            'image/png': '.png',
            'image/jpeg': '.jpg',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'image/svg+xml': '.svg'
        }
        
        if content_type in type_map:
            return type_map[content_type]
        
        # Try to get from URL
        parsed = urlparse(url)
        path_ext = Path(parsed.path).suffix.lower()
        if path_ext in ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg']:
            return path_ext
        
        return '.png'  # Default
    
    def generate_content(self, repo_data: dict) -> dict:
        """
        Generate Turkish content using Claude AI.
        Returns dict with summary, hashtags, and body.
        """
        # Truncate README for context
        readme_preview = repo_data["readme_content"][:3000] if repo_data["readme_content"] else "README not available"
        
        prompt = f"""Analyze this GitHub repository and generate Turkish content for a Twitter post and blog article.

Repository: {repo_data['full_name']}
Description: {repo_data['description']}
Language: {repo_data['language']}
Stars: {repo_data['stars']}⭐
Topics: {', '.join(repo_data['topics']) if repo_data['topics'] else 'None'}

README Preview:
{readme_preview}

Generate a JSON response with EXACTLY these fields:
1. "summary": A single, powerful Turkish sentence (max 180 characters) explaining exactly what this tool does. Be specific and impactful. No fluff, no generic descriptions.
2. "hashtags": Exactly 3 relevant hashtags (without # symbol), e.g. ["Python", "Geliştirici", "Araçlar"]
3. "body": A 2-paragraph Turkish blog post explanation. First paragraph: What problem does it solve? Second paragraph: Key features and why developers should care.

IMPORTANT:
- Write in natural, professional Turkish
- Be specific about what the tool does
- Avoid generic phrases like "Bu araç geliştiriciler için..."
- The summary must be punchy and Twitter-friendly

Respond with ONLY valid JSON, no markdown code blocks."""

        try:
            response = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content_text = response.content[0].text.strip()
            
            # Clean up potential markdown formatting
            if content_text.startswith('```'):
                content_text = re.sub(r'^```(?:json)?\n?', '', content_text)
                content_text = re.sub(r'\n?```$', '', content_text)
            
            content = json.loads(content_text)
            
            # Validate required fields
            required = ['summary', 'hashtags', 'body']
            for field in required:
                if field not in content:
                    raise ValueError(f"Missing required field: {field}")
            
            logger.info(f"✅ Generated Turkish content successfully")
            return content
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Claude response as JSON: {e}")
            # Fallback content
            return {
                "summary": f"{repo_data['full_name']} - {repo_data['description'][:100]}",
                "hashtags": ["OpenSource", "GitHub", "Geliştirici"],
                "body": f"{repo_data['description']}\n\n{repo_data['language']} ile geliştirilmiş bu proje, geliştiricilere faydalı araçlar sunuyor."
            }
        except Exception as e:
            logger.error(f"❌ Content generation failed: {e}")
            raise
    
    def post_to_twitter(self, content: dict, repo_url: str, image_path: str | None) -> str | None:
        """
        Post to Twitter/X with image.
        Uses hybrid approach: v1.1 for media upload, v2 for tweet.
        Returns tweet URL or None.
        """
        # Format tweet text
        hashtags_str = ' '.join(f"#{tag}" for tag in content['hashtags'])
        tweet_text = f"{content['summary']}\n\n🔗 {repo_url}\n\n{hashtags_str}"
        
        # Truncate if too long (280 char limit)
        if len(tweet_text) > 280:
            # Shorten summary to fit
            available = 280 - len(f"\n\n🔗 {repo_url}\n\n{hashtags_str}") - 3
            shortened_summary = content['summary'][:available] + "..."
            tweet_text = f"{shortened_summary}\n\n🔗 {repo_url}\n\n{hashtags_str}"
        
        try:
            media_id = None
            
            # Upload image using v1.1 API
            if image_path and Path(image_path).exists():
                logger.info(f"📤 Uploading image to Twitter...")
                media = self.twitter_api_v1.media_upload(filename=image_path)
                media_id = media.media_id
                logger.info(f"✅ Image uploaded, media_id: {media_id}")
            
            # Post tweet using v2 API
            logger.info(f"🐦 Posting tweet...")
            if media_id:
                response = self.twitter_client.create_tweet(
                    text=tweet_text,
                    media_ids=[media_id]
                )
            else:
                response = self.twitter_client.create_tweet(text=tweet_text)
            
            tweet_id = response.data['id']
            # Construct tweet URL (we don't have username easily, use generic format)
            tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
            
            logger.info(f"✅ Tweet posted: {tweet_url}")
            return tweet_url
            
        except Exception as e:
            logger.error(f"❌ Twitter posting failed: {e}")
            # Continue with Jekyll archiving even if Twitter fails
            return None
    
    def create_jekyll_post(self, repo_data: dict, content: dict, image_path: str | None) -> str:
        """
        Create a Jekyll markdown post for the repository.
        Returns the path to the created file.
        """
        # Generate filename
        today = datetime.now().strftime("%Y-%m-%d")
        slug = re.sub(r'[^a-z0-9]+', '-', repo_data['repo'].lower()).strip('-')
        filename = f"{today}-{slug}.md"
        filepath = POSTS_DIR / filename
        
        # Prepare image reference
        image_ref = ""
        image_frontmatter = ""
        if image_path:
            # Convert to Jekyll-friendly path
            image_filename = Path(image_path).name
            jekyll_image_path = f"/assets/images/{image_filename}"
            image_frontmatter = f'image: "{jekyll_image_path}"'
            image_ref = f"![{repo_data['repo']} Hero Image]({jekyll_image_path})"
        
        # Prepare tags
        tags = content['hashtags'] + [repo_data['language']] if repo_data['language'] != 'Unknown' else content['hashtags']
        tags_str = ', '.join(f'"{tag}"' for tag in tags)
        
        # Build markdown content
        post_content = f"""---
layout: post
title: "{content['summary'].replace('"', '\\"')}"
{image_frontmatter}
repo_url: "{repo_data['url']}"
tags: [{tags_str}]
date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} +0300
---

{image_ref}

{content['body']}

---

⭐ **Stars:** {repo_data['stars']}  
💻 **Language:** {repo_data['language']}  
🔗 **Repository:** [{repo_data['full_name']}]({repo_data['url']})
"""
        
        # Write file
        filepath.write_text(post_content, encoding='utf-8')
        logger.info(f"✅ Jekyll post created: {filepath}")
        
        return str(filepath)
    
    def process_one(self) -> bool:
        """
        Process one repository from the queue.
        Returns True if successful, False otherwise.
        """
        # Load queue
        queue = self._load_queue()
        
        if not queue:
            logger.info("📭 Queue is empty. Nothing to process.")
            return False
        
        # Get first URL
        repo_url = queue[0]
        logger.info(f"🎯 Processing: {repo_url}")
        
        try:
            # Fetch repository data
            logger.info("📡 Fetching repository data...")
            repo_data = self.fetch_repo_data(repo_url)
            
            # Extract hero image
            logger.info("🖼️  Extracting hero image...")
            image_path = self.extract_hero_image(repo_data)
            
            # Generate content with Claude
            logger.info("🤖 Generating Turkish content...")
            content = self.generate_content(repo_data)
            
            # Post to Twitter
            logger.info("🐦 Posting to Twitter...")
            tweet_url = self.post_to_twitter(content, repo_url, image_path)
            
            # Create Jekyll post
            logger.info("📝 Creating Jekyll post...")
            post_path = self.create_jekyll_post(repo_data, content, image_path)
            
            # Cleanup: Remove from queue, add to history
            queue.pop(0)
            self._save_queue(queue)
            self._add_to_history(repo_url)
            
            logger.info(f"✅ Successfully processed: {repo_data['full_name']}")
            if tweet_url:
                logger.info(f"   🐦 Tweet: {tweet_url}")
            logger.info(f"   📝 Post: {post_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to process {repo_url}: {e}")
            # Optionally: move failed URL to end of queue or separate failed list
            return False


def main():
    """Entry point for autoposter script."""
    try:
        poster = AutoPoster()
        success = poster.process_one()
        return 0 if success else 1
    except Exception as e:
        logger.error(f"❌ AutoPoster failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
