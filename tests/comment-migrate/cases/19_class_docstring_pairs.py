class PollingReader:
    """Reader that polls a station once a minute (wraps `socket.socket`).

    每分鐘輪詢一次測站的讀取器（包裝 `socket.socket`）。

    Deliberately keeps no buffer between polls: a stale reading shown as fresh
    is worse than a missing one.

    刻意不在兩次輪詢之間保留緩衝：把過期讀數當成最新的顯示，比缺少讀數更糟。
    """

    def __init__(self, sock):
        self._sock = sock
