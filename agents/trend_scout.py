import asyncio
import hashlib
from datetime import datetime, timezone
import httpx
import asyncpg
from asyncpg.pool import Pool
from common.types import Trend

HNS_API = "https://hacker-news.firebaseio.com/v0"


async def fetch_hn_top(n: int = 30):
    """Fetch top n stories from Hacker News API"""
    async with httpx.AsyncClient() as c:
        # Get top story IDs
        ids = (await c.get(f"{HNS_API}/topstories.json")).json()[:n]
        
        async def one(i: int):
            """Fetch a single item and convert to Trend"""
            item = (await c.get(f"{HNS_API}/item/{i}.json")).json()
            t = Trend(
                id=hashlib.md5(str(i).encode()).hexdigest(),
                title=item["title"],
                url=item.get("url"),  # Use .get() since URL might be missing for Ask HN posts
                source="hn",
                score=item["score"],
                ts=datetime.fromtimestamp(item["time"], tz=timezone.utc)
            )
            return t
        
        # Fetch all items concurrently
        return await asyncio.gather(*map(one, ids))

async def persist(pool: Pool, trends: list[Trend]):
    """Persist trends to PostgreSQL database"""
    async with pool.acquire() as con: # type: ignore
        await con.executemany( # type: ignore
            "INSERT INTO trends(id, title, url, source, score, ts) "
            "VALUES($1, $2, $3, $4, $5, $6) ON CONFLICT DO NOTHING",
            [t.tuple() for t in trends]
        )


async def main():
    """Main function to fetch trends and persist them"""
    # Create database connection pool
    pool = await asyncpg.create_pool(dsn="postgresql://blog:pw@localhost/blog") # type: ignore
    
    try:
        # Fetch trends from Hacker News
        trends = await fetch_hn_top()
        print("trends fetched:", len(trends))
        exit(0)
        # Persist to database
        await persist(pool, trends) # type: ignore

        print(f"Successfully processed {len(trends)} trends")
        
    finally:
        # Close the pool
        await pool.close() # type: ignore


if __name__ == "__main__":
    asyncio.run(main())
