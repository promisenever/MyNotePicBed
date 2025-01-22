# coding=utf-8
import os
from flask import Flask, flash, request, redirect, url_for, render_template, current_app, jsonify
from werkzeug.utils import secure_filename
from flask import send_from_directory
import random, time
import db
import getConfig as gcf
import traceback
import shutil
from datetime import datetime
import subprocess
import sys
import webbrowser

cf = gcf.get_config()

allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
upload_folder = os.path.join(os.getcwd(), 'pics')
trash_folder = os.path.join(os.getcwd(), 'trash')  # 添加回收站文件夹
print(upload_folder)
app = Flask(__name__, instance_relative_config=True)

IMAGES_ROOT = os.path.join(os.getcwd(), 'images')

def init_app_config(app, config):
    """初始化应用配置"""
    app.config.update(
        UPLOAD_FOLDER=upload_folder,
        TRASH_FOLDER=trash_folder,  # 添加回收站配置
        running_domain=config['running_domain'],
        running_port=config['port'],
        MAX_CONTENT_LENGTH=1024 * 1024 * int(config['max_length']),
        SECRET_KEY='dgvbv43@$ewedc',
        DATABASE=os.path.join(app.instance_path, 'my-easy-pic-bed.sqlite'),
    )

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def move_to_trash(file_path):
    """将文件移动到回收站文件夹"""
    try:
        # 确保回收站文件夹存在
        os.makedirs(trash_folder, exist_ok=True)
        # 移动文件到回收站
        shutil.move(file_path, os.path.join(trash_folder, os.path.basename(file_path)))
        return True
    except Exception as e:
        print(f"移动到回收站失败: {str(e)}")
        return False

@app.route('/local_pic_host', methods=['POST','GET'])
def local_picuse_host():
    if request.method != 'POST':
        return jsonify({'file_data': ''})
        
    if 'file' not in request.files:
        flash('你没有上传文件！')
        return redirect(request.url)
        
    file = request.files['file']
    if file.filename == '':
        flash('你没有选择文件！')
        return redirect(request.url)
        
    if not file or not allowed_file(file.filename):
        flash('不被服务器支持的文件！')
        return redirect(url_for('upload_file'))
        
    try:
        filename = str(file.filename)
        file.save(os.path.join(upload_folder, filename))
        
        # 修复数据库操作
        database = db.get_db()
        database.execute(
            'INSERT INTO pics (filename) VALUES (?)',
            (filename,)
        )
        database.commit()  # 确保提交事务
        
        file_link = construct_file_link(filename)
        flash('http://' + file_link)
        return jsonify({'file_data': 'http://' + file_link})
        
    except Exception as e:
        flash('出现错误！')
        print(e.args)
        return redirect(request.url)

def construct_file_link(filename):
    """构造文件访问链接"""
    domain = app.config['running_domain']
    port = app.config['running_port']
    file_url = url_for('uploaded_file', filename=filename)
    
    return f"{domain}:{port}{file_url}" if port != 80 else f"{domain}{file_url}"

@app.route('/', methods=['POST', 'GET'] )
def upload_file():
    if request.method == 'POST':
        # 检查post请求中是否有文件
        if 'file' not in request.files:
            flash('你没有上传文件！')
            return redirect(request.url)
        file = request.files['file']
        print(file)
        if file.filename == '':
            flash('你没有选择文件！')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = str(int(time.time())) + str(random.randint(1, 99999)) + secure_filename(str(random.randint(1, 7887)) + file.filename)
            try:
                file.save(os.path.join(upload_folder, filename))
                database = db.get_db()
                database.execute(
                    'INSERT INTO pics (filename)'
                    ' VALUES (?)',
                    (filename,)
                )
                database.commit()
                url = url_for('uploaded_file', filename=filename)
                # 构造完整的URL
                full_url = 'http://' + app.config['running_domain']
                if app.config['running_port'] != 80:
                    full_url += ':' + str(app.config['running_port'])
                full_url += url
                flash(full_url)
            except Exception as e:
                flash('出现错误！')
                print(e.args)

            return redirect(url_for('upload_file'))
        else:
            flash('不被服务器支持的文件！')
            return redirect(url_for('upload_file'))
    database = db.get_db()
    pcnum = database.execute("SELECT Count(*) FROM pics").fetchone()[0]
    print(pcnum)

    return render_template('bs_index.html', pic_num=pcnum)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # 首先在 pics 目录查找
    pics_folder = os.path.join(os.getcwd(), 'pics')
    if os.path.exists(os.path.join(pics_folder, filename)):
        return send_from_directory(pics_folder, filename)
    
    # 如果在 pics 目录找不到，在 images 目录的所有子目录中查找
    images_root = os.path.join(os.getcwd(), 'images')
    if os.path.exists(images_root):
        for root, _, files in os.walk(images_root):
            if filename in files:
                # 使用文件所在的实际目录
                return send_from_directory(root, filename)
    
    # 如果都找不到，返回 404
    return '', 404


@app.route('/manage', methods=['GET', 'POST'])
def manage_pics():
    try:
        if request.method == 'POST':
            # 检查post请求中是否有文件
            if 'file' not in request.files:
                flash('你没有上传文件！')
                return redirect(request.url)
            files = request.files.getlist('file')
            if not files or files[0].filename == '':
                flash('你没有选择文件！')
                return redirect(request.url)
            
            uploaded_urls = []
            for file in files:
                if file and allowed_file(file.filename):
                    filename = str(int(time.time())) + str(random.randint(1, 99999)) + secure_filename(str(random.randint(1, 7887)) + file.filename)
                    try:
                        file.save(os.path.join(upload_folder, filename))
                        database = db.get_db()
                        database.execute(
                            'INSERT INTO pics (filename)'
                            ' VALUES (?)',
                            (filename,)
                        )
                        database.commit()
                        url = url_for('uploaded_file', filename=filename)
                        full_url = 'http://' + app.config['running_domain']
                        if app.config['running_port'] != 80:
                            full_url += ':' + str(app.config['running_port'])
                        full_url += url
                        uploaded_urls.append(full_url)
                    except Exception as e:
                        flash('出现错误！')
                        print(e.args)
                        continue
            
            if uploaded_urls:
                for url in uploaded_urls:
                    flash(url)
                return redirect(url_for('manage_pics'))
            else:
                flash('没有成功上传任何文件！')
                return redirect(request.url)
        
        sort_by = request.args.get('sort', 'created')
        order = request.args.get('order', 'DESC')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        pics, total, total_pages = db.get_all_pics(sort_by, order, page, per_page)
        
        domain = 'http://' + app.config['running_domain']
        if app.config['running_port'] != 80:
            domain += ':' + str(app.config['running_port'])
        
        next_order = 'ASC' if order == 'DESC' else 'DESC'
        
        # 计算分页范围
        start_page = max(1, page - 2)
        end_page = min(total_pages + 1, page + 3)
        page_range = range(start_page, end_page)
        
        return render_template('manage_pics.html', 
                             pics=pics,
                             domain=domain,
                             current_sort=sort_by,
                             current_order=order,
                             next_order=next_order,
                             current_page=page,
                             total_pages=total_pages,
                             total_items=total,
                             page_range=page_range)  # 添加页码范围
    except Exception as e:
        print('Error in manage_pics:', str(e))
        print(traceback.format_exc())
        raise


def find_file_path(filename):
    """查找文件的实际路径，包括归档目录"""
    # 首先检查上传目录
    file_path = os.path.join(upload_folder, filename)
    if os.path.exists(file_path):
        return file_path
        
    # 如果在上传目录中找不到，搜索归档目录（images目录）
    images_root = os.path.join(os.getcwd(), 'images')
    for root, _, files in os.walk(images_root):
        if filename in files:
            return os.path.join(root, filename)
            
    return None

@app.route('/delete_pic', methods=['POST'])
def delete_pic():
    try:
        filename = request.form.get('filename')
        pic_id = request.form.get('id')
        
        if not filename or not pic_id:
            return jsonify({'success': False, 'message': '参数不完整'})
            
        file_path = find_file_path(filename)
        if file_path and os.path.exists(file_path):
            if not move_to_trash(file_path):
                return jsonify({'success': False, 'message': '移动到回收站失败'})
            
        # 删除数据库记录
        database = db.get_db()
        database.execute('DELETE FROM pics WHERE id = ?', (pic_id,))
        database.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/delete_pics', methods=['POST'])
def delete_pics():
    try:
        data = request.get_json()
        pics = data.get('pics', [])
        deleted_ids = []
        failed_deletes = []
        
        if not pics:
            return jsonify({'success': False, 'message': '没有选择要删除的图片'})
        
        database = db.get_db()
        
        for pic in pics:
            filename = pic.get('filename')
            pic_id = pic.get('id')
            
            if not filename or not pic_id:
                continue
                
            file_path = find_file_path(filename)
            if file_path and os.path.exists(file_path):
                try:
                    if move_to_trash(file_path):
                        database.execute('DELETE FROM pics WHERE id = ?', (pic_id,))
                        deleted_ids.append(pic_id)
                    else:
                        failed_deletes.append({
                            'filename': filename,
                            'error': '移动到回收站失败'
                        })
                except Exception as e:
                    failed_deletes.append({
                        'filename': filename,
                        'error': str(e)
                    })
            else:
                # 如果找不到文件但数据库中有记录，也删除数据库记录
                database.execute('DELETE FROM pics WHERE id = ?', (pic_id,))
                deleted_ids.append(pic_id)
        
        database.commit()
        
        # 构造返回消息
        message = f'成功删除 {len(deleted_ids)} 张图片'
        if failed_deletes:
            message += f'\n{len(failed_deletes)} 张图片删除失败'
        
        return jsonify({
            'success': True,
            'deleted_ids': deleted_ids,
            'failed_deletes': failed_deletes,
            'message': message
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/check_files')
def check_files():
    result = db.check_files_and_records()
    return jsonify(result)

@app.route('/clean_files', methods=['POST'])
def clean_files():
    try:
        data = request.get_json()
        if data.get('clean_records'):
            record_ids = [r['id'] for r in data['missing_files']]
            db.clean_orphaned_records(record_ids)
        
        if data.get('clean_files'):
            db.clean_orphaned_files(data['orphaned_files'])
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/restore_files', methods=['POST'])
def restore_files():
    try:
        data = request.get_json()
        filenames = data.get('filenames', [])
        
        if not filenames:
            return jsonify({'success': False, 'message': '没有选择要恢复的文件'})
        
        result = db.restore_orphaned_files(filenames)
        
        return jsonify({
            'success': True,
            'restored': result['restored'],
            'failed': result['failed']
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/search_pics')
def search_pics():
    try:
        query = request.args.get('query', '').strip()
        sort = request.args.get('sort', 'created')
        order = request.args.get('order', 'DESC')
        page = int(request.args.get('page', 1))
        per_page = 10

        database = db.get_db()
        
        # 构建基础查询
        base_query = '''
            SELECT id, filename, created 
            FROM pics 
        '''
        
        params = []
        if query:
            # 修改搜索条件，使用 LIKE 进行模糊匹配
            base_query += '''
                WHERE (
                    filename LIKE ? 
                    OR created LIKE ? 
                    OR filename LIKE '%' || ? || '%'
                )
            '''
            params.extend(['%' + query + '%', '%' + query + '%', query])
        else:
            base_query += ' WHERE 1=1'

        # 获取总记录数
        count_query = f"SELECT COUNT(*) as total FROM ({base_query})"
        total = database.execute(count_query, params).fetchone()['total']

        # 添加排序和分页
        base_query += f' ORDER BY {sort} {order} LIMIT ? OFFSET ?'
        params.extend([per_page, (page - 1) * per_page])

        # 执行查询
        pics = database.execute(base_query, params).fetchall()

        # 构造结果
        items = []
        for pic in pics:
            # 查找实际文件路径
            file_path = find_file_path(pic['filename'])
            if file_path:
                url = url_for('uploaded_file', filename=pic['filename'])
                full_url = 'http://' + app.config['running_domain']
                if app.config['running_port'] != 80:
                    full_url += ':' + str(app.config['running_port'])
                full_url += url

                items.append({
                    'id': pic['id'],
                    'filename': pic['filename'],
                    'url': full_url,
                    'created': pic['created']
                })

        return jsonify({
            'items': items,
            'total': total,
            'current_page': page,
            'total_pages': (total + per_page - 1) // per_page
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(500)
def internal_error(error):
    print('Server Error: %s' % str(error))
    print(traceback.format_exc())  # 打印完整的错误堆栈
    return '服务器错误: %s' % str(error), 500

@app.route('/archive_files', methods=['POST'])
def archive_files():
    try:
        # 确保目标目录存在
        os.makedirs(IMAGES_ROOT, exist_ok=True)
        
        # 创建以日期命名的目标文件夹
        today = datetime.now().strftime('%Y%m%d')
        target_dir = os.path.join(IMAGES_ROOT, today)
        
        # 检查今天是否已经归档过
        if os.path.exists(target_dir):
            return jsonify({
                'success': False,
                'message': '今天已经归档过文件了，每天只能归档一次'
            })
        
        # 获取所有图片文件
        files = os.listdir(upload_folder)
        if not files:
            return jsonify({
                'success': False,
                'message': '没有需要归档的文件'
            })
        
        moved_files = []
        os.makedirs(target_dir)  # 创建目标文件夹
        
        # 获取数据库连接
        database = db.get_db()
        
        for filename in files:
            src_path = os.path.join(upload_folder, filename)
            dst_path = os.path.join(target_dir, filename)
            
            if os.path.isfile(src_path):
                # 移动文件
                shutil.move(src_path, dst_path)
                moved_files.append(filename)
        
        if not moved_files:
            # 如果没有移动任何文件，删除空文件夹
            os.rmdir(target_dir)
            return jsonify({
                'success': False,
                'message': '没有可移动的文件'
            })
        
        # 更新配置和数据库中的文件路径
        app.config['UPLOAD_FOLDER'] = target_dir
        
        # 保存归档记录到配置文件
        with open(os.path.join(IMAGES_ROOT, 'archive_history.txt'), 'a') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: {len(moved_files)} files moved to {target_dir}\n")
        
        return jsonify({
            'success': True,
            'message': f'已将 {len(moved_files)} 个文件移动到 {os.path.basename(target_dir)} 文件夹',
            'archive_path': target_dir
        })
        
    except Exception as e:
        print(f"归档文件时出错: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'归档文件时出错: {str(e)}'
        })

@app.route('/restart_app', methods=['POST'])
def restart_app():
    try:
        # 使用 cmd /c 来执行批处理文件
        subprocess.Popen('cmd /c restart.bat', shell=True)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/open_folder', methods=['POST'])
def open_folder():
    try:
        data = request.get_json()
        filename = data.get('filename')
        
        if filename:
            # 如果指定了文件名，查找文件位置
            file_path = None
            # 检查 pics 目录
            pics_path = os.path.join(os.getcwd(), 'pics', filename)
            if os.path.exists(pics_path):
                file_path = os.path.dirname(pics_path)
            else:
                # 检查 images 目录
                images_root = os.path.join(os.getcwd(), 'images')
                for root, _, files in os.walk(images_root):
                    if filename in files:
                        file_path = root
                        break
            
            if not file_path:
                return jsonify({'success': False, 'message': '找不到文件'})
                
            folder_path = file_path
        else:
            # 如果没有指定文件名，打开 pics 目录
            folder_path = os.path.join(os.getcwd(), 'pics')
            
        # 打开文件夹
        if sys.platform == 'win32':
            os.startfile(folder_path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.Popen(['open', folder_path])
        else:  # linux
            subprocess.Popen(['xdg-open', folder_path])
            
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    # 初始化配置
    init_app_config(app, cf)
    
    # 确保必要目录存在
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(upload_folder, exist_ok=True)
    os.makedirs(trash_folder, exist_ok=True)
    
    # 异步执行文件检查
    def async_check_files():
        with app.app_context():
            check_result = db.check_files_and_records()
            if check_result['status'] == 'mismatch':
                print("\n发现文件不匹配:")
                if check_result['orphaned_files']:
                    print(f"孤立文件: {len(check_result['orphaned_files'])} 个")
                if check_result['missing_files']:
                    print(f"丢失文件: {len(check_result['missing_files'])} 个")
            else:
                print("\n文件检查通过")
    
    from threading import Thread
    Thread(target=async_check_files).start()
    
    # 启动应用
    print("正在启动应用...")
    app.run(debug=False, host=app.config['running_domain'], port=app.config['running_port'])






