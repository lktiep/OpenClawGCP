const { S3Client, PutObjectCommand } = require("@aws-sdk/client-s3");
const fs = require("fs");
const path = require("path");

// Configuration from environment variables
const ACCOUNT_ID = process.env.R2_ACCOUNT_ID || "851741409acd69e96d6c480584a3c107";
const ACCESS_KEY_ID = process.env.R2_ACCESS_KEY_ID;
const SECRET_ACCESS_KEY = process.env.R2_SECRET_ACCESS_KEY;
const BUCKET_NAME = process.env.R2_BUCKET_NAME || "openclaw-images";
const PUBLIC_DOMAIN = process.env.R2_PUBLIC_DOMAIN || "https://pub-406cc49bf2114c608757721fa88725fa.r2.dev";

if (!ACCESS_KEY_ID || !SECRET_ACCESS_KEY) {
    console.error("Error: Missing R2_ACCESS_KEY_ID or R2_SECRET_ACCESS_KEY env vars.");
    console.error("Set them: export R2_ACCESS_KEY_ID=xxx R2_SECRET_ACCESS_KEY=yyy");
    process.exit(1);
}

const s3Client = new S3Client({
    region: "auto",
    endpoint: `https://${ACCOUNT_ID}.r2.cloudflarestorage.com`,
    credentials: {
        accessKeyId: ACCESS_KEY_ID,
        secretAccessKey: SECRET_ACCESS_KEY,
    },
});

async function uploadFile(filePath) {
    try {
        const fileName = path.basename(filePath);
        const fileContent = fs.readFileSync(filePath);
        
        let contentType = "application/octet-stream";
        if (fileName.endsWith(".jpg") || fileName.endsWith(".jpeg")) contentType = "image/jpeg";
        else if (fileName.endsWith(".png")) contentType = "image/png";
        else if (fileName.endsWith(".gif")) contentType = "image/gif";
        else if (fileName.endsWith(".webp")) contentType = "image/webp";
        else if (fileName.endsWith(".svg")) contentType = "image/svg+xml";
        else if (fileName.endsWith(".pdf")) contentType = "application/pdf";

        const command = new PutObjectCommand({
            Bucket: BUCKET_NAME,
            Key: fileName,
            Body: fileContent,
            ContentType: contentType,
        });

        await s3Client.send(command);
        
        const publicUrl = `${PUBLIC_DOMAIN}/${fileName}`;
        console.log(`\u2705 Upload success!`);
        console.log(`URL: ${publicUrl}`);
        return publicUrl;
    } catch (err) {
        console.error("Upload failed:", err.message || err);
        process.exit(1);
    }
}

const filePath = process.argv[2];
if (!filePath) {
    console.log("Usage: node upload.js <file_path>");
    process.exit(1);
}

uploadFile(filePath);
