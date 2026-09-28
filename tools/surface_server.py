"""Local server for the working surface (#199). Standard library only.

    python tools/surface_server.py                      # full inventory, port 8765
    python tools/surface_server.py --inventory docs/data/route-inventory.slice.json
    python tools/surface_server.py --state path/to/scratch-state.json
    python tools/surface_server.py --glosses path/to/glosses.json   # default docs/data/capability-glosses.json
    python tools/surface_server.py --agent-state path/to/agent.json # default docs/data/working-surface.agent.json

Serves tools/surface/index.html on 127.0.0.1. The surface state IS the repo file
(docs/data/working-surface.json by default): the page GETs it on load and PUTs the whole
state back after every edit. Writes are atomic (temp file, then rename) and pretty-printed
in a fixed key order, so git diffs read well. A PUT carrying a stale If-Match is refused
with 409, so an edit made to the file behind the page's back is never overwritten.

GET /api/doc?path=docs/specs/X.md&anchor=slug serves one markdown section, read-only, from
under docs/ only: the heading whose GitHub-style slug matches, down to the next heading of
the same or a higher level. No anchor, or an anchor that does not match, returns the whole file.

GET /api/glosses serves the plain-language glosses file ({"capabilities": {ID: {title, summary}},
"routes": {ID: {plain}}}), read-only; a missing file serves empty maps.

GET /api/agent-state serves the agent's assessment (same schema as the state), read-only: a
PUT to it is refused with 405, and a missing file is a 404 the page shows as "no assessment yet".
"""
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import unicodedata
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

REPO = Path(__file__).resolve().parent.parent
DOCS = REPO / "docs"
PAGE = REPO / "tools" / "surface" / "index.html"
SCHEMA = "archinity.working-surface/1"

TOP = ["schema", "inventory_commit", "exported_at", "needs", "sessions", "tags", "no_owner",
       "route_global", "route_need", "capability_decision", "notes", "followups"]
ITEM = {
    "needs": ["id", "parent", "statement", "description", "order"],
    "tags": ["capability", "need", "note"],
    "no_owner": ["capability", "note"],
    "route_global": ["route", "state", "reason"],
    "route_need": ["route", "need", "state", "reason", "reopen"],
    "capability_decision": ["capability", "state", "routes", "decided_by", "candidates", "known", "reopen"],
    "notes": ["target", "text"],
    "followups": ["id", "target_type", "target", "kind", "note", "status", "created"],
}


def ordered(obj, keys):
    """Known keys in contract order, then any others sorted, so nothing is dropped."""
    out = {k: obj[k] for k in keys if k in obj}
    out.update({k: obj[k] for k in sorted(obj) if k not in out})
    return out


def canonical(state):
    state = ordered(state, TOP)
    for sec, keys in ITEM.items():
        if isinstance(state.get(sec), list):
            state[sec] = [ordered(x, keys) if isinstance(x, dict) else x for x in state[sec]]
    return state


def render(state):
    return (json.dumps(canonical(state), ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def etag(data):
    return '"' + hashlib.sha256(data).hexdigest()[:16] + '"'


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def shown(path):
    """A path as the page shows it: repo-relative where it can be."""
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return path.as_posix()


# ---------- markdown sections ----------
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")


def slug(text):
    """GitHub's heading anchor: inline markup dropped, lowercased, punctuation removed, spaces to hyphens."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"<[^>]+>", "", text).lower()
    out = []
    for ch in text:
        if ch in " -_" or ch.isalnum() or unicodedata.category(ch).startswith("M"):
            out.append("-" if ch == " " else ch)
    return "".join(out)


def headings(lines):
    """[(line index, level, title, slug)], fenced code skipped, duplicate slugs suffixed -1, -2 as GitHub does."""
    out, seen, fenced = [], {}, False
    for i, line in enumerate(lines):
        if FENCE.match(line):
            fenced = not fenced
            continue
        m = None if fenced else HEADING.match(line)
        if not m:
            continue
        s = slug(m.group(2))
        n = seen.get(s, 0)
        seen[s] = n + 1
        out.append((i, len(m.group(1)), m.group(2), s if n == 0 else f"{s}-{n}"))
    return out


def resolve_doc(rel):
    """A markdown file under docs/, or None. Rejects traversal, absolute paths and non-.md files."""
    if not rel or "\x00" in rel or rel.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", rel):
        return None
    p = (REPO / rel).resolve()
    try:
        p.relative_to(DOCS.resolve())
    except ValueError:
        return None
    return p if p.suffix.lower() == ".md" and p.is_file() else None


def doc_section(p, anchor):
    lines = p.read_text(encoding="utf-8").splitlines()
    hs = headings(lines)
    title = hs[0][2] if hs else p.name
    body = {"path": shown(p), "anchor": anchor or "", "found": False, "title": title,
            "doc_title": title, "markdown": "\n".join(lines)}
    if anchor:
        for k, (i, lvl, text, s) in enumerate(hs):
            if s == anchor.lower():
                end = next((j for j, l2, _, _ in hs[k + 1:] if l2 <= lvl), len(lines))
                body.update(found=True, title=text, markdown="\n".join(lines[i:end]))
                break
    return body


def make_handler(inventory, state_path, glosses, agent_path):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            sys.stderr.write("%s %s\n" % (self.command, fmt % args))

        def send(self, code, body=b"", ctype="text/plain; charset=utf-8", headers=None):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            for k, v in (headers or {}).items():
                self.send_header(k, v)
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def do_GET(self):
            url = urlsplit(self.path)
            path = url.path
            if path in ("/", "/index.html"):
                return self.send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            if path == "/api/inventory":
                return self.send(200, inventory.read_bytes(), "application/json; charset=utf-8",
                                 {"X-Inventory-Path": shown(inventory)})
            if path == "/api/state":
                rel = {"X-State-Path": shown(state_path)}
                if not state_path.exists():
                    return self.send(404, b"no state file yet", headers=rel)
                data = state_path.read_bytes()
                return self.send(200, data, "application/json; charset=utf-8", {"ETag": etag(data), **rel})
            if path == "/api/agent-state":
                # The agent's assessment: read-only here, written only by an agent. Missing is normal.
                rel = {"X-State-Path": shown(agent_path)}
                if not agent_path.exists():
                    return self.send(404, b"no agent assessment yet", headers=rel)
                data = agent_path.read_bytes()
                return self.send(200, data, "application/json; charset=utf-8", {"ETag": etag(data), **rel})
            if path == "/api/glosses":
                # Plain-language glosses of capabilities and routes; a missing file means none yet.
                body = glosses.read_bytes() if glosses.exists() else b'{"capabilities": {}, "routes": {}}'
                return self.send(200, body, "application/json; charset=utf-8",
                                 {"X-Glosses-Path": shown(glosses), "X-Glosses-Present": "1" if glosses.exists() else "0"})
            if path == "/api/doc":
                q = parse_qs(url.query)
                p = resolve_doc((q.get("path") or [""])[0])
                if not p:
                    return self.send(404, b"only markdown files under docs/ are served")
                body = doc_section(p, (q.get("anchor") or [""])[0])
                return self.send(200, json.dumps(body, ensure_ascii=False).encode("utf-8"),
                                 "application/json; charset=utf-8")
            self.send(404, b"not found")

        def do_PUT(self):
            if urlsplit(self.path).path == "/api/agent-state":
                return self.send(405, b"the agent's assessment is read-only", headers={"Allow": "GET"})
            if urlsplit(self.path).path != "/api/state":
                return self.send(404, b"not found")
            try:
                state = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))).decode("utf-8"))
            except (ValueError, UnicodeDecodeError) as e:
                return self.send(400, f"not JSON: {e}".encode())
            if not isinstance(state, dict) or state.get("schema") != SCHEMA:
                return self.send(400, f"schema must be {SCHEMA}".encode())
            want = self.headers.get("If-Match")
            if state_path.exists() and want and want != etag(state_path.read_bytes()):
                return self.send(409, b"the state file changed on disk since this page loaded it")
            data = render(state)
            atomic_write(state_path, data)
            self.send(200, b"saved", headers={"ETag": etag(data)})

    return Handler


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--inventory", default="docs/data/route-inventory.json",
                    help="inventory JSON, relative to the repo root (default: the full inventory)")
    ap.add_argument("--state", default="docs/data/working-surface.json",
                    help="surface state JSON, relative to the repo root or absolute")
    ap.add_argument("--glosses", default="docs/data/capability-glosses.json",
                    help="plain-language glosses JSON, relative to the repo root or absolute; missing means none")
    ap.add_argument("--agent-state", default="docs/data/working-surface.agent.json",
                    help="the agent's assessment JSON, served read-only; relative to the repo root or absolute; "
                         "missing means no assessment yet")
    a = ap.parse_args()
    inventory, state_path = (REPO / a.inventory).resolve(), (REPO / a.state).resolve()
    glosses, agent_path = (REPO / a.glosses).resolve(), (REPO / a.agent_state).resolve()
    if not inventory.exists():
        sys.exit(f"inventory not found: {inventory}")
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), make_handler(inventory, state_path, glosses, agent_path))
    print(f"Working surface: http://127.0.0.1:{a.port}\n  inventory {shown(inventory)}\n"
          f"  state     {shown(state_path)}\n"
          f"  glosses   {shown(glosses)}{'' if glosses.exists() else ' (not there yet: no glosses)'}\nCtrl+C to stop.")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
