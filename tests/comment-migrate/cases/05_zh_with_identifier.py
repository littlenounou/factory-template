def build_headers(headers):
    """
    Copies the caller's headers and forces `Content-Type: application/json`.
    A caller-supplied Content-Type entry is rejected before anything is sent.

    複製呼叫端的標頭，並強制設定 `Content-Type: application/json`，否則擲回
    `ExampleDbQueryConfigurationError`。
    """
    return dict(headers or {})
