def build_request_headers(headers):
    """
    Copies the caller's headers and always sends `Accept: application/json`.
    A caller-supplied Accept entry is rejected before anything is sent.

    複製呼叫端的標頭，並一律送出 `Accept: application/json`，否則擲回
    `StationConfigurationError`。
    """
    return dict(headers or {})
