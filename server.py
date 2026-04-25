import base64
import hashlib
import hmac
import io
import json
import os
import re
import shutil
import sqlite3
import time
import traceback
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


ROOT_DIR = Path(__file__).resolve().parent
UPLOADS_DIR = ROOT_DIR / "uploads"
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "vault.db"
ENV_PATH = ROOT_DIR / ".env"
LEGACY_ENV_PATH = ROOT_DIR / "vellathur.env"


def load_env(path: Path) -> None:
    if not path.exists():
        return

    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def load_project_env() -> None:
    load_env(ENV_PATH)
    load_env(LEGACY_ENV_PATH)


def ensure_dirs() -> None:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def use_supabase() -> bool:
    return bool(supabase_url() and supabase_service_key())


def supabase_url() -> str:
    return os.environ.get("SUPABASE_URL", "").rstrip("/")


def supabase_service_key() -> str:
    # Support both backend service-role naming and generic key naming.
    # This keeps existing deployments working while allowing simpler `.env` setup.
    return (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        or os.environ.get("SUPABASE_KEY", "")
        or os.environ.get("SUPABASE_ANON_KEY", "")
    )


def supabase_bucket() -> str:
    return os.environ.get("SUPABASE_STORAGE_BUCKET", "vault-uploads")


def supabase_headers(content_type: str = "application/json") -> dict[str, str]:
    key = supabase_service_key()
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
    }
    if content_type:
        headers["Content-Type"] = content_type
    return headers


def supabase_request(method: str, path: str, body: bytes | None = None, headers: dict | None = None) -> tuple[int, bytes]:
    request = Request(
        f"{supabase_url()}{path}",
        data=body,
        method=method,
        headers=headers or supabase_headers(),
    )
    try:
        with urlopen(request, timeout=20) as response:
            return response.status, response.read()
    except HTTPError as error:
        return error.code, error.read()
    except URLError as error:
        reason = str(error.reason).encode("utf-8", errors="ignore")
        return 0, reason


def should_fallback_to_sqlite(status: int, body: bytes) -> bool:
    details = body.decode("utf-8", errors="ignore")
    if status == 404 and "PGRST205" in details:
        return True
    if status in (401, 403) and "42501" in details:
        return True
    return False


def init_db() -> None:
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS rates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rate_22k_1g REAL NOT NULL,
                rate_22k_8g REAL NOT NULL,
                rate_18k_1g REAL NOT NULL,
                silver_1g REAL NOT NULL,
                market_status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS uploads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                tag TEXT NOT NULL,
                file_path TEXT NOT NULL,
                original_name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )


def json_response(handler: SimpleHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def parse_json(handler: SimpleHTTPRequestHandler) -> dict:
    length = int(handler.headers.get("Content-Length", "0"))
    body = handler.rfile.read(length).decode("utf-8")
    return json.loads(body or "{}")


def admin_passphrase() -> str:
    return os.environ.get("ADMIN_PASSPHRASE", "")


def session_secret() -> str:
    return os.environ.get("SESSION_SECRET", "")


def token_ttl() -> int:
    return int(os.environ.get("SESSION_TTL_SECONDS", "28800"))


def sign_token(payload: dict) -> str:
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    signature = hmac.new(session_secret().encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
    return f"{payload_b64}.{signature_b64}"


def decode_token(token: str) -> dict | None:
    try:
        payload_b64, signature_b64 = token.split(".", 1)
        expected_sig = hmac.new(session_secret().encode("utf-8"), payload_b64.encode("utf-8"), hashlib.sha256).digest()
        actual_sig = base64.urlsafe_b64decode(signature_b64 + "=" * (-len(signature_b64) % 4))
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        payload_raw = base64.urlsafe_b64decode(payload_b64 + "=" * (-len(payload_b64) % 4))
        payload = json.loads(payload_raw.decode("utf-8"))
        if payload.get("exp", 0) < int(time.time()):
            return None
        return payload
    except Exception:
        return None


def make_token() -> str:
    now = int(time.time())
    payload = {
        "role": "admin",
        "iat": now,
        "exp": now + token_ttl(),
    }
    return sign_token(payload)


def bearer_token(handler: SimpleHTTPRequestHandler) -> str:
    header = handler.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return ""
    return header.split(" ", 1)[1].strip()


def require_auth(handler: SimpleHTTPRequestHandler) -> bool:
    token = bearer_token(handler)
    if not token or not session_secret():
        json_response(handler, 401, {"ok": False, "message": "Unauthorized"})
        return False
    payload = decode_token(token)
    if not payload or payload.get("role") != "admin":
        json_response(handler, 401, {"ok": False, "message": "Unauthorized"})
        return False
    return True


def sanitize_filename(filename: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", filename).strip("-")
    return safe or "upload.bin"


def latest_rates() -> dict | None:
    if use_supabase():
        fields = "rate_22k_1g,rate_22k_8g,rate_18k_1g,silver_1g,market_status,created_at"
        status, body = supabase_request(
            "GET",
            f"/rest/v1/rates?select={fields}&order=id.desc&limit=1",
            headers=supabase_headers(content_type=""),
        )
        if status != 200:
            if should_fallback_to_sqlite(status, body):
                with get_db() as conn:
                    row = conn.execute(
                        """
                        SELECT rate_22k_1g, rate_22k_8g, rate_18k_1g, silver_1g, market_status, created_at
                        FROM rates
                        ORDER BY id DESC
                        LIMIT 1
                        """
                    ).fetchone()
                return dict(row) if row else None
            details = body.decode("utf-8", errors="ignore")
            raise RuntimeError(f"Supabase request failed ({status}): {details}")
        rows = json.loads(body.decode("utf-8") or "[]")
        if rows:
            return rows[0]
        # Supabase read succeeded but has no rows. Prefer local fallback data when available.
        with get_db() as conn:
            row = conn.execute(
                """
                SELECT rate_22k_1g, rate_22k_8g, rate_18k_1g, silver_1g, market_status, created_at
                FROM rates
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
        return dict(row) if row else None

    with get_db() as conn:
        row = conn.execute(
            """
            SELECT rate_22k_1g, rate_22k_8g, rate_18k_1g, silver_1g, market_status, created_at
            FROM rates
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()
    return dict(row) if row else None


def recent_uploads() -> list[dict]:
    if use_supabase():
        fields = "title,tag,file_path,original_name,created_at"
        status, body = supabase_request(
            "GET",
            f"/rest/v1/uploads?select={fields}&order=id.desc&limit=12",
            headers=supabase_headers(content_type=""),
        )
        if status != 200:
            if should_fallback_to_sqlite(status, body):
                with get_db() as conn:
                    rows = conn.execute(
                        """
                        SELECT title, tag, file_path, original_name, created_at
                        FROM uploads
                        ORDER BY id DESC
                        LIMIT 12
                        """
                    ).fetchall()
                return [dict(row) for row in rows]
            details = body.decode("utf-8", errors="ignore")
            raise RuntimeError(f"Supabase request failed ({status}): {details}")
        rows = json.loads(body.decode("utf-8") or "[]")
        if rows:
            return rows
        with get_db() as conn:
            local_rows = conn.execute(
                """
                SELECT title, tag, file_path, original_name, created_at
                FROM uploads
                ORDER BY id DESC
                LIMIT 12
                """
            ).fetchall()
        return [dict(row) for row in local_rows]

    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT title, tag, file_path, original_name, created_at
            FROM uploads
            ORDER BY id DESC
            LIMIT 12
            """
        ).fetchall()
    return [dict(row) for row in rows]


def save_rates(payload: dict) -> None:
    if use_supabase():
        status, body = supabase_request(
            "POST",
            "/rest/v1/rates",
            body=json.dumps(payload).encode("utf-8"),
            headers={
                **supabase_headers(),
                "Prefer": "return=minimal",
            },
        )
        if status not in (200, 201, 204):
            if should_fallback_to_sqlite(status, body):
                with get_db() as conn:
                    conn.execute(
                        """
                        INSERT INTO rates (rate_22k_1g, rate_22k_8g, rate_18k_1g, silver_1g, market_status, created_at)
                        VALUES (:rate_22k_1g, :rate_22k_8g, :rate_18k_1g, :silver_1g, :market_status, :created_at)
                        """,
                        payload,
                    )
                return
            details = body.decode("utf-8", errors="ignore")
            raise RuntimeError(f"Supabase request failed ({status}): {details}")
        return

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO rates (rate_22k_1g, rate_22k_8g, rate_18k_1g, silver_1g, market_status, created_at)
            VALUES (:rate_22k_1g, :rate_22k_8g, :rate_18k_1g, :silver_1g, :market_status, :created_at)
            """,
            payload,
        )


def save_upload_metadata(payload: dict) -> None:
    if use_supabase():
        status, body = supabase_request(
            "POST",
            "/rest/v1/uploads",
            body=json.dumps(payload).encode("utf-8"),
            headers={
                **supabase_headers(),
                "Prefer": "return=minimal",
            },
        )
        if status not in (200, 201, 204):
            if should_fallback_to_sqlite(status, body):
                with get_db() as conn:
                    conn.execute(
                        """
                        INSERT INTO uploads (title, tag, file_path, original_name, created_at)
                        VALUES (:title, :tag, :file_path, :original_name, :created_at)
                        """,
                        payload,
                    )
                return
            details = body.decode("utf-8", errors="ignore")
            raise RuntimeError(f"Supabase request failed ({status}): {details}")
        return

    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO uploads (title, tag, file_path, original_name, created_at)
            VALUES (:title, :tag, :file_path, :original_name, :created_at)
            """,
            payload,
        )


def store_upload(file_item, stored_name: str) -> str:
    if use_supabase():
        object_path = f"collections/{stored_name}"
        file_item.file.seek(0)
        status, body = supabase_request(
            "POST",
            f"/storage/v1/object/{quote(supabase_bucket())}/{quote(object_path)}",
            body=file_item.file.read(),
            headers={
                **supabase_headers(content_type="application/octet-stream"),
                "x-upsert": "false",
            },
        )
        if status not in (200, 201):
            details = body.decode("utf-8", errors="ignore")
            raise RuntimeError(f"Supabase request failed ({status}): {details}")
        return f"{supabase_url()}/storage/v1/object/public/{quote(supabase_bucket())}/{quote(object_path)}"

    target = UPLOADS_DIR / stored_name
    file_item.file.seek(0)
    with target.open("wb") as output_file:
        shutil.copyfileobj(file_item.file, output_file)
    return f"uploads/{stored_name}"


class VaultHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT_DIR), **kwargs)

    def do_GET(self) -> None:
        try:
            if self.path == "/api/rates":
                self.handle_get_rates()
                return
            if self.path == "/api/uploads":
                self.handle_get_uploads()
                return
            if self.path == "/api/admin/session":
                self.handle_get_session()
                return
            super().do_GET()
        except Exception as error:
            traceback.print_exc()
            json_response(self, 500, {"ok": False, "message": f"Internal server error: {error}"})

    def do_POST(self) -> None:
        try:
            if self.path == "/api/admin/login":
                self.handle_admin_login()
                return
            if self.path == "/api/update-rate":
                self.handle_update_rate()
                return
            if self.path == "/api/upload-image":
                self.handle_upload_image()
                return
            json_response(self, 404, {"ok": False, "message": "Not Found"})
        except Exception as error:
            traceback.print_exc()
            json_response(self, 500, {"ok": False, "message": f"Internal server error: {error}"})

    def log_message(self, format: str, *args) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {self.address_string()} {format % args}")

    def handle_admin_login(self) -> None:
        try:
            body = parse_json(self)
        except json.JSONDecodeError:
            json_response(self, 400, {"ok": False, "message": "Invalid JSON"})
            return

        if not admin_passphrase() or not session_secret():
            json_response(self, 500, {"ok": False, "message": "Server is missing ADMIN_PASSPHRASE or SESSION_SECRET"})
            return

        if body.get("passphrase") != admin_passphrase():
            json_response(self, 401, {"ok": False, "message": "Invalid passphrase"})
            return

        json_response(self, 200, {"ok": True, "token": make_token()})

    def handle_get_session(self) -> None:
        if not require_auth(self):
            return
        json_response(self, 200, {"ok": True})

    def handle_get_rates(self) -> None:
        try:
            row = latest_rates()
        except RuntimeError as error:
            json_response(self, 502, {"ok": False, "message": str(error)})
            return

        if row is None:
            json_response(
                self,
                200,
                {
                    "ok": True,
                    "rates": None,
                },
            )
            return

        json_response(
            self,
            200,
            {
                "ok": True,
                "rates": row,
            },
        )

    def handle_get_uploads(self) -> None:
        try:
            rows = recent_uploads()
        except RuntimeError as error:
            json_response(self, 502, {"ok": False, "message": str(error)})
            return

        json_response(
            self,
            200,
            {
                "ok": True,
                "items": rows,
            },
        )

    def handle_update_rate(self) -> None:
        if not require_auth(self):
            return

        try:
            body = parse_json(self)
            rates = body.get("rates", {})
            payload = {
                "rate_22k_1g": float(rates["rate22k1g"]),
                "rate_22k_8g": float(rates["rate22k8g"]),
                "rate_18k_1g": float(rates["rate18k1g"]),
                "silver_1g": float(rates["silver1g"]),
                "market_status": str(body["marketStatus"]).strip(),
                "created_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            }
        except (KeyError, TypeError, ValueError):
            json_response(self, 400, {"ok": False, "message": "Invalid rate payload"})
            return

        try:
            save_rates(payload)
        except RuntimeError as error:
            json_response(self, 502, {"ok": False, "message": str(error)})
            return

        json_response(self, 200, {"ok": True, "message": "Successfully Updated"})

    def handle_upload_image(self) -> None:
        if not require_auth(self):
            return

        # Parse multipart form data
        content_type = self.headers.get("Content-Type", "")
        content_length = int(self.headers.get("Content-Length", 0))
        
        if not content_type.startswith("multipart/form-data"):
            json_response(self, 400, {"ok": False, "message": "Invalid content type"})
            return
        
        # Parse boundary
        boundary = None
        for part in content_type.split(";"):
            if "boundary=" in part:
                boundary = part.split("=", 1)[1].strip().strip('"')
                break
        
        if not boundary:
            json_response(self, 400, {"ok": False, "message": "Missing boundary"})
            return
        
        # Read the request body
        body = self.rfile.read(content_length)
        
        # Parse multipart data
        form_fields = {}
        file_item = None
        
        parts = body.split(f"--{boundary}".encode())
        for part in parts[1:-1]:  # Skip first empty and last closing
            if not part.strip():
                continue
                
            # Split headers from content
            header_end = part.find(b"\r\n\r\n")
            if header_end == -1:
                header_end = part.find(b"\n\n")
                if header_end == -1:
                    continue
                header_section = part[:header_end]
                content = part[header_end + 2:]
            else:
                header_section = part[:header_end]
                content = part[header_end + 4:]
            
            # Remove trailing CRLLN or LF
            if content.endswith(b"\r\n"):
                content = content[:-2]
            elif content.endswith(b"\n"):
                content = content[:-1]
            
            # Parse headers
            headers_text = header_section.decode('utf-8', errors='ignore')
            field_name = None
            filename = None
            
            for line in headers_text.split('\n'):
                if 'Content-Disposition:' in line:
                    # Extract name and filename
                    if 'name="' in line:
                        name_start = line.find('name="') + 6
                        name_end = line.find('"', name_start)
                        field_name = line[name_start:name_end]
                    if 'filename="' in line:
                        filename_start = line.find('filename="') + 10
                        filename_end = line.find('"', filename_start)
                        filename = line[filename_start:filename_end]
            
            if not field_name:
                continue
            
            if filename:
                # This is a file field
                if field_name == "collectionFile":
                    file_item = type('FileItem', (), {
                        'filename': filename,
                        'file': io.BytesIO(content)
                    })()
            else:
                # This is a regular form field
                form_fields[field_name] = content.decode('utf-8', errors='ignore')

        title = form_fields.get("title", "").strip()
        tag = form_fields.get("tag", "").strip()

        if not file_item or not title or not tag:
            json_response(self, 400, {"ok": False, "message": "Missing upload data"})
            return

        original_name = sanitize_filename(file_item.filename or "upload.bin")
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        ext = Path(original_name).suffix.lower() or ".bin"
        stored_name = f"{timestamp}-{hashlib.sha1(original_name.encode('utf-8')).hexdigest()[:10]}{ext}"
        created_at = datetime.utcnow().isoformat(timespec="seconds") + "Z"

        try:
            public_path = store_upload(file_item, stored_name)
            save_upload_metadata(
                {
                    "title": title,
                    "tag": tag,
                    "file_path": public_path,
                    "original_name": original_name,
                    "created_at": created_at,
                }
            )
        except RuntimeError as error:
            json_response(self, 502, {"ok": False, "message": str(error)})
            return

        json_response(
            self,
            200,
            {
                "ok": True,
                "message": "Successfully Updated",
                "item": {
                    "title": title,
                    "tag": tag,
                    "filePath": public_path,
                },
            },
        )


def main() -> None:
    load_project_env()
    ensure_dirs()
    init_db()

    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), VaultHandler)
    print(f"Vault server running at http://localhost:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
