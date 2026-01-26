# Turkish Repo Showcase - Güncellemeler

## 🐛 Bug Fix: 10 Yıldızlı Repo Nasıl Seçildi?

### Problem
`discovery.py`'de Hacker News'den gelen repolar için `MIN_STARS` kontrolü yapılmıyordu!

```python
# ESKI KOD (discover_hackernews fonksiyonu)
if match:
    repo_path = match.group(1)
    repo_info = self._fetch_repo_info(repo_path)
    if repo_info:
        repos.append(repo_info)  # ❌ Star kontrolü yok!
```

### Çözüm
```python
# YENİ KOD
if repo_info:
    # FIX: Apply MIN_STARS filter to HN repos too!
    if repo_info["stars"] >= MIN_STARS:
        repos.append(repo_info)
        logger.info(f"  ✅ HN repo accepted: {repo_info['name']} ({repo_info['stars']}⭐)")
    else:
        logger.info(f"  ⏭️  HN repo skipped (low stars): {repo_info['name']} ({repo_info['stars']}⭐ < {MIN_STARS})")
```

---

## ✨ Feature: Genişletilmiş Tweet Formatı

### Eski Format
```
{summary}

🔗 {github_repo_url}

#Tag1 #Tag2 #Tag3
```

### Yeni Format
```
{summary}

{first_paragraph}

🔗 {jekyll_site_url}

#Tag1 #Tag2 #Tag3
```

### Değişiklikler (`autoposter.py`)

1. **Jekyll URL üretimi eklendi:**
   ```python
   SITE_BASE_URL = "https://arifsolmaz.github.io/turkish-repo-showcase"
   
   def _generate_jekyll_url(self, repo_name: str) -> str:
       now_istanbul = datetime.now(ISTANBUL_TZ)
       today = now_istanbul.strftime("%Y/%m/%d")
       slug = re.sub(r'[^a-z0-9]+', '-', repo_name.lower()).strip('-')
       return f"{SITE_BASE_URL}/{today}/{slug}/"
   ```

2. **İlk paragraf çıkarılıyor:**
   ```python
   paragraphs = [p.strip() for p in content['body'].split('\n\n') if p.strip()]
   content["first_paragraph"] = paragraphs[0] if paragraphs else ""
   ```

3. **Twitter post formatı güncellendi:**
   ```python
   tweet_text = f"{content['summary']}\n\n{first_para}\n\n🔗 {jekyll_url}\n\n{hashtags_str}"
   ```

4. **Bluesky post formatı güncellendi:**
   ```python
   post_text = f"{content['summary']}\n\n{first_para}\n\n🔗 {jekyll_url}\n\n{hashtags_str}"
   ```

5. **Telegram bildirimi Jekyll URL içeriyor:**
   ```python
   if jekyll_url:
       message += f"\n📄 [Detaylı İnceleme]({jekyll_url})"
   ```

---

## 📁 Güncellenen Dosyalar

1. `discovery.py` - HN repoları için MIN_STARS kontrolü
2. `autoposter.py` - Jekyll URL + ilk paragraf

Bu dosyaları GitHub'daki repo'nuza kopyalayın.
