from typing import Optional, Dict


def parse_bearer_token(authorization_header: Optional[str]) -> Optional[str]:
    if not authorization_header:
        return None
    value = authorization_header.strip()
    if not value:
        return None
    if value.lower().startswith("bearer "):
        token = value[7:].strip()
        return token or None
    return None


def resolve_user_id(token: Optional[str], tokens_map: Dict[str, str]) -> Optional[str]:
    if not token:
        return None
    return tokens_map.get(token)
