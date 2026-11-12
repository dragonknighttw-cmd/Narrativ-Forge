from pathlib import Path


def test_cloudflare_edge_cors_allows_frontend_idempotency_requests():
    repo_root = Path(__file__).resolve().parents[4]
    source = (repo_root / "infra/cloudflare-worker/src/index.ts").read_text(encoding="utf-8")

    assert 'requestOrigin !== allowedOrigin' in source
    assert '"Access-Control-Allow-Origin": allowedOrigin' in source
    assert '"Access-Control-Allow-Headers": "Content-Type,Authorization,Idempotency-Key"' in source
    assert 'request.headers.get("Origin") ?? ""' in source
