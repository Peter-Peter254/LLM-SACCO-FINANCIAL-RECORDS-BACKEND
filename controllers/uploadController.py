from fastapi import APIRouter, UploadFile, File, HTTPException
import os, requests, logging
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET")

router = APIRouter()

# Setup basic logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/")
async def upload_to_supabase(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        if not SUPABASE_URL or not SUPABASE_KEY or not SUPABASE_BUCKET:
            logger.error("Supabase env variables are not set correctly.")
            raise HTTPException(status_code=500, detail="Server misconfiguration")

        headers = {
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/octet-stream"
        }

        file_path = file.filename
        upload_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{file_path}"

        logger.info(f"Uploading to: {upload_url}")
        logger.info(f"File name: {file_path}")
        logger.info(f"File size: {len(contents)} bytes")

        response = requests.post(upload_url, headers=headers, data=contents)

        logger.info(f"Supabase response code: {response.status_code}")
        logger.info(f"Supabase response body: {response.text}")

        if response.status_code not in [200, 201]:
            # Try to extract message from Supabase response
            try:
                error_detail = response.json().get("message", "Supabase upload failed")
            except Exception:
                error_detail = "Supabase upload failed"

            raise HTTPException(status_code=response.status_code, detail=error_detail)

        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{SUPABASE_BUCKET}/{file_path}"
        logger.info(f"Upload successful: {public_url}")

        return {"url": public_url, "name": file.filename}

    except Exception as e:
        logger.exception("Upload to Supabase failed")
        raise HTTPException(status_code=500, detail=str(e))
