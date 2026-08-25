from __future__ import annotations
import json, os, pathlib, sys, urllib.parse, urllib.request, re

ROOT = pathlib.Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
CORPUS = ROOT / "data" / "corpus"
API = "https://openapi.band.us"

def get(path, params):
    token = os.environ.get("BAND_ACCESS_TOKEN")
    if not token:
        raise RuntimeError("BAND_ACCESS_TOKEN is not set")
    query = dict(params)
    query["access_token"] = token
    url = API + path + "?" + urllib.parse.urlencode(query)
    req = urllib.request.Request(url, headers={"User-Agent": "blueberry-band-mcp/0.1"})
    with urllib.request.urlopen(req, timeout=60) as response:
        value = json.loads(response.read().decode("utf-8"))
    if value.get("result_code") not in (None, 1):
        raise RuntimeError(json.dumps(value, ensure_ascii=False))
    return value

def pages(path, params, key="items"):
    out, current = [], dict(params)
    while True:
        value = get(path, current)
        data = value.get("result_data", {})
        out.extend(data.get(key, []))
        nxt = data.get("paging", {}).get("next_params")
        if not nxt:
            return out
        current = {k: v for k, v in nxt.items() if k != "access_token"}

def save(name, value):
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")

def result(value):
    return {"content": [{"type": "text", "text": json.dumps(value, ensure_ascii=False, indent=2)}]}

TOOLS = [
    {"name": "band_sync_all", "description": "Sync authorized BAND posts, comments, albums and photos to local raw data.", "inputSchema": {"type": "object", "properties": {"band_key": {"type": "string"}}, "required": ["band_key"]}},
    {"name": "blueberry_search_cases", "description": "Search locally indexed blueberry case documents and return compact source excerpts.", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer"}}, "required": ["query"]}},
]

def call(name, args):
    if name == "band_sync_all":
        band = args.get("band_key") or os.environ.get("BAND_KEY")
        if not band:
            raise RuntimeError("band_key or BAND_KEY is required")
        posts = pages("/v2/band/posts", {"band_key": band, "locale": "ko_KR"})
        comments = {p["post_key"]: pages("/v2/band/post/comments", {"band_key": band, "post_key": p["post_key"]}) for p in posts if p.get("post_key")}
        albums = pages("/v2/band/albums", {"band_key": band})
        photos = {a["photo_album_key"]: pages("/v2/band/album/photos", {"band_key": band, "photo_album_key": a["photo_album_key"]}) for a in albums if a.get("photo_album_key")}
        save("posts.json", {"band_key": band, "items": posts})
        save("comments.json", comments)
        save("albums.json", {"band_key": band, "items": albums})
        save("photos.json", photos)
        return {"synced": True, "posts": len(posts), "comments": sum(map(len, comments.values())), "albums": len(albums), "photos": sum(map(len, photos.values()))}
    if name == "blueberry_search_cases":
        terms = args["query"].lower().split()
        hits = []
        if CORPUS.exists():
            for path in CORPUS.rglob("*.md"):
                text = path.read_text(encoding="utf-8", errors="replace")
                score = sum(text.lower().count(term) for term in terms)
                if score:
                    hits.append({"score": score, "source": str(path.relative_to(ROOT)), "excerpt": re.sub(r"\s+", " ", text)[:1000]})
        return sorted(hits, key=lambda x: x["score"], reverse=True)[:args.get("max_results", 8)]
    raise RuntimeError("unknown tool")

def main():
    for line in sys.stdin:
        request = json.loads(line)
        method, ident = request.get("method"), request.get("id")
        if method == "initialize":
            value = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "blueberry-band-mcp", "version": "0.1.0"}}
        elif method == "notifications/initialized":
            continue
        elif method == "tools/list":
            value = {"tools": TOOLS}
        elif method == "tools/call":
            try:
                value = result(call(request["params"]["name"], request["params"].get("arguments", {})))
            except Exception as exc:
                value = {"isError": True, "content": [{"type": "text", "text": str(exc)}]}
        else:
            value = {}
        sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": ident, "result": value}, ensure_ascii=False) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
