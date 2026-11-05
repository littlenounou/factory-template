def test_unit_symbols():
    """The label set is written as code point escapes, so the source file contains
    neither of the two unit glyphs (U+00B0, U+2103).

    標籤集合以碼位跳脫序列撰寫，因此原始碼檔案不含這兩個單位字形
    （U+00B0、U+2103）。
    """


def test_offline_station():
    """A station that misses three polls raises an error containing
    "station offline".

    連續三次輪詢未回應的測站會擲出包含 "station offline" 的
    `StationOfflineError`。
    """


def test_default_retry_limit():
    """Omitting `retries` uses the default limit, matching
    `Defaults.RetryLimit`.

    省略 `retries` 時使用預設上限，比照
    `Defaults.RetryLimit`。
    """
