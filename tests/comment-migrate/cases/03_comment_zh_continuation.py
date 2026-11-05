def summarize(readings):
    if isinstance(readings, list):
        # The message names the method family "Fetch" (FetchHourly/FetchDaily/
        # FetchWeekly) so a caller knows which call returns several series; the
        # word "Fetch" must stay verbatim.
        #
        # 訊息點名方法家族 "Fetch"（
        # FetchHourly／FetchDaily／FetchWeekly）；
        # 使呼叫端知道哪個呼叫會回傳多組序列，"Fetch" 一詞必須逐字保留。
        raise SeriesError("use Fetch instead")
    return readings
