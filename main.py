"""
IP Geolocation API
Free IP-to-location lookup.
"""
import subprocess, json as _json, time, threading
from fastapi import Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="IP Geolocation API", version="1.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

_cache = {}
_cache_lock = threading.Lock()
CACHE_TTL = 3600  # 1 hour

class IPResult(BaseModel):
    ip: str
    country: str = ""
    country_code: str = ""
    city: str = ""
    region: str = ""
    isp: str = ""
    timezone: str = ""
    error: str = ""

def curl_get(url: str) -> dict:
    cmd = ["curl", "-s", "--connect-timeout", "5", "--max-time", "8", url]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return _json.loads(r.stdout) if r.returncode == 0 and r.stdout else {}
    except:
        return {}

@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok", "cache_size": len(_cache)}

@app.get("/")
async def root():
    return {"service": "IP Geolocation API", "version": "1.1.0"}

@app.get("/lookup", response_model=IPResult)
async def lookup(ip: str = Query("", description="IP address. Leave empty for your own IP.")):
    key = ip or "myip"
    with _cache_lock:
        entry = _cache.get(key)
        if entry and time.time() - entry["ts"] < CACHE_TTL:
            return IPResult(**entry["data"])

    data = curl_get(f"https://ipapi.co/{ip}/json/" if ip else "https://ipapi.co/json/")
    
    result = IPResult(
        ip=data.get("ip", ip or "unknown"),
        country=data.get("country_name", ""),
        country_code=data.get("country_code", ""),
        city=data.get("city", ""),
        region=data.get("region", ""),
        isp=data.get("org", ""),
        timezone=data.get("timezone", ""),
        error=data.get("error", "") if not data.get("ip") else "",
    )

    if not result.error and result.ip != "unknown":
        with _cache_lock:
            _cache[key] = {"data": result.model_dump(), "ts": time.time()}
            if len(_cache) > 500:
                oldest = min(_cache, key=lambda k: _cache[k]["ts"])
                del _cache[oldest]

    return result
