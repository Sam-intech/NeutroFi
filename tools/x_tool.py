# tools/x_tool.py
import re
from datetime import datetime, timedelta
import snscrape.modules.twitter as sntwitter

def _clean(text: str) -> str:
    text = re.sub(r"http\S+|www\S+|https\S+", "", text)
    text = re.sub(r"@\w+|#\w+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:500]

class TwitterSentimentScraper:
    """
    Free Twitter (X) scraper using snscrape. No API key needed.
    Use coin name/symbol and optional since/until window.
    """
    def fetch_posts(
        self,
        query: str,
        since: str | None = None,  # "YYYY-MM-DD"
        until: str | None = None,  # "YYYY-MM-DD"
        limit: int = 50,
        lang: str | None = "en",
    ) -> list[str]:
        # Build snscrape query
        parts = [query]
        if lang: parts.append(f"lang:{lang}")
        if since: parts.append(f"since:{since}")
        if until: parts.append(f"until:{until}")
        q = " ".join(parts)

        results = []
        try:
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(q).get_items()):
                if i >= limit: break
                # combine full text-like fields
                content = getattr(tweet, "rawContent", None) or getattr(tweet, "content", "")
                if content and len(content.strip()) > 20:
                    results.append(content)
        except Exception as e:
            # keep it quiet but fail soft
            print(f"[ERROR] snscrape failed: {e}")
            return []
        return results

    def get_cleaned_posts(
        self,
        coin_symbol_or_name: str,
        trade_date: str | None = None,  # "YYYY-MM-DD"
        window_days: int = 7,
        limit: int = 50,
    ) -> list[str]:
        # Narrow to a recent window around trade_date if provided
        if trade_date:
            try:
                d = datetime.strptime(trade_date, "%Y-%m-%d").date()
            except ValueError:
                d = datetime.utcnow().date()
        else:
            d = datetime.utcnow().date()

        since = (d - timedelta(days=window_days)).isoformat()
        until = (d + timedelta(days=1)).isoformat()  # inclusive-ish

        raw = self.fetch_posts(query=coin_symbol_or_name, since=since, until=until, limit=limit)
        cleaned = [_clean(t) for t in raw if t]
        return cleaned if cleaned else ["No recent tweets found for this coin."]
