"""Runtime hardening for twikit User payloads (missing entities.urls etc.)."""

from __future__ import annotations

_applied = False


def apply_user_urls_patch() -> None:
    """Ensure legacy.entities.description/url.urls exist before User.__init__ parses them."""
    global _applied
    if _applied:
        return
    try:
        from twikit.user import User
    except ImportError:
        return

    if getattr(User, "_follow_tracker_urls_patched", False):
        _applied = True
        return

    _orig = User.__init__

    def __init__(self, client, data):  # type: ignore[no-untyped-def]
        if isinstance(data, dict):
            data = dict(data)
            legacy = data.get("legacy")
            if isinstance(legacy, dict):
                legacy = dict(legacy)
                entities = dict(legacy.get("entities") or {})
                description = dict(entities.get("description") or {})
                description.setdefault("urls", [])
                entities["description"] = description
                url_block = dict(entities.get("url") or {})
                url_block.setdefault("urls", [])
                entities["url"] = url_block
                legacy["entities"] = entities
                legacy.setdefault("withheld_in_countries", [])
                legacy.setdefault("pinned_tweet_ids_str", [])
                legacy.setdefault("location", "")
                legacy.setdefault("description", "")
                data["legacy"] = legacy
        _orig(self, client, data)

    User.__init__ = __init__  # type: ignore[method-assign]
    User._follow_tracker_urls_patched = True  # type: ignore[attr-defined]
    _applied = True
