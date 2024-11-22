from datetime import datetime
from app import get_db

def cleanup_messages():
    try:
        db = get_db()
        cursor = db.cursor()
        current_time = datetime.now()
        
        # 标记已失效的消息为已删除
        cursor.execute('''
            UPDATE Msg 
            SET isDeleted = 1,
                updatedAt = datetime('now')
            WHERE isDeleted = 0 
            AND status = 0
        ''')
        
        # 物理删除30天前的已删除消息
        cursor.execute('''
            DELETE FROM Msg 
            WHERE isDeleted = 1 
            AND datetime(updatedAt) <= datetime('now', '-30 days')
        ''')
        
        db.commit()
        print(f"清理任务完成: {datetime.now()}")
        
    except Exception as e:
        print(f"清理任务错误: {e}")
    finally:
        if db:
            db.close() 