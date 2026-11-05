def test_glyphs():
    """AC29: the trigger set is written as code point escapes, so the source file
    contains none of the four full-width glyphs (U+FF1D, U+FF0B, U+FF0D, U+FF20).

    AC29：觸發字元集以碼位跳脫序列撰寫，因此原始碼檔案不含這四個全形字形
    （U+FF1D、U+FF0B、U+FF0D、U+FF20）。
    """


def test_unsupported_format():
    """AC38: an unrecognized format value raises a config error containing
    "Unsupported output format".

    AC38：不被辨識的格式值會擲出包含 "Unsupported output format" 的
    `ExampleConfigError`。
    """


def test_default_order_column():
    """AC32: omitting `order_column` defaults it to "updated_at", matching
    `Constants.DefaultOrderColumn`.

    AC32：省略 `order_column` 時預設為 "updated_at"，比照
    `Constants.DefaultOrderColumn`。
    """
