import secrets

from fastapi import Header, HTTPException, Request


def require_token(request: Request, authorization: str = Header(default="")):
    expected = request.app.state.settings.api_token
    if not expected:
        return
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not secrets.compare_digest(token.strip(), expected):
        raise HTTPException(status_code=401, detail="Token de acceso inválido o faltante.")
