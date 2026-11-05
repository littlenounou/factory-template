"""Station reading conversions: units, rounding and range checks.

測站讀數轉換：單位、捨入與範圍檢查。
"""

# The display layer shares one rounding helper with `units` so the two cannot
# drift apart. The import direction is one-way.
#
# 顯示層與 `units` 共用同一個捨入輔助函式，使兩者不會產生分歧。
# 匯入方向為單向。
from .units import round_half_up

# The plausible temperature range for a ground station, in degrees Celsius.
#
# 地面測站合理的溫度範圍，單位為攝氏度。
MIN_CELSIUS = -90
MAX_CELSIUS = 60


def to_celsius(fahrenheit):
    """Converts one Fahrenheit reading to Celsius, unrounded.

    將一筆華氏讀數轉為攝氏，不做捨入。
    """
    return (fahrenheit - 32) * 5 / 9
