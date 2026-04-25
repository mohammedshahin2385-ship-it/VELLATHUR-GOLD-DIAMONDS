"""
Vellathur Vault API — Vercel Serverless Function

A single Flask application that exposes the admin vault API endpoints.
All persistent storage is handled by Supabase (PostgREST + Storage).
No SQLite or local filesystem writes — Vercel's filesystem is ephemeral.

Adapted from server.py for Vercel's serverless Python runtime.
"""

import base64
import hashlib
import hmac
import io
import json
import os
import re
import time
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from flask import Flask, request, jsonify


# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Supabase helpers
# ---------------------------------------------------------------------------

def supabase_url() -> str:
    return os.environ.get("SUPABASE_URL", "").rstrip("/")


def supabase_service_key() -> str:
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


def supabase_request(
    method: str,
    path: str,
    body: bytes | None = None,
    headers: dict | None = None,
) -> tuple[int, bytes]:
    req = Request(
        f"{supabase_url()}{path}",
        data=body,
        method=method,
        headers=headers or supabase_headers(),
    )
    try:
        with urlopen(req, timeout=20) as response:
            return response.status, response.read()
    except HTTPError as error:
        return error.code, error.read()
    except URLError as error:
        reason = str(error.reason).encode("utf-8", errors="ignore")
        return 0, reason


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------

def admin_passphrase() -> str:
    return os.environ.get("ADMIN_PASSPHRASE", "")


def session_secret() -> str:
    return os.environ.get("SESSION_SECRET", "")


def token_ttl() -> int:
    return int(os.environ.get("SESSION_TTL_SECONDS", "28800"))


def sign_token(payload: dict) -> str:
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    payload_b64 = base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")
    signature = hmac.new(
        session_secret().encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode("ascii").rstrip("=")
    return f"{payload_b64}.{signature_b64}"


def decode_token(token: str) -> dict | None:
    try:
        payload_b64, signature_b64 = token.split(".", 1)
        expected_sig = hmac.new(
            session_secret().encode("utf-8"),
            payload_b64.encode("utf-8"),
            hashlib.sha256,
        ).digest()
        actual_sig = base64.urlsafe_b64decode(
            signature_b64 + "=" * (-len(signature_b64) % 4)
        )
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None
        payload_raw = base64.urlsafe_b64decode(
            payload_b64 + "=" * (-len(payload_b64) % 4)
        )
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


def get_bearer_token() -> str:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return ""
    return header.split(" ", 1)[1].strip()


def require_auth():
    """Return an error response if auth fails, or None if auth succeeds."""
    token = get_bearer_token()
    if not token or not session_secret():
        return jsonify({"ok": False, "message": "Unauthorized"}), 401
    payload = decode_token(token)
    if not payload or payload.get("role") != "admin":
        return jsonify({"ok": False, "message": "Unauthorized"}), 401
    return None


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def sanitize_filename(filename: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", filename).strip("-")
    return safe or "upload.bin"


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/api/rates", methods=["GET"])
def get_rates():
    """Fetch the latest gold/silver rates from Supabase."""
    if not supabase_url() or not supabase_service_key():
        return jsonify({"ok": True, "rates": None})

    fields = "rate_22k_1g,rate_22k_8g,rate_18k_1g,silver_1g,market_status,created_at"
    status, body = supabase_request(
        "GET",
        f"/rest/v1/rates?select={fields}&order=id.desc&limit=1",
        headers=supabase_headers(content_type=""),
    )

    if status != 200:
        details = body.decode("utf-8", errors="ignore")
        return jsonify({"ok": False, "message": f"Supabase error ({status}): {details}"}), 502

    rows = json.loads(body.decode("utf-8") or "[]")
    return jsonify({"ok": True, "rates": rows[0] if rows else None})


@app.route("/api/uploads", methods=["GET"])
def get_uploads():
    """Fetch recent collection uploads from Supabase."""
    if not supabase_url() or not supabase_service_key():
        return jsonify({"ok": True, "items": []})

    fields = "title,tag,file_path,original_name,created_at"
    status, body = supabase_request(
        "GET",
        f"/rest/v1/uploads?select={fields}&order=id.desc&limit=12",
        headers=supabase_headers(content_type=""),
    )

    if status != 200:
        details = body.decode("utf-8", errors="ignore")
        return jsonify({"ok": False, "message": f"Supabase error ({status}): {details}"}), 502

    rows = json.loads(body.decode("utf-8") or "[]")
    return jsonify({"ok": True, "items": rows})


@app.route("/api/admin/login", methods=["POST"])
def admin_login():
    """Authenticate admin with passphrase and return a signed token."""
    try:
        body = request.get_json(force=True) or {}
    except Exception:
        return jsonify({"ok": False, "message": "Invalid JSON"}), 400

    if not admin_passphrase() or not session_secret():
        return jsonify({
            "ok": False,
            "message": "Server is missing ADMIN_PASSPHRASE or SESSION_SECRET",
        }), 500

    if body.get("passphrase") != admin_passphrase():
        return jsonify({"ok": False, "message": "Invalid passphrase"}), 401

    return jsonify({"ok": True, "token": make_token()})


@app.route("/api/admin/session", methods=["GET"])
def admin_session():
    """Verify that the caller has a valid admin session token."""
    auth_error = require_auth()
    if auth_error:
        return auth_error
    return jsonify({"ok": True})


@app.route("/api/update-rate", methods=["POST"])
def update_rate():
    """Publish new gold/silver rates (admin auth required)."""
    auth_error = require_auth()
    if auth_error:
        return auth_error

    try:
        body = request.get_json(force=True) or {}
        rates = body.get("rates", {})
        payload = {
            "rate_22k_1g": float(rates["rate22k1g"]),
            "rate_22k_8g": float(rates["rate22k8g"]),
            "rate_18k_1g": float(rates["rate18k1g"]),
            "silver_1g": float(rates["silver1g"]),
            "market_status": str(body["marketStatus"]).strip(),
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        }
    except (KeyError, TypeError, ValueError):
        return jsonify({"ok": False, "message": "Invalid rate payload"}), 400

    status, body_resp = supabase_request(
        "POST",
        "/rest/v1/rates",
        body=json.dumps(payload).encode("utf-8"),
        headers={
            **supabase_headers(),
            "Prefer": "return=minimal",
        },
    )

    if status not in (200, 201, 204):
        details = body_resp.decode("utf-8", errors="ignore")
        return jsonify({"ok": False, "message": f"Supabase error ({status}): {details}"}), 502

    return jsonify({"ok": True, "message": "Successfully Updated"})


@app.route("/api/upload-image", methods=["POST"])
def upload_image():
    """Upload a collection image to Supabase Storage (admin auth required)."""
    auth_error = require_auth()
    if auth_error:
        return auth_error

    file = request.files.get("collectionFile")
    title = request.form.get("title", "").strip()
    tag = request.form.get("tag", "").strip()

    if not file or not title or not tag:
        return jsonify({"ok": False, "message": "Missing upload data"}), 400

    original_name = sanitize_filename(file.filename or "upload.bin")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    ext = os.path.splitext(original_name)[1].lower() or ".bin"
    stored_name = f"{timestamp}-{hashlib.sha1(original_name.encode('utf-8')).hexdigest()[:10]}{ext}"
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

    # Upload file to Supabase Storage
    object_path = f"collections/{stored_name}"
    file_data = file.read()

    status, body_resp = supabase_request(
        "POST",
        f"/storage/v1/object/{quote(supabase_bucket())}/{quote(object_path)}",
        body=file_data,
        headers={
            **supabase_headers(content_type="application/octet-stream"),
            "x-upsert": "false",
        },
    )

    if status not in (200, 201):
        details = body_resp.decode("utf-8", errors="ignore")
        return jsonify({"ok": False, "message": f"Storage upload failed ({status}): {details}"}), 502

    public_path = f"{supabase_url()}/storage/v1/object/public/{quote(supabase_bucket())}/{quote(object_path)}"

    # Save metadata to Supabase
    metadata_payload = {
        "title": title,
        "tag": tag,
        "file_path": public_path,
        "original_name": original_name,
        "created_at": created_at,
    }

    status, body_resp = supabase_request(
        "POST",
        "/rest/v1/uploads",
        body=json.dumps(metadata_payload).encode("utf-8"),
        headers={
            **supabase_headers(),
            "Prefer": "return=minimal",
        },
    )

    if status not in (200, 201, 204):
        details = body_resp.decode("utf-8", errors="ignore")
        return jsonify({"ok": False, "message": f"Metadata save failed ({status}): {details}"}), 502

    return jsonify({
        "ok": True,
        "message": "Successfully Updated",
        "item": {
            "title": title,
            "tag": tag,
            "filePath": public_path,
        },
    })


# ---------------------------------------------------------------------------
# Health check (useful for debugging on Vercel)
# ---------------------------------------------------------------------------

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "ok": True,
        "supabase_configured": bool(supabase_url() and supabase_service_key()),
        "admin_configured": bool(admin_passphrase() and session_secret()),
    })
