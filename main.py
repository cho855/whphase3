from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any
from db import get_conn

app = FastAPI()

class PostIn(BaseModel):
    content: str
    image_url: Optional[str] = None

@app.get("/api/function")
def function():
    return {"ok": True}

@app.post("/api/posts")
def create_post(payload: PostIn):
    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            INSERT INTO posts (content, image_url)
            VALUES (%s, %s)
            """,
            (payload.content, payload.image_url),
        )
        conn.commit()

        post_id = cursor.lastrowid
        cursor.execute(
            "SELECT id, content, image_url, created_at FROM posts WHERE id = %s",
            (post_id,),
        )
        row = cursor.fetchone()
        return {"data": row}
    finally:
        conn.close()

@app.get("/api/posts")
def list_posts() -> Dict[str, Any]:
    conn = get_conn()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, content, image_url, created_at
            FROM posts
            ORDER BY created_at DESC
            LIMIT 100
            """
        )
        rows = cursor.fetchall()
        return {"data": rows}
    finally:
        conn.close()
