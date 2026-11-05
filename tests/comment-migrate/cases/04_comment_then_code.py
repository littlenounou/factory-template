"""Transport-agnostic pure core: envelope building and response decoding.

與傳輸層無關的純函式核心：封包建立與回應解碼。
"""

# The schema renderer shares one Markdown escape with `converters` so the two cannot
# drift apart. The import direction is acyclic.
#
# 結構呈現器與 `converters` 共用同一個 Markdown 跳脫函式，使兩者不會產生分歧。
# 匯入方向無循環。
from .converters import _markdown_escape

# The signed 64-bit integer range, mirroring a C# `long`.
#
# 有號 64 位元整數範圍，比照 C# 的 `long`。
INT64_MIN = -(2**63)
INT64_MAX = 2**63 - 1


def build_envelope(request):
    """Builds the envelope the endpoint expects: exactly these two keys.

    建立端點所預期的封包：僅此兩個鍵。
    """
    return {"Sql": request.sql, "Timeout": request.timeout}
