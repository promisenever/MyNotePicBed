import sqlite3
import click
import os
from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    """获取数据库连接，如果不存在则创建新连接"""
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    """关闭数据库连接"""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """初始化数据库表结构"""
    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode('utf8'))
    print('初始化数据库成功')

@click.command('init-db')
@with_appcontext
def init_db_command():
    """清除现有数据并创建新表"""
    init_db()
    click.echo('数据库初始化成功')

def init_app(app):
    """在应用中注册数据库函数"""
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def get_all_pics(sort_by='created', order='DESC', page=1, per_page=20):
    """获取分页的图片记录
    
    Args:
        sort_by: 排序字段 ('id', 'filename', 'created')
        order: 排序方式 ('ASC', 'DESC')
        page: 页码，从1开始
        per_page: 每页记录数
    Returns:
        tuple: (记录列表, 总记录数, 总页数)
    """
    allowed_fields = ['id', 'filename', 'created']
    allowed_orders = ['ASC', 'DESC']
    
    sort_by = sort_by if sort_by in allowed_fields else 'created'
    order = order if order in allowed_orders else 'DESC'
    
    db = get_db()
    # 获取总记录数
    total = db.execute('SELECT COUNT(*) FROM pics').fetchone()[0]
    total_pages = (total + per_page - 1) // per_page
    
    # 计算偏移量
    offset = (page - 1) * per_page
    
    # 获取分页数据
    records = db.execute(
        f'SELECT id, filename, created FROM pics ORDER BY {sort_by} {order} LIMIT ? OFFSET ?',
        (per_page, offset)
    ).fetchall()
    
    return records, total, total_pages

def check_files_and_records():
    """检查文件和数据库记录的匹配情况"""
    db = get_db()
    result = {
        'orphaned_files': [],
        'missing_files': [],
        'status': 'ok'
    }
    
    # 定义允许的图片扩展名
    ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    
    def is_image_file(filename):
        """检查文件是否为图片"""
        return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)
    
    try:
        # 使用索引加速查询
        records = db.execute('SELECT id, filename FROM pics').fetchall()
        db_files = {record['filename'] for record in records}
        
        # 检查 pics 目录
        pics_folder = os.path.join(os.getcwd(), 'pics')
        pics_files = set()
        if os.path.exists(pics_folder):
            pics_files = {
                f for f in os.listdir(pics_folder)
                if os.path.isfile(os.path.join(pics_folder, f)) and is_image_file(f)
            }
            
        # 检查 images 目录下的所有子目录
        images_root = os.path.join(os.getcwd(), 'images')
        images_files = set()
        if os.path.exists(images_root):
            for root, _, files in os.walk(images_root):
                for file in files:
                    if is_image_file(file):
                        images_files.add(file)
        
        # 合并所有实际文件
        actual_files = pics_files | images_files
        
        # 检查不匹配情况
        result['orphaned_files'] = list(actual_files - db_files)
        result['missing_files'] = [
            {'id': r['id'], 'filename': r['filename']}
            for r in records
            if r['filename'] not in actual_files
        ]
        
        result['status'] = 'mismatch' if result['orphaned_files'] or result['missing_files'] else 'ok'
        
    except Exception as e:
        print(f"文件检查出错: {str(e)}")
        result['status'] = 'error'
    
    return result

def clean_orphaned_records(record_ids):
    """删除没有对应文件的数据库记录
    
    Args:
        record_ids: 要删除的记录ID列表
    """
    if not record_ids:
        return
        
    db = get_db()
    placeholders = ','.join('?' * len(record_ids))
    db.execute(f'DELETE FROM pics WHERE id IN ({placeholders})', record_ids)
    db.commit()

def clean_orphaned_files(filenames):
    """删除没有数据库记录的文件
    
    Args:
        filenames: 要删除的文件名列表
    """
    if not filenames:
        return
        
    # 检查 pics 目录
    pics_folder = os.path.join(current_app.config['UPLOAD_FOLDER'])
    
    # 检查 images 目录
    images_root = os.path.join(os.getcwd(), 'images')
    
    for filename in filenames:
        # 检查 pics 目录
        file_path = os.path.join(pics_folder, filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            continue
            
        # 检查 images 目录下的所有子目录
        for root, _, files in os.walk(images_root):
            if filename in files:
                file_path = os.path.join(root, filename)
                os.remove(file_path)
                break

def restore_orphaned_files(filenames):
    """将孤立文件恢复到数据库中
    
    Args:
        filenames: 要恢复的文件名列表
    Returns:
        dict: {
            'restored': [成功恢复的文件列表],
            'failed': [恢复失败的文件列表]
        }
    """
    if not filenames:
        return {'restored': [], 'failed': []}
        
    db = get_db()
    restored = []
    failed = []
    
    # 检查 pics 目录和 images 目录
    pics_folder = os.path.join(current_app.config['UPLOAD_FOLDER'])
    images_root = os.path.join(os.getcwd(), 'images')
    
    for filename in filenames:
        try:
            # 首先检查 pics 目录
            file_path = os.path.join(pics_folder, filename)
            if os.path.exists(file_path):
                db.execute('INSERT INTO pics (filename) VALUES (?)', (filename,))
                restored.append(filename)
                continue
                
            # 然后检查 images 目录下的所有子目录
            found = False
            for root, _, files in os.walk(images_root):
                if filename in files:
                    db.execute('INSERT INTO pics (filename) VALUES (?)', (filename,))
                    restored.append(filename)
                    found = True
                    break
                    
            if not found:
                failed.append(filename)
                
        except Exception as e:
            print(f"恢复文件 {filename} 失败: {str(e)}")
            failed.append(filename)
    
    db.commit()
    return {'restored': restored, 'failed': failed}

def search_pics(query, sort_by='created', order='DESC', page=1, per_page=20):
    """搜索图片记录，支持分页
    
    Args:
        query: 搜索关键词
        sort_by: 排序字段
        order: 排序方式
        page: 页码
        per_page: 每页记录数
    """
    allowed_fields = ['id', 'filename', 'created']
    allowed_orders = ['ASC', 'DESC']
    
    sort_by = sort_by if sort_by in allowed_fields else 'created'
    order = order if order in allowed_orders else 'DESC'
    
    db = get_db()
    # 获取搜索结果总数
    total = db.execute(
        'SELECT COUNT(*) FROM pics WHERE filename LIKE ? OR date(created) = date(?)',
        (f'%{query}%', query)
    ).fetchone()[0]
    
    total_pages = (total + per_page - 1) // per_page
    offset = (page - 1) * per_page
    
    # 获取分页搜索结果
    records = db.execute(
        f'''SELECT id, filename, created 
           FROM pics 
           WHERE filename LIKE ? OR date(created) = date(?)
           ORDER BY {sort_by} {order}
           LIMIT ? OFFSET ?''',
        (f'%{query}%', query, per_page, offset)
    ).fetchall()
    
    return records, total, total_pages