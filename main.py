from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from db import get_conn
import os, uuid
import boto3

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET")
CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONT_DOMAIN")

s3 = boto3.client(
    "s3",
    region_name=AWS_REGION,
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)



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


@app.post("/api/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    ext = ""
    if file.filename and "." in file.filename:
        ext = "." + file.filename.split(".")[-1].lower()

    key = f"uploads/{uuid.uuid4().hex}{ext}"

    
    body = await file.read()

    try:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=body,
            ContentType=file.content_type,
            ACL="public-read",  
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

   
    image_url = f"https://{CLOUDFRONT_DOMAIN}/{key}"
    return {"data": {"image_url": image_url}}


@app.delete("/api/posts/{post_id}")
def delete_post(post_id: int):
    conn = None
    try:
        conn = get_conn()  
        cursor = conn.cursor(dictionary=True)

        cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        conn.commit()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Post not found")

        return {"ok": True, "data": {"deleted_id": post_id}}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {e}")
    finally:
        if conn is not None:
            conn.close()