"""
title: Fetch Tech News
author: arthur
version: 1.1.0
description: Adds a deterministic button to fetch and display RSS news.
requirements: feedparser, requests, python-dateutil
"""

import sys
import asyncio
import subprocess
from datetime import datetime, timedelta
from typing import Optional

# --- DEPENDENCY CHECK ---
# We perform this check to prevent the "No Function class found" error.
# If feedparser is missing, the file usually crashes silently before Open WebUI can load the class.
try:
    import feedparser
    from dateutil import parser
except ImportError:
    # This acts as a self-healing mechanism for Docker containers
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "feedparser",
            "python-dateutil",
            "requests",
        ]
    )
    import feedparser
    from dateutil import parser
# ------------------------


class Action:
    def __init__(self):
        self.feeds = {
            "Kubernetes": "https://kubernetes.io/feed.xml",
            "ArgoCD": "https://blog.argoproj.io/feed",
            "AWS": "https://aws.amazon.com/blogs/aws/feed/",
            "CNCF": "https://www.cncf.io/feed/",
            "The New Stack": "https://thenewstack.io/feed/",
            "Hacker News": "https://hnrss.org/frontpage",
        }
        self.keywords = [
            "kubernetes",
            "k8s",
            "argocd",
            "gitops",
            "sre",
            "devops",
            "platform engineering",
        ]

    async def action(
        self,
        body: dict,
        __user__=None,
        __event_emitter__=None,
        __event_call__=None,
    ) -> Optional[dict]:
        """
        The presence of this method tells Open WebUI to create a button for this function.
        When clicked, this code runs 100% deterministically (no LLM involved).
        """

        # 1. Notify UI that we are working (Status Indicator)
        if __event_emitter__:
            await __event_emitter__(
                {
                    "type": "status",
                    "data": {"description": "Fetching RSS feeds...", "done": False},
                }
            )

        try:
            # 2. Run the Fetch Logic (Sync code needs to be wrapped for async)
            articles = await asyncio.to_thread(self._fetch_news)

            # 3. Format the Output
            if not articles:
                result_text = "No relevant news found in the last 48 hours."
            else:
                result_text = "# 📰 Tech News Briefing\n\n"
                for i, article in enumerate(articles, 1):
                    result_text += f"**{i}. [{article['title']}]({article['link']})**\n"
                    result_text += f"*{article['source']}*\n\n"

            # 4. Clear the Status Indicator
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": "News loaded.", "done": True},
                    }
                )

            # 5. Send the Result as a Message
            # We emit a 'message' event to inject the text directly into the chat
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "message",
                        "data": {"content": result_text},
                    }
                )

        except Exception as e:
            # Handle Crashes Gracefully
            if __event_emitter__:
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {"description": f"Error: {str(e)}", "done": True},
                    }
                )

        # Return None so we don't trigger the LLM to generate extra text
        return None

    def _fetch_news(self):
        """Standard synchronous RSS fetching logic"""
        articles = []
        cutoff = datetime.now() - timedelta(hours=48)

        for source, url in self.feeds.items():
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]:  # Check top 5 from each
                    # Parse Date
                    try:
                        published = entry.get("published", entry.get("updated", ""))
                        dt = parser.parse(published)
                        if dt.tzinfo:
                            dt = dt.replace(tzinfo=None)  # Make naive
                    except:
                        continue

                    if dt < cutoff:
                        continue

                    # Simple Keyword Scoring
                    title = entry.get("title", "")
                    is_relevant = any(k in title.lower() for k in self.keywords)

                    # Include if relevant or if it's from a high-signal source like K8s blog
                    if is_relevant or source in ["Kubernetes", "CNCF"]:
                        articles.append(
                            {
                                "title": title,
                                "link": entry.get("link", "#"),
                                "source": source,
                                "date": dt,
                            }
                        )
            except:
                continue

        # Sort by date
        articles.sort(key=lambda x: x["date"], reverse=True)
        return articles[:15]

