---
name: r2-upload
description: Upload files (images, documents) to Cloudflare R2 and get a public URL. Use when you need to host/share an image or file publicly.
metadata:
  {
    "openclaw":
      {
        "emoji": "☁️",
        "os": ["linux", "macos"],
        "requires": { "bins": ["python3"] },
        "env": ["R2_ACCESS_KEY_ID", "R2_SECRET_ACCESS_KEY"]
      }
  }
---

# R2 Upload — Cloudflare R2 File Hosting

Upload images and files to Cloudflare R2 storage and get a permanent public URL.

## When to use

- When you need to **host an image** and share the public URL
- When you generated an image and want to **send it in chat** (Telegram, Zalo, etc.)
- When you need to **store files permanently** in the cloud

## Environment Variables (Required)

| Variable | Description |
|----------|-------------|
| `R2_ACCESS_KEY_ID` | Cloudflare R2 access key |
| `R2_SECRET_ACCESS_KEY` | Cloudflare R2 secret key |
| `R2_ACCOUNT_ID` | Cloudflare account ID (default: `851741409acd69e96d6c480584a3c107`) |
| `R2_BUCKET_NAME` | R2 bucket name (default: `openclaw-images`) |
| `R2_PUBLIC_DOMAIN` | Public domain (default: `https://pub-406cc49bf2114c608757721fa88725fa.r2.dev`) |

## Option A: Python (recommended, auto-installs boto3)

```shell
python3 /app/skills/r2-upload/scripts/upload.py /path/to/image.jpg
```

Upload with custom key:
```shell
python3 /app/skills/r2-upload/scripts/upload.py /path/to/photo.png --key "agents/my-photo.png"
```

Upload from URL:
```shell
python3 /app/skills/r2-upload/scripts/upload.py "https://example.com/image.jpg"
```

## Option B: Node.js (requires @aws-sdk/client-s3)

First install (one-time):
```shell
cd /app/skills/r2-upload/scripts && npm install @aws-sdk/client-s3
```

Then upload:
```shell
node /app/skills/r2-upload/scripts/upload.js /path/to/image.jpg
```

## Output

```
✅ Upload success!
URL: https://pub-406cc49bf2114c608757721fa88725fa.r2.dev/image.jpg
```

## Important Notes

- Max file size: 300MB (R2 free tier)
- Files are **publicly accessible** once uploaded
- Duplicate filenames are **overwritten** — use `--key` for unique paths
- To change bucket/domain: set `R2_BUCKET_NAME` and `R2_PUBLIC_DOMAIN` env vars
