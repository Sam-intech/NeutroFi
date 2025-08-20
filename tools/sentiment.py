import praw
import re
import prawcore


class RedditSentimentScraper:
    def __init__(self, client_id, client_secret, user_agent):
        try:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent,
            )
        except Exception as e:
            print(f"[ERROR] Failed to initialize Reddit API: {e}")
            raise

    def fetch_posts(self, coin_symbol, subreddit_list=None, limit=10):
        if subreddit_list is None:
            subreddit_list = [
                "CryptoCurrency",
                "CryptoMarkets",
                "Bitcoin",
                "ethereum",
                "altcoin",
            ]

        results = []
        try:
            for sub in subreddit_list:
                for post in self.reddit.subreddit(sub).search(
                    coin_symbol, sort="new", limit=limit
                ):
                    combined = f"{post.title} {post.selftext}"
                    if len(combined.strip()) > 20:
                        results.append(combined)
        except prawcore.exceptions.RequestException as e:
            print(f"[ERROR] Reddit API request failed: {e}")
            return []
        except prawcore.exceptions.OAuthException as e:
            print(f"[ERROR] Reddit API authentication failed: {e}")
            return []
        return results

    # function for post cleaning and preprocsessing
    def clean_posts(self, texts):
        cleaned = []
        for text in texts:
            text = re.sub(r"http\S+|www\S+|https\S+", "", text)
            text = re.sub(r"@\w+|#\w+", "", text)
            text = re.sub(r"\s+", " ", text).strip()[:500]  # Truncate to 500 characters
            if text:
                cleaned.append(text)
        return cleaned

    def get_cleaned_posts(self, coin_symbol):
        posts = self.fetch_posts(coin_symbol)
        cleaned = self.clean_posts(posts)
        return cleaned if cleaned else ["No recent posts found for this coin."]
