# Phase 3 - Message Board

A simple message board web application where users can post messages with optional images.

## Live Demo
- Frontend: http://cindyho.work/
- API (List Posts): http://cindyho.work/api/post

## Features
- Create message with optional image
- Upload images to AWS S3
- Serve images via CloudFront CDN
- List latest posts
- Delete posts

## Tech Stack
- Backend: FastAPI (Python)
- Database: AWS RDS MySQL
- Storage: AWS S3
- CDN: AWS CloudFront
- Reverse Proxy & Static Hosting: Nginx on EC2
- Deployment: Docker on AWS EC2

## Environment Variables
Create a `.env` file on the server (do not commit):

