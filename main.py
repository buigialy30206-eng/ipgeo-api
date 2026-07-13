"""
IP Geolocation API
Free IP-to-location lookup. Zero API keys.
"""

import subprocess, json as _json

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="IP Geolocation API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}



class IPResult(BaseModel):
    ip: str
    country: str = ""
    country_code: str = ""
    city: str = ""
    region: str = ""
    isp: str = ""
    timezone: str = ""


def curl_get(url: str) -> dict:
    cmd = ["curl", "-s", "--connect-timeout", "5", "--max-time", "8", url]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return _json.loads(r.stdout) if r.returncode == 0 and r.stdout else {}


@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return {"service": "IP Geolocation API", "version": "1.0.0"}


@app.get("/lookup", response_model=IPResult)
async def lookup(ip: str = Query("", description="IP address to look up. Leave empty for your own IP.")):
    data = curl_get(f"https://ipapi.co/{ip}/json/" if ip else "https://ipapi.co/json/")
    return IPResult(
        ip=data.get("ip", ip or "unknown"),
        country=data.get("country_name", ""),
        country_code=data.get("country_code", ""),
        city=data.get("city", ""),
        region=data.get("region", ""),
        isp=data.get("org", ""),
        timezone=data.get("timezone", ""),
    )
