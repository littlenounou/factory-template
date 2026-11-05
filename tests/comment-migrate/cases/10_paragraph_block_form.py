"""Station reading pipeline: fetching, decoding, unit checks and
alerting.

Every step here is a pure function, so the hourly job and the live dashboard can
call the exact same code and never disagree.

測站讀數流程：擷取、解碼、單位檢查與
警報。

這裡的每個步驟都是純函式，因此每小時排程與即時儀表板能呼叫完全相同的程式碼，
彼此永遠不會不一致。
"""

import json
