from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import os
import httpx
import base64
import io
from dotenv import load_dotenv

app = FastAPI()

# Load environment variables from .env file
load_dotenv()  # loads backend/.env (or project-root .env)

# Enable CORS so your React app can communicate with this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default port
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/data")
async def get_data():
    return {"message": "Hello from Python!"}

@app.get("/")
async def root():
    return {"status": "Server is running!"}

class ImageRequest(BaseModel):
    prompt: str

@app.post("/api/image/generate")
async def generate_image(req: ImageRequest, request: Request, as_image: bool = Query(False, description="Set true to return decoded image bytes when possible")):
    """
    Proxy endpoint to call Bria image generation.
    Provide api_token either as a request header "api_token" or set BRIA_API_TOKEN env var.
    If as_image=true and the Bria response contains base64 image data, the endpoint will return the decoded image bytes (image/png).
    """
    api_token = request.headers.get("api_token") or os.getenv("BRIA_API_TOKEN")
    if not api_token:
        raise HTTPException(status_code=400, detail="Missing api_token header or BRIA_API_TOKEN env var")

    url = "https://engine.prod.bria-api.com/v2/image/generate"
    headers = {
        "Content-Type": "application/json",
        "api_token": api_token,
    }
    payload = {"prompt": req.prompt}

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(url, json=payload, headers=headers)

    # Attempt to parse JSON body
    resp_content = resp.content
    resp_json = None
    try:
        resp_json = resp.json()
    except Exception:
        resp_json = None

    # If caller asks for image and the provider returned an image content-type, stream it directly
    ct = resp.headers.get("content-type", "")
    if as_image and ct.startswith("image/"):
        return StreamingResponse(io.BytesIO(resp_content), media_type=ct)

    # If caller asks for image and we got JSON, try to extract base64 data from common keys
    if as_image and resp_json:
        # common patterns: 'b64_json', 'base64', nested artifacts list with 'base64' or 'b64_json'
        b64_candidates = []

        # top-level keys
        for k in ("b64_json", "base64", "image_base64", "b64"):
            if k in resp_json and isinstance(resp_json[k], str):
                b64_candidates.append(resp_json[k])

        # nested artifacts
        artifacts = resp_json.get("artifacts") or resp_json.get("images") or resp_json.get("data")
        if isinstance(artifacts, list):
            for item in artifacts:
                if not isinstance(item, dict):
                    continue
                for k in ("b64_json", "base64", "b64", "image"):
                    v = item.get(k)
                    if isinstance(v, str):
                        b64_candidates.append(v)
                    # sometimes 'image' is a dict with 'b64_json'
                    if isinstance(v, dict):
                        inner = v.get("b64_json") or v.get("base64")
                        if isinstance(inner, str):
                            b64_candidates.append(inner)

        if b64_candidates:
            # take first candidate
            try:
                img_bytes = base64.b64decode(b64_candidates[0])
                return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")
            except Exception:
                # fall through to returning JSON if decode fails
                pass

    # If response was an error from Bria, forward as 502
    if resp.status_code >= 400:
        detail = {"bria_status": resp.status_code}
        if resp_json is not None:
            detail["body"] = resp_json
        else:
            detail["raw_text"] = resp.text
        raise HTTPException(status_code=502, detail=detail)

    # Default: return the provider JSON or raw text
    if resp_json is not None:
        return JSONResponse(content={"bria_status": resp.status_code, "bria_response": resp_json})
    else:
        return JSONResponse(content={"bria_status": resp.status_code, "bria_response": {"raw_text": resp.text}})
    
if __name__ == "__main__":
    # For local development on Windows: python main.py
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)