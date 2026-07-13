"""
UUID Generator API
Generate UUIDs v1, v4. Pure Python, zero deps.
"""

import uuid

from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import time as _t, threading as _th
_rl_win, _rl_max, _rl_hits, _rl_lk = 60, 60, {}, _th.Lock()

async def _rate_limit(request):
    from fastapi import Request, HTTPException
    ip = (request.headers.get('X-Forwarded-For','') or request.headers.get('X-Real-IP','') or (request.client.host if request.client else '127.0.0.1')).split(',')[0].strip()
    now = _t.time()
    with _rl_lk:
        e = _rl_hits.get(ip)
        if e:
            if now - e['s'] > _rl_win: e['s'], e['c'] = now, 1
            else:
                e['c'] += 1
                if e['c'] > _rl_max: raise HTTPException(429, 'Too many requests')
        else: _rl_hits[ip] = {'s': now, 'c': 1}
    return True

app = FastAPI(title="UUID Generator API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.api_route("/health", methods=["GET", "HEAD"])
async def health():
    return {"status": "ok"}



class UUIDResult(BaseModel):
    uuid: str
    version: int


):
    if version == 1:
        val = str(uuid.uuid1())
    else:
        val = str(uuid.uuid4())
    return UUIDResult(uuid=val, version=version)


@app.get("/generate-batch")
async def generate_batch(
    count: int = Query(10, ge=1, le=100),
    version: int = Query(4, ge=1, le=4),
):
    vals = [str(uuid.uuid4()) if version == 4 else str(uuid.uuid1()) for _ in range(count)]
    return {"uuids": vals}
