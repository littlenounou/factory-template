"""Chart renderers that turn a reading series into every supported

image format.
圖表呈現器，將讀數序列轉成每一種支援的圖片格式。

Every renderer derives its time axis from the union of timestamps across all
stations, so series with gaps still line up.

每個呈現器都以所有測站時間戳記的聯集作為時間軸，使有缺漏的序列仍能對齊。
"""

import json
