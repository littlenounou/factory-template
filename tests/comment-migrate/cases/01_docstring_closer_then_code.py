def test_first():
    """AC1: a value with only a bare CR must still be quoted, so a reader cannot
    treat the lone CR as a record break.

    AC1：只含單獨 CR 的值仍須加上引號，避免讀取器把單獨的 CR 當成記錄斷點。
    """
    result = render([{"note": "before\rafter", "plain": "plain"}])

    assert '"before\rafter"' in result
    # Counter-example: a plain value with no special characters stays unquoted.
    # 反例：沒有特殊字元的普通值維持不加引號。
    assert '"plain"' not in result
    assert ",plain\r\n" in result


def test_second():
    """AC2: a missing value renders as an explicit empty quoted field, never as
    an omitted column.

    AC2：缺漏的值呈現為明確的空引號欄位，絕不省略該欄。
    """
    assert render([{"a": None}]) == 'a\r\n""\r\n'
