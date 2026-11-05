"""The polling and streaming station readers.

Two readers are exposed: one polls every minute, one keeps a stream open. Both
hand every reading to the same decoder, so their output can never differ.

輪詢與串流兩種測站讀取器。

對外提供兩種讀取器：一種每分鐘輪詢，一種維持串流連線。兩者都把每筆讀數交給
同一個解碼器，因此輸出永遠不會不同。
"""

import socket
