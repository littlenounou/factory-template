"""Transport-agnostic pure core: envelope building, response decoding, identifier

validation, and query building.

Every function here takes no I/O, so both the async and the sync client can call
the exact same functions and never drift from each other.

與傳輸層無關的純函式核心：封包建立、回應解碼、識別字驗證，以及查詢的
建置。

本模組的每個函式都不涉及 I/O，因此非同步與同步用戶端能呼叫完全相同的函式，
彼此永遠不會產生分歧。
"""

import json
