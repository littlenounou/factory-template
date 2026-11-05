def test_reading_rounds_half_up():
    """A reading of 21.45 degrees is shown as 21.5, because the display rounds
    half up rather than to even.

    21.45 度的讀數顯示為 21.5，因為顯示採四捨五入而非銀行家捨入。
    """
    shown = display(21.45)

    assert shown == "21.5"
    # Counter-example: a value that needs no rounding stays as it is.
    # 反例：不需捨入的值維持原樣。
    assert display(21.5) == "21.5"
    assert display(-3.0) == "-3.0"


def test_missing_reading_is_a_dash():
    """A station that sent nothing shows a dash, never zero, so an outage cannot
    look like a cold morning.

    未回傳資料的測站顯示破折號而非零，避免斷線看起來像寒冷的早晨。
    """
    assert display(None) == "-"
