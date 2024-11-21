from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import praw
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Reddit Analysis Tool")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent=os.getenv("REDDIT_USER_AGENT")
)

class SearchQuery(BaseModel):
    keyword: str
    limit: int = 10

@app.post("/api/search")
async def search_reddit(query: SearchQuery):
    try:
        submissions = reddit.subreddit("all").search(
            query.keyword,
            limit=query.limit
        )
        
        results = []
        for submission in submissions:
            results.append({
                "title": submission.title,
                "score": submission.score,
                "url": submission.url,
                "created_utc": datetime.fromtimestamp(submission.created_utc).isoformat(),
                "num_comments": submission.num_comments,
                "subreddit": submission.subreddit.display_name
            })
        
        return {"status": "success", "data": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)