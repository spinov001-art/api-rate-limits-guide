# ⏱️ API Rate Limits Guide 2026 — Every Major API's Limits in One Place

> Stop getting 429 errors. Know the limits before you code.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Updated: March 2026](https://img.shields.io/badge/Updated-March_2026-blue.svg)]()

## AI & LLM APIs

| API | Free Tier | Paid Tier | Burst | Notes |
|-----|-----------|-----------|-------|-------|
| OpenAI GPT-4o | 500 RPM / 30K TPM | 10K RPM / 2M TPM | No | Tier-based, increases with spend |
| OpenAI GPT-4o-mini | 500 RPM / 200K TPM | 30K RPM / 10M TPM | No | Higher limits than GPT-4o |
| Anthropic Claude | 50 RPM / 40K TPM | 4K RPM / 400K TPM | No | Tier 1-4, based on spend |
| Google Gemini | 60 RPM | 1000 RPM | No | Free tier generous |
| Groq (open source) | 30 RPM / 6K TPD | 100 RPM | Yes | Very fast inference |
| Cohere | 5 RPM (trial) | 10K RPM | No | Embed + Generate separate |
| HuggingFace Inference | 300 req/min | Custom | No | Free for public models |

**RPM** = Requests Per Minute · **TPM** = Tokens Per Minute · **TPD** = Tokens Per Day

## Social Media APIs

| API | Free Tier | Auth Required | Notes |
|-----|-----------|:---:|-------|
| Twitter/X v2 | 1500 tweets/15min read | Yes | Write: 17 tweets/24h free |
| Reddit JSON | 30 req/min | No | Add `.json` to any URL |
| Reddit OAuth | 60 req/min | Yes | 100 req/min with OAuth |
| Bluesky AT Protocol | 300 req/5min | Partial | Public endpoints no auth |
| Instagram Graph | 200 req/hr | Yes | Business accounts only |
| LinkedIn | 100 req/day | Yes | Very restrictive |
| Discord | 50 req/s | Yes | Per-route limits vary |
| Telegram Bot | 30 msg/s | Yes | 20 msg/min to same chat |

## Developer Tools

| API | Free Tier | Auth | Notes |
|-----|-----------|:---:|-------|
| GitHub | 60 req/hr | No | 5000 req/hr with token |
| GitLab | 60 req/min | No | 600 req/min with token |
| npm Registry | ~100 req/s | No | Undocumented, be polite |
| PyPI | ~100 req/s | No | Undocumented |
| StackOverflow | 300 req/day | No | 10K/day with key |
| Docker Hub | 100 pulls/6hr | No | 200/6hr with free account |
| Vercel | 100 deploys/day | Yes | Free tier |

## Research & Academic

| API | Free Tier | Auth | Notes |
|-----|-----------|:---:|-------|
| arXiv | 3 req/s | No | Crawl delay enforced |
| PubMed (NCBI) | 3 req/s | No | 10 req/s with free API key |
| Crossref | 50 req/s polite | No | Add email to User-Agent |
| Semantic Scholar | 100 req/5min | No | 1 req/s sustained |
| OpenAlex | 10 req/s | No | Polite pool with email |
| CORE | 10 req/s | Yes (free) | Open access papers |

## Maps & Geo

| API | Free Tier | Auth | Notes |
|-----|-----------|:---:|-------|
| Google Maps | $200/mo credit | Yes | ~28K geocoding calls free |
| Nominatim (OSM) | 1 req/s | No | Strict, will ban abusers |
| Mapbox | 100K tiles/mo | Yes | Generous free tier |
| ip-api.com | 45 req/min | No | Non-commercial only |
| ipinfo.io | 50K req/mo | No | 1K/day without token |

## Finance

| API | Free Tier | Auth | Notes |
|-----|-----------|:---:|-------|
| CoinGecko | 10 req/min | No | 500/min with Pro ($129/mo) |
| Yahoo Finance | ~2K req/hr | No | Undocumented, may change |
| Alpha Vantage | 25 req/day | Yes (free) | 500/day premium |
| Polygon.io | 5 req/min | Yes (free) | Delayed data |
| IEX Cloud | 50K msg/mo | Yes (free) | Real-time stocks |

## Weather & Environment

| API | Free Tier | Auth | Notes |
|-----|-----------|:---:|-------|
| Open-Meteo | Unlimited | No | Best free weather API |
| OpenWeatherMap | 60 req/min | Yes (free) | 1000 req/day free |
| USGS Earthquake | Unlimited | No | Real-time seismic data |
| Air Quality (OpenAQ) | 60 req/min | No | Global air quality |

## Communication

| API | Free Tier | Auth | Notes |
|-----|-----------|:---:|-------|
| Twilio | Trial credits | Yes | ~$0.0075/SMS |
| SendGrid | 100 emails/day | Yes (free) | 40K first month |
| Mailgun | 100 emails/day | Yes (free) | 3-month trial |
| Slack | Varies by plan | Yes | 1 msg/s per channel |

## Cloud Providers

| API | Free Tier | Notes |
|-----|-----------|-------|
| AWS (general) | Varies by service | IAM-based, per-account |
| GCP | $300 credit / 90 days | Per-project quotas |
| Azure | $200 credit / 30 days | Per-subscription |
| Cloudflare Workers | 100K req/day | 10ms CPU per request |
| Vercel Serverless | 100K req/day | 10s execution limit |

---

## How to Handle Rate Limits

### Python: Automatic Retry with Backoff

```python
import time
import requests
from functools import wraps


def retry_on_429(max_retries: int = 3, base_delay: float = 1.0):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    response = func(*args, **kwargs)
                    if response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", base_delay * (2 ** attempt)))
                        print(f"Rate limited. Waiting {retry_after}s...")
                        time.sleep(retry_after)
                        continue
                    return response
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries:
                        raise
                    time.sleep(base_delay * (2 ** attempt))
            return response
        return wrapper
    return decorator


@retry_on_429(max_retries=3)
def fetch(url: str, **kwargs) -> requests.Response:
    return requests.get(url, timeout=30, **kwargs)
```

### Read Rate Limit Headers

```python
def check_rate_limit(response: requests.Response) -> dict:
    return {
        "limit": response.headers.get("X-RateLimit-Limit"),
        "remaining": response.headers.get("X-RateLimit-Remaining"),
        "reset": response.headers.get("X-RateLimit-Reset"),
        "retry_after": response.headers.get("Retry-After"),
    }
```

---

## Contributing

API changed its limits? [Open a PR](https://github.com/Spinov001-art/api-rate-limits-guide/pulls)!

## Related

- [Free APIs List](https://github.com/Spinov001-art/free-apis-list) — 200+ APIs that need no key
- [Python Data Pipelines](https://github.com/Spinov001-art/python-data-pipelines) — Templates that respect rate limits
- [Awesome Web Scraping 2026](https://github.com/Spinov001-art/awesome-web-scraping-2026) — 500+ scraping tools
- [LLM Cost Calculator](https://github.com/Spinov001-art/llm-cost-calculator) — Compare AI API costs
- [More on Dev.to](https://dev.to/0012303)

## License

MIT
