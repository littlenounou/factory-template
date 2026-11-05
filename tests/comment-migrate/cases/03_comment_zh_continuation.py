def decode(parsed):
    if isinstance(parsed, list):
        # D6 locks the literal substring "FetchMany" (from the method-name family
        # FetchManyAsList/FetchManyAsTable/FetchManyAsSheet); the message must
        # keep "FetchMany" verbatim.
        #
        # D6 鎖定字面子字串 "FetchMany"（源自方法名稱家族
        # FetchManyAsList／FetchManyAsTable／FetchManyAsSheet）；
        # 訊息中必須逐字保留 "FetchMany"。
        raise DecodeError("use FetchMany instead")
    return parsed
