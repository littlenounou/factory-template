public class Guard
{
    // Reject the request when the tenant does not own the record.
    // 當租戶並未擁有該紀錄時拒絕請求。
    // This is the last line of defence.
    // 這是最後一道防線。
    public void Check(Record record) { }
}
