#!/usr/bin/env python3
"""
autoposter.py - The Creator
===========================
Processes repositories from the queue:
1. Extracts hero image from README
2. Generates Turkish content using Claude AI
3. Posts to Twitter/X with image (links to Jekyll site)
4. Posts to Bluesky with image (links to Jekyll site)
5. Archives to Jekyll site
6. Sends Telegram notification
"""

import os
import re
import json
import logging
import hashlib
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup
from anthropic import Anthropic
import tweepy
from atproto import Client as BlueskyClient
from dotenv import load_dotenv
from PIL import Image
import io

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

# Istanbul timezone (+03:00)
ISTANBUL_TZ = timezone(timedelta(hours=3))

# Site URL for Jekyll
SITE_BASE_URL = "https://arifsolmaz.github.io/depo"

# Minimum stars threshold (safety check before posting)
MIN_STARS = 50
MIN_STARS_ASTRO = 3
MIN_LIKES_HF = 100  # Minimum likes for HuggingFace models

# Telegram settings
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Bluesky settings
BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
BLUESKY_APP_PASSWORD = os.getenv("BLUESKY_APP_PASSWORD")

# Ensure directories exist
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
POSTS_DIR.mkdir(parents=True, exist_ok=True)


def send_telegram_notification(repo_name: str, summary: str, repo_url: str, tweet_url: str = None, bluesky_url: str = None, category: str = "general", jekyll_url: str = None):
    """Send a Telegram notification when a new repo is posted."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("⚠️  Telegram credentials not set, skipping notification")
        return False
    
    # Category emoji
    if category == "astronomy":
        cat_emoji = "🔭"
        cat_label = "Astronomi"
    elif category == "huggingface":
        cat_emoji = "🤗"
        cat_label = "HuggingFace Model"
    else:
        cat_emoji = "💻"
        cat_label = "GitHub"
    
    # Build message
    link_label = "HuggingFace'te Gör" if category == "huggingface" else "GitHub'da Gör"
    message = f"""🚀 *Yeni {'Model' if category == 'huggingface' else 'Repo'} Paylaşıldı!*

{cat_emoji} *Kategori:* {cat_label}
📦 *{repo_name}*

📝 {summary}

🔗 [{link_label}]({repo_url})"""
    
    if jekyll_url:
        message += f"\n📄 [Detaylı İnceleme]({jekyll_url})"
    
    if tweet_url:
        message += f"\n🐦 [Tweet'i Gör]({tweet_url})"
    
    if bluesky_url:
        message += f"\n🦋 [Bluesky'da Gör]({bluesky_url})"
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        logger.info("✅ Telegram notification sent!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Telegram notification failed: {e}")
        return False


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
    
    def _parse_hf_url(self, url: str) -> str:
        """Extract model ID from HuggingFace URL."""
        # URL format: https://huggingface.co/org/model-name
        parsed = urlparse(url)
        model_id = parsed.path.strip('/')
        return model_id
    
    def fetch_hf_model_data(self, url: str) -> dict:
        """Fetch HuggingFace model metadata."""
        model_id = self._parse_hf_url(url)
        
        # Fetch model metadata from HuggingFace API
        api_url = f"https://huggingface.co/api/models/{model_id}"
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        model_data = response.json()
        
        # Try to get README/model card
        readme_content = ""
        try:
            readme_url = f"https://huggingface.co/{model_id}/raw/main/README.md"
            readme_response = requests.get(readme_url, timeout=15)
            if readme_response.status_code == 200:
                readme_content = readme_response.text
        except:
            pass
        
        # Build description from model info
        pipeline_tag = model_data.get("pipeline_tag", "unknown")
        library = model_data.get("library_name", "")
        description = f"{pipeline_tag.replace('-', ' ').title()}"
        if library:
            description += f" ({library})"
        
        return {
            "url": url,
            "owner": model_id.split('/')[0] if '/' in model_id else "unknown",
            "repo": model_id.split('/')[-1] if '/' in model_id else model_id,
            "full_name": model_id,
            "description": description,
            "stars": model_data.get("likes", 0),
            "downloads": model_data.get("downloads", 0),
            "language": library or "Unknown",
            "topics": model_data.get("tags", [])[:5],
            "pipeline_tag": pipeline_tag,
            "readme_content": readme_content,
            "default_branch": "main",
            "is_huggingface": True
        }
    
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
                content_type = response.headers.get('content-type', '').split(';')[0].strip()
                
                # Skip SVG files (don't render well on social media)
                if 'svg' in content_type.lower() or img_url.lower().endswith('.svg'):
                    logger.info(f"  ⏭️  Skipping SVG image")
                    continue
                
                if not content_type.startswith('image/'):
                    continue
                
                # Read first bytes to detect actual content
                content = response.content
                
                # Check if content is actually SVG (sometimes mislabeled)
                if content[:100].strip().startswith(b'<svg') or b'<svg' in content[:500]:
                    logger.info(f"  ⏭️  Skipping SVG image (detected from content)")
                    continue
                
                # Save ORIGINAL image for Jekyll site
                ext = self._get_image_extension(content_type, img_url)
                original_filename = f"{repo}-hero{ext}"
                original_path = IMAGES_DIR / original_filename
                
                with open(original_path, 'wb') as f:
                    f.write(content)
                logger.info(f"✅ Original image saved: {original_path}")
                
                # Create PROCESSED version for social media (JPG, compressed)
                social_path = self._process_image_for_social(content, repo)
                
                # Return both paths
                return {
                    "original": str(original_path),  # For Jekyll
                    "social": social_path  # For Twitter/Bluesky (may be None if processing fails)
                }
                return str(local_path)
                
            except Exception as e:
                logger.warning(f"⚠️  Failed to download {img_url[:50]}...: {e}")
                continue
        
        return None  # Returns None if no image found, or dict with original/social paths
    
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
    
    def _process_image_for_social(self, content: bytes, repo_name: str) -> str | None:
        """
        Process image for social media compatibility:
        - Convert webp/gif/bmp to jpg (Twitter doesn't support webp)
        - Compress to under 900KB (Bluesky limit ~1MB)
        - Handle animated GIFs (use first frame)
        """
        try:
            # Open image with PIL
            img = Image.open(io.BytesIO(content))
            
            # Handle animated GIF - use LAST frame (first frame is often blank/logo intro)
            if hasattr(img, 'n_frames') and img.n_frames > 1:
                last_frame_idx = img.n_frames - 1
                logger.info(f"  🎞️  Animated image detected ({img.n_frames} frames), using last frame ({last_frame_idx})")
                img.seek(last_frame_idx)
            
            # Convert to RGB if necessary (handles RGBA, P mode, etc.)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large (max 2048px on longest side)
            max_dimension = 2048
            if max(img.size) > max_dimension:
                ratio = max_dimension / max(img.size)
                new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                logger.info(f"  📐 Resized to {new_size}")
            
            # Save as JPG with compression (different filename from original)
            filename = f"{repo_name}-hero-social.jpg"
            local_path = IMAGES_DIR / filename
            
            # Try different quality levels to get under 900KB
            for quality in [90, 80, 70, 60, 50]:
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=quality, optimize=True)
                size_kb = buffer.tell() / 1024
                
                if size_kb < 900:
                    # Save to file
                    with open(local_path, 'wb') as f:
                        f.write(buffer.getvalue())
                    logger.info(f"✅ Hero image saved: {local_path} ({size_kb:.0f}KB, quality={quality})")
                    return str(local_path)
            
            # If still too large, resize more aggressively
            ratio = 0.7
            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG', quality=60, optimize=True)
            with open(local_path, 'wb') as f:
                f.write(buffer.getvalue())
            
            size_kb = buffer.tell() / 1024
            logger.info(f"✅ Hero image saved (resized): {local_path} ({size_kb:.0f}KB)")
            return str(local_path)
            
        except Exception as e:
            logger.warning(f"⚠️  Failed to process image: {e}")
            return None
    
    def generate_content(self, repo_data: dict) -> dict:
        """
        Generate Turkish content using Claude AI.
        Returns dict with summary, hashtags, body, and first_paragraph.
        Uses category-specific prompts and hashtags.
        """
        # Truncate README for context
        readme_preview = repo_data["readme_content"][:3000] if repo_data["readme_content"] else "README not available"
        
        category = repo_data.get("category", "general")
        
        # Category-specific prompt instructions
        if category == "huggingface":
            # HuggingFace model specific prompt
            pipeline_tag = repo_data.get("pipeline_tag", "unknown")
            downloads = repo_data.get("downloads", 0)
            
            prompt = f"""Analyze this HuggingFace AI model and generate Turkish content for a Twitter post and blog article.

Model: {repo_data['full_name']}
Type: {pipeline_tag}
Library: {repo_data['language']}
Likes: {repo_data['stars']}❤️
Downloads: {downloads:,}
Tags: {', '.join(repo_data['topics']) if repo_data['topics'] else 'None'}

Model Card Preview:
{readme_preview}

Generate a JSON response with EXACTLY these fields:
1. "summary": A single, powerful Turkish sentence (max 180 characters) explaining what this AI model does and why it's useful. Be specific about capabilities.
2. "hashtags": Exactly 3 relevant AI/ML hashtags (without # symbol), e.g. ["YapayZeka", "LLM", "HuggingFace", "MachineLearning", "DeepLearning", "NLP", "ComputerVision"]
3. "body": A 2-paragraph Turkish blog post explanation for AI/ML practitioners and developers. First paragraph: What is this model and what problem does it solve? Second paragraph: Key features, performance, and use cases.

IMPORTANT FOR HUGGINGFACE CONTENT:
- Use Turkish AI/ML terminology
- Mention model size/parameters if available
- Highlight practical use cases
- Note if it supports Turkish language
- Compare to similar models if relevant

Respond with ONLY valid JSON, no markdown code blocks."""

        elif category == "astronomy":
            hashtag_instruction = '2. "hashtags": Exactly 3 relevant astronomy hashtags (without # symbol), e.g. ["Exoplanet", "Astronomi", "Astrofizik", "TESS", "Kepler", "JWST", "Yıldız", "Gezegen"]'
            audience_instruction = "astronomlar ve astrofizikçiler"
            extra_instruction = """
IMPORTANT FOR ASTRONOMY CONTENT:
- Use proper Turkish astronomical terminology
- Be accurate about scientific concepts
- Target audience is astronomers and astrophysicists
- Hashtags should be astronomy-specific"""
            
            prompt = f"""Analyze this GitHub repository and generate Turkish content for a Twitter post and blog article.

Repository: {repo_data['full_name']}
Description: {repo_data['description']}
Language: {repo_data['language']}
Stars: {repo_data['stars']}⭐
Topics: {', '.join(repo_data['topics']) if repo_data['topics'] else 'None'}
Category: {category}

README Preview:
{readme_preview}

Generate a JSON response with EXACTLY these fields:
1. "summary": A single, powerful Turkish sentence (max 180 characters) explaining exactly what this tool does. Be specific and impactful. No fluff, no generic descriptions.
{hashtag_instruction}
3. "body": A 2-paragraph Turkish blog post explanation for {audience_instruction}. First paragraph: What problem does it solve? Second paragraph: Key features and why they should care.

IMPORTANT:
- Write in natural, professional Turkish
- Be specific about what the tool does
- Avoid generic phrases
- The summary must be punchy and Twitter-friendly
{extra_instruction}

Respond with ONLY valid JSON, no markdown code blocks."""

        else:
            hashtag_instruction = '2. "hashtags": Exactly 3 relevant hashtags (without # symbol), e.g. ["Python", "Geliştirici", "Araçlar"]'
            audience_instruction = "geliştiriciler"
            extra_instruction = ""
        
            prompt = f"""Analyze this GitHub repository and generate Turkish content for a Twitter post and blog article.

Repository: {repo_data['full_name']}
Description: {repo_data['description']}
Language: {repo_data['language']}
Stars: {repo_data['stars']}⭐
Topics: {', '.join(repo_data['topics']) if repo_data['topics'] else 'None'}
Category: {category}

README Preview:
{readme_preview}

Generate a JSON response with EXACTLY these fields:
1. "summary": A single, powerful Turkish sentence (max 180 characters) explaining exactly what this tool does. Be specific and impactful. No fluff, no generic descriptions.
{hashtag_instruction}
3. "body": A 2-paragraph Turkish blog post explanation for {audience_instruction}. First paragraph: What problem does it solve? Second paragraph: Key features and why they should care.

IMPORTANT:
- Write in natural, professional Turkish
- Be specific about what the tool does
- Avoid generic phrases
- The summary must be punchy and Twitter-friendly
{extra_instruction}

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
            
            # Add category to content
            content["category"] = category
            
            # Extract first paragraph for extended social posts
            paragraphs = [p.strip() for p in content['body'].split('\n\n') if p.strip()]
            content["first_paragraph"] = paragraphs[0] if paragraphs else ""
            
            logger.info(f"✅ Generated Turkish content successfully (category: {category})")
            return content
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Claude response as JSON: {e}")
            # Fallback content based on category
            if category == "astronomy":
                hashtags = ["Astronomi", "Astrofizik", "OpenSource"]
            else:
                hashtags = ["OpenSource", "GitHub", "Geliştirici"]
            
            fallback_body = f"{repo_data['description']}\n\n{repo_data['language']} ile geliştirilmiş bu proje."
            return {
                "summary": f"{repo_data['full_name']} - {repo_data['description'][:100]}",
                "hashtags": hashtags,
                "body": fallback_body,
                "first_paragraph": repo_data['description'],
                "category": category
            }
        except Exception as e:
            logger.error(f"❌ Content generation failed: {e}")
            raise
    
    def post_to_twitter(self, content: dict, repo_url: str, image_path: str | None, jekyll_url: str) -> str | None:
        """
        Post to Twitter/X with image.
        Uses hybrid approach: v1.1 for media upload, v2 for tweet.
        Now includes first paragraph and links to Jekyll site.
        Returns tweet URL or None.
        """
        # Format tweet text - EXTENDED FORMAT with first paragraph
        hashtags_str = ' '.join(f"#{tag}" for tag in content['hashtags'])
        first_para = content.get('first_paragraph', '')
        
        # Build tweet: summary + first paragraph + jekyll link + hashtags
        tweet_text = f"{content['summary']}\n\n{first_para}\n\n🔗 {jekyll_url}\n\n{hashtags_str}"
        
        # Twitter Blue has extended limit (~4000 chars), but we'll be safe
        max_length = 4000
        if len(tweet_text) > max_length:
            # Truncate first paragraph to fit
            available = max_length - len(f"{content['summary']}\n\n...\n\n🔗 {jekyll_url}\n\n{hashtags_str}") - 10
            if available > 100:
                shortened_para = first_para[:available] + "..."
                tweet_text = f"{content['summary']}\n\n{shortened_para}\n\n🔗 {jekyll_url}\n\n{hashtags_str}"
            else:
                tweet_text = f"{content['summary']}\n\n🔗 {jekyll_url}\n\n{hashtags_str}"
        
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
            
        except tweepy.errors.Forbidden as e:
            # DETAILED ERROR LOGGING
            logger.error(f"❌ Twitter 403 Forbidden Error!")
            logger.error(f"   Error message: {e}")
            logger.error(f"   API Errors: {e.api_errors if hasattr(e, 'api_errors') else 'N/A'}")
            logger.error(f"   API Codes: {e.api_codes if hasattr(e, 'api_codes') else 'N/A'}")
            logger.error(f"   API Messages: {e.api_messages if hasattr(e, 'api_messages') else 'N/A'}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"   Response Status: {e.response.status_code}")
                logger.error(f"   Response Text: {e.response.text}")
            return None
        except tweepy.errors.TweepyException as e:
            logger.error(f"❌ Twitter API error: {type(e).__name__}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"   Response: {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"❌ Twitter posting failed: {type(e).__name__}: {e}")
            return None
    
    def post_to_bluesky(self, content: dict, repo_url: str, image_path: str | None, jekyll_url: str) -> str | None:
        """
        Post to Bluesky with image.
        Bluesky has 300 grapheme limit - shorter format than Twitter.
        Returns post URL or None.
        """
        if not BLUESKY_HANDLE or not BLUESKY_APP_PASSWORD:
            logger.warning("⚠️  Bluesky credentials not set, skipping")
            return None
        
        # Format post text - Bluesky has strict 300 grapheme limit
        hashtags_str = ' '.join(f"#{tag}" for tag in content['hashtags'])
        
        # Build short post: summary + link + hashtags (no first paragraph)
        post_text = f"{content['summary']}\n\n🔗 {jekyll_url}\n\n{hashtags_str}"
        
        # Bluesky limit is 300 graphemes
        max_length = 300
        if len(post_text) > max_length:
            # Shorten summary to fit
            available = max_length - len(f"\n\n🔗 {jekyll_url}\n\n{hashtags_str}") - 3
            if available > 50:
                shortened_summary = content['summary'][:available] + "..."
                post_text = f"{shortened_summary}\n\n🔗 {jekyll_url}\n\n{hashtags_str}"
            else:
                # Even shorter - just summary and link
                available = max_length - len(f"\n\n🔗 {jekyll_url}") - 3
                shortened_summary = content['summary'][:available] + "..."
                post_text = f"{shortened_summary}\n\n🔗 {jekyll_url}"
        
        try:
            # Login to Bluesky
            client = BlueskyClient()
            client.login(BLUESKY_HANDLE, BLUESKY_APP_PASSWORD)
            logger.info("✅ Logged into Bluesky")
            
            # Upload image if available
            embed = None
            if image_path and Path(image_path).exists():
                logger.info("📤 Uploading image to Bluesky...")
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                # Upload blob
                upload = client.upload_blob(image_data)
                
                # Create embed with image
                embed = {
                    "$type": "app.bsky.embed.images",
                    "images": [
                        {
                            "alt": content['summary'][:100],
                            "image": upload.blob
                        }
                    ]
                }
                logger.info("✅ Image uploaded to Bluesky")
            
            # Create post
            logger.info("🦋 Posting to Bluesky...")
            if embed:
                response = client.send_post(text=post_text, embed=embed)
            else:
                response = client.send_post(text=post_text)
            
            # Construct post URL
            post_uri = response.uri
            # URI format: at://did:plc:xxx/app.bsky.feed.post/xxx
            # Convert to web URL
            parts = post_uri.split('/')
            post_id = parts[-1]
            bluesky_url = f"https://bsky.app/profile/{BLUESKY_HANDLE}/post/{post_id}"
            
            logger.info(f"✅ Bluesky post created: {bluesky_url}")
            return bluesky_url
            
        except Exception as e:
            logger.error(f"❌ Bluesky posting failed: {e}")
            return None
    
    def create_jekyll_post(self, repo_data: dict, content: dict, image_path: str | None) -> tuple[str, str]:
        """
        Create a Jekyll markdown post for the repository.
        Returns tuple of (filepath, jekyll_url).
        """
        # Use Istanbul timezone for consistent date handling
        now_istanbul = datetime.now(ISTANBUL_TZ)
        today = now_istanbul.strftime("%Y-%m-%d")
        slug = re.sub(r'[^a-z0-9]+', '-', repo_data['repo'].lower()).strip('-')
        filename = f"{today}-{slug}.md"
        filepath = POSTS_DIR / filename
        
        # Generate Jekyll URL
        jekyll_url = f"{SITE_BASE_URL}/{now_istanbul.strftime('%Y/%m/%d')}/{slug}/"
        
        # Prepare image reference for frontmatter
        image_frontmatter = ""
        if image_path:
            # Convert to Jekyll-friendly path
            image_filename = Path(image_path).name
            jekyll_image_path = f"/assets/images/{image_filename}"
            image_frontmatter = f'image: "{jekyll_image_path}"'
        
        # Prepare tags
        tags = content['hashtags'] + [repo_data['language']] if repo_data['language'] != 'Unknown' else content['hashtags']
        tags_str = ', '.join(f'"{tag}"' for tag in tags)
        
        # Escape quotes in summary for YAML
        escaped_summary = content['summary'].replace('"', '\\"')
        
        # Category-specific footer
        category = repo_data.get("category", "general")
        if category == "huggingface":
            downloads = repo_data.get('downloads', 0)
            footer = f"""---

❤️ **Likes:** {repo_data['stars']}  
📥 **Downloads:** {downloads:,}  
🤗 **Model:** [{repo_data['full_name']}]({repo_data['url']})
"""
        else:
            footer = f"""---

⭐ **Stars:** {repo_data['stars']}  
💻 **Language:** {repo_data['language']}  
🔗 **Repository:** [{repo_data['full_name']}]({repo_data['url']})
"""
        
        # Build markdown content (image shown via template, not in body)
        post_content = f"""---
layout: post
title: "{escaped_summary}"
{image_frontmatter}
repo_url: "{repo_data['url']}"
tags: [{tags_str}]
date: {now_istanbul.strftime("%Y-%m-%d %H:%M:%S")} +0300
---

{content['body']}

{footer}"""
        
        # Write file
        filepath.write_text(post_content, encoding='utf-8')
        logger.info(f"✅ Jekyll post created: {filepath}")
        
        return str(filepath), jekyll_url
    
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
        
        # Get first entry and parse URL|category format
        queue_entry = queue[0]
        if "|" in queue_entry:
            repo_url, category = queue_entry.split("|", 1)
        else:
            repo_url = queue_entry
            category = "general"
        
        logger.info(f"🎯 Processing: {repo_url} (category: {category})")
        
        try:
            # Fetch data based on category
            logger.info("📡 Fetching data...")
            if category == "huggingface":
                repo_data = self.fetch_hf_model_data(repo_url)
            else:
                repo_data = self.fetch_repo_data(repo_url)
            repo_data["category"] = category
            
            # ========================================
            # SAFETY CHECK: Verify minimum stars/likes
            # ========================================
            if category == "huggingface":
                min_required = MIN_LIKES_HF
                star_label = "❤️"
            elif category == "astronomy":
                min_required = MIN_STARS_ASTRO
                star_label = "⭐"
            else:
                min_required = MIN_STARS
                star_label = "⭐"
            
            if repo_data["stars"] < min_required:
                logger.warning(f"⚠️  Insufficient stars/likes: {repo_data['stars']}{star_label} < {min_required} required")
                logger.warning(f"   Skipping {repo_data['full_name']} and removing from queue")
                
                # Remove from queue but DON'T add to history (so it could be reconsidered later if stars increase)
                queue.pop(0)
                self._save_queue(queue)
                
                # Send notification about skipped repo
                if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
                    skip_message = f"⏭️ *Atlandı (Düşük {'Like' if category == 'huggingface' else 'Yıldız'})*\n\n📦 {repo_data['full_name']}\n{star_label} {repo_data['stars']} < {min_required} gerekli"
                    try:
                        requests.post(
                            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                            json={"chat_id": TELEGRAM_CHAT_ID, "text": skip_message, "parse_mode": "Markdown"},
                            timeout=10
                        )
                    except:
                        pass
                
                return False
            
            logger.info(f"✅ Check passed: {repo_data['stars']}{star_label} >= {min_required}")
            
            # Extract hero image (returns dict with 'original' and 'social' paths, or None)
            logger.info("🖼️  Extracting hero image...")
            image_result = self.extract_hero_image(repo_data)
            
            # Separate paths for Jekyll (original) and social media (processed)
            original_image = image_result.get("original") if image_result else None
            social_image = image_result.get("social") if image_result else None
            
            # Generate content with Claude
            logger.info("🤖 Generating Turkish content...")
            content = self.generate_content(repo_data)
            
            # Create Jekyll post FIRST with ORIGINAL image (so we have the URL)
            logger.info("📝 Creating Jekyll post...")
            post_path, jekyll_url = self.create_jekyll_post(repo_data, content, original_image)
            
            # Post to Twitter with PROCESSED image
            logger.info("🐦 Posting to Twitter...")
            tweet_url = self.post_to_twitter(content, repo_url, social_image, jekyll_url)
            
            # Post to Bluesky with PROCESSED image
            logger.info("🦋 Posting to Bluesky...")
            bluesky_url = self.post_to_bluesky(content, repo_url, social_image, jekyll_url)
            
            # Cleanup: Remove from queue, add to history
            queue.pop(0)
            self._save_queue(queue)
            self._add_to_history(repo_url)
            
            logger.info(f"✅ Successfully processed: {repo_data['full_name']}")
            if tweet_url:
                logger.info(f"   🐦 Tweet: {tweet_url}")
            if bluesky_url:
                logger.info(f"   🦋 Bluesky: {bluesky_url}")
            logger.info(f"   📝 Post: {post_path}")
            logger.info(f"   🔗 Jekyll URL: {jekyll_url}")
            
            # Send Telegram notification (now with Jekyll URL)
            logger.info("📱 Sending Telegram notification...")
            send_telegram_notification(
                repo_name=repo_data['full_name'],
                summary=content['summary'],
                repo_url=repo_url,
                tweet_url=tweet_url,
                bluesky_url=bluesky_url,
                category=category,
                jekyll_url=jekyll_url
            )
            
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