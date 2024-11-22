from flask import Flask, request, jsonify, render_template
import sqlite3
import secrets
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import os
from threading import Thread
import schedule
import time
import string
import random

app = Flask(__name__)

# 获取当前文件所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 数据库文件路径
DATABASE_PATH = os.path.join(CURRENT_DIR, 'messages.db')

# 从环境变量获取服务器地址，默认为本地地址
SERVER_URL = os.getenv('SERVER_URL', 'http://127.0.0.1:5000')

# 配置项
class Config:
    _use_zws = os.getenv('USE_ZWS', 'false').lower() == 'true'  # 默认为 false

    @classmethod
    def use_zws(cls):
        return cls._use_zws

    @classmethod
    def set_use_zws(cls, value):
        cls._use_zws = bool(value)

    # 普通路径前缀
    NORMAL_PATHS = {
        'VIEW': '_',  # 改为下划线
        'API': '-'    # 改为短横线
    }

class ZWSPaths:
    """零宽字符路径配置"""
    VIEW = '\u200b\u200c'     # 直接作为hash的前缀
    API  = '\u200d\u2060'     # 直接作为hash的前缀

def get_db():
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db

def get_next_counter():
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute('SELECT MAX(id) FROM Hash')
        result = cursor.fetchone()
        return result[0] + 1 if result[0] else 0
    except sqlite3.Error:
        return 0

def generate_hash(length=6):
    """生成短哈希值
    length: 生成的哈希长度，默认6位
    """
    chars = string.ascii_letters + string.digits  # a-z A-Z 0-9
    while True:
        hash = ''.join(random.choices(chars, k=length))
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('SELECT hash FROM Hash WHERE hash = ?', (hash,))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO Hash (hash) VALUES (?)', (hash,))
                db.commit()
                return hash
        except sqlite3.Error as e:
            print(f"数据库错误: {e}")
            db.rollback()
            raise

def generate_zero_width_chars(length=4):
    """使用真正的零宽字符生成哈希"""
    # 只使用完全不可见的零宽字符
    zero_width_chars = [
        '\u200b',  # 零宽空格 ZERO WIDTH SPACE
        '\u200c',  # 零宽非连接符 ZERO WIDTH NON-JOINER
        '\u200d',  # 零宽连接符 ZERO WIDTH JOINER
        '\u2060',  # 词组连接符 WORD JOINER
        '\ufeff',  # 零宽非断空格 ZERO WIDTH NO-BREAK SPACE
    ]
    
    counter = get_next_counter()
    
    # 基础哈希
    base_hash = ''.join(random.choices(zero_width_chars, k=length))
    # 添加计数器作为后缀（也使用零宽字符）
    counter_hash = ''.join(random.choices(zero_width_chars, k=len(str(counter))))
    
    return base_hash + counter_hash

def create_url(base_url, path_type, hash):
    """
    创建URL，根据配置决定是否使用零宽字符
    """
    base_url = base_url.rstrip('/')
    if Config.use_zws():
        # 使用零宽字符
        prefix = getattr(ZWSPaths, path_type)
        return f"{base_url}/{prefix}{hash}"
    else:
        # 使用短前缀
        prefix = Config.NORMAL_PATHS[path_type]
        return f"{base_url}/{prefix}{hash}"  # 移除额外的斜杠

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['POST'])
def create_message():
    try:
        content = request.json.get('content')
        password = request.json.get('password')
        destroy_type = request.json.get('destroyType')
        expire_minutes = request.json.get('expireMinutes', 5)
        
        # 内容验证
        if not content:
            return jsonify({'error': '消息内容不能为空'}), 400
        
        # 内容长度验证
        if len(content) > 512:
            return jsonify({'error': '消息内容不能超过512个字符'}), 400
            
        # 密码长度验证（可选）
        if password and len(password) > 32:
            return jsonify({'error': '密码长度不能超过32个字符'}), 400
        
        try:
            expire_minutes = int(expire_minutes)
            # 限制过期时间范围（可选）
            if expire_minutes < 1 or expire_minutes > 1440:  # 最长24小时
                return jsonify({'error': '过期时间必须在1-1440分钟之间'}), 400
        except:
            return jsonify({'error': '过期时间必须是数字'}), 400
        
        # 使用零宽字符生成哈希

        if Config.use_zws():
            hash = generate_zero_width_chars()
        else:
            hash = generate_hash()

        db = get_db()
        cursor = db.cursor()
        
        password_hash = generate_password_hash(password) if password else None
        destroy_at = datetime.datetime.now() + datetime.timedelta(minutes=expire_minutes)
        
        # destroy_type: 'burn' 为阅后即焚, 'expire' 为定时销毁
        is_burn = destroy_type == 'burn'
        
        cursor.execute('''
            INSERT INTO Msg (
                hash, content, type, destroyMinutes, 
                secret, destroyedAt, destroyType, status
            )
            VALUES (?, ?, 0, ?, ?, ?, ?, 1)
        ''', (hash, content, expire_minutes, password_hash, destroy_at, 1 if is_burn else 0))
        
        db.commit()
        
        # 生成使用零宽字符路径的链接
        message_url = create_url(SERVER_URL, 'VIEW', hash)
        
        return jsonify({
            'success': True,
            'message': '消息创建成功',
            'url': message_url
        })
    except Exception as e:
        print(f"创建消息错误: {e}")
        return jsonify({'error': '创建消息失败'}), 500

@app.route('/<path:hash_path>', methods=['GET', 'POST'])
def view_message(hash_path):
    """处理所有可能的哈希路径"""
    try:
        # 检查是否是零宽字符路径
        if hash_path.startswith(ZWSPaths.VIEW):
            hash = hash_path[len(ZWSPaths.VIEW):]
        # 检查是否是短前缀路径
        elif hash_path.startswith(Config.NORMAL_PATHS['VIEW']):
            hash = hash_path[len(Config.NORMAL_PATHS['VIEW']):]
        else:
            return render_template('view.html', error='消息不存在或已失效')
            
        db = get_db()
        cursor = db.cursor()
        
        # 查询未删除的消息
        cursor.execute('''
            SELECT 
                *
            FROM Msg 
            WHERE hash = ? 
                AND isDeleted = 0
                AND status = 1  -- 只查询有效消息
        ''', (hash,))
        
        msg = cursor.fetchone()
        if not msg:
            return render_template('view.html', error='消息不存在或已失效')
        
        # 判断阅后即焚
        if msg['destroyType'] == 1 and msg['viewCount'] > 0:
            # 标记消息为已删除
            cursor.execute('''
                UPDATE Msg 
                SET isDeleted = 1,
                    updatedAt = datetime('now')
                WHERE hash = ?
            ''', (hash,))
            db.commit()
            return render_template('view.html', error='消息已被销毁')
            
        # 判断时销毁
        if msg['destroyType'] == 0 and msg['destroyedAt']:
            current_time = datetime.datetime.now()
            destroy_time = datetime.datetime.strptime(
                msg['destroyedAt'].split('.')[0], 
                '%Y-%m-%d %H:%M:%S'
            )
            if current_time >= destroy_time:
                # 标记消息为已删除
                cursor.execute('''
                    UPDATE Msg 
                    SET isDeleted = 1,
                    updatedAt = datetime('now')
                    WHERE hash = ?
                ''', (hash,))
                db.commit()
                return render_template('view.html', error='消息已过期')
        
        # 处理密码保护
        if msg['secret']:
            if request.method == 'GET':
                remaining_attempts = 3 - msg['passwordAttempts']
                return render_template('view.html', 
                    hash=hash, 
                    need_password=True, 
                    remaining_attempts=remaining_attempts
                )
            
            password = request.form.get('password')
            if not password or not check_password_hash(msg['secret'], password):
                cursor.execute('''
                    UPDATE Msg 
                    SET passwordAttempts = passwordAttempts + 1 
                    WHERE hash = ?
                ''', (hash,))
                db.commit()
                
                cursor.execute('SELECT passwordAttempts FROM Msg WHERE hash = ?', (hash,))
                updated_msg = cursor.fetchone()
                
                if updated_msg['passwordAttempts'] >= 3:
                    cursor.execute('''
                        UPDATE Msg 
                        SET viewCount = 1,
                            isDeleted = 1,
                            updatedAt = datetime('now')
                        WHERE hash = ?
                    ''', (hash,))
                    db.commit()
                    return render_template('view.html', error='密码错误次数过多，消息已被销毁')
                
                remaining_attempts = 3 - updated_msg['passwordAttempts']
                return render_template('view.html', 
                    hash=hash, 
                    need_password=True, 
                    error=f'密码错误，还剩 {remaining_attempts} 次尝试机会',
                    remaining_attempts=remaining_attempts
                )
        
        # 果是阅后即焚，更查看次数
        if msg['destroyType'] == 1:
            cursor.execute('''
                UPDATE Msg 
                SET viewCount = viewCount + 1,
                    updatedAt = datetime('now')
                WHERE hash = ?
            ''', (hash,))
            db.commit()
        
        return render_template('view.html', 
            content=msg['content'],
            destroy_type='burn' if msg['destroyType'] == 1 else 'expire',
            expire_time=msg['destroyedAt'],
            expire_minutes=msg['destroyMinutes']
        )
    except Exception as e:
        print(f"查看消息错误: {e}")
        return render_template('view.html', error='系统错误')

def cleanup_messages():
    try:
        db = get_db()
        cursor = db.cursor()
        
        # 标记已失效的消息为已删除
        cursor.execute('''
            UPDATE Msg 
            SET isDeleted = 1,
                status = 0,  -- 标记为无效
                updatedAt = datetime('now')
            WHERE isDeleted = 0 
            AND (
                (destroyType = 1 AND viewCount > 0) OR
                (destroyType = 0 AND datetime(destroyedAt) <= datetime('now'))
            )
        ''')
        
        # 物理删除30天前的已删除消息
        cursor.execute('''
            DELETE FROM Msg 
            WHERE isDeleted = 1 
            AND datetime(updatedAt) <= datetime('now', '-30 days')
        ''')
        
        db.commit()
        print(f"清理任务完成: {datetime.datetime.now()}")
        
    except Exception as e:
        print(f"清理任务错误: {e}")
    finally:
        if db:
            db.close()

def run_schedule():
    while True:
        schedule.run_pending()
        time.sleep(60)

# 添加一个管理接口（可选）
@app.route('/admin/config', methods=['POST'])
def update_config():
    if request.json.get('use_zws') is not None:
        Config.set_use_zws(request.json['use_zws'])
    return jsonify({
        'use_zws': Config.use_zws()
    })

if __name__ == '__main__':
    # 设置定时任务
    schedule.every(1).hours.do(cleanup_messages)
    
    # 在后台线程启动定时任务
    cleanup_thread = Thread(target=run_schedule, daemon=True)
    cleanup_thread.start()
    
    # 启动时执行一次清理
    cleanup_messages()
    
    # 启动Flask应用
    app.run(debug=True) 