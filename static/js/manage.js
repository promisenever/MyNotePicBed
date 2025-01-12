// 通用工具函数
const utils = {
    formatTime(date) {
        return date.toLocaleTimeString('zh-CN', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit' 
        });
    },
    
    showMessage(message, isError = false) {
        alert(message); // 可以改进为更友好的提示方式
    }
};

// 剪贴板操作类
class ClipboardManager {
    constructor() {
        this.initClipboard();
        this.bindEvents();
    }
    
    initClipboard() {
        new ClipboardJS('.copy-btn');
        new ClipboardJS('.filename-cell');
    }
    
    bindEvents() {
        // 复制文件名提示
        $('.filename-cell').click(this.handleCopy.bind(this));
        // 复制链接提示
        $('.copy-btn').click(this.handleCopy.bind(this));
        // 复制Markdown链接
        $('.copy-md-btn').click(this.handleMarkdownCopy.bind(this));
    }
    
    handleCopy(e) {
        const $element = $(e.currentTarget);
        const originalText = $element.text();
        $element.text('已复制!');
        setTimeout(() => {
            $element.text(originalText);
        }, 2000);
    }
    
    handleMarkdownCopy(e) {
        const $btn = $(e.currentTarget);
        const filename = $btn.data('filename');
        const url = $btn.data('url');
        const markdown = `![${filename}](${url})`;
        
        const textarea = document.createElement('textarea');
        textarea.value = markdown;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        
        this.handleCopy(e);
    }
}

// 表格管理类
class TableManager {
    constructor() {
        this.bindEvents();
        this.currentPage = 1;
    }
    
    bindEvents() {
        $('#masterCheckbox').change(e => this.handleMasterCheckbox(e));
        $('#selectAll').click(() => this.handleSelectAll());
        $('#deleteSelected').click(() => this.handleDeleteSelected());
        $('#checkInvalid').click(() => this.handleCheckInvalid());
        $('.delete-btn').click(e => this.handleDelete(e));
        $('#refreshTable').click(() => this.refreshTable());
        
        // 修改搜索相关事件
        $('#searchBtn').click(() => this.handleSearch());
        $('#clearSearchBtn').click(() => this.clearSearch());
        $('#searchInput').keypress(e => {
            if (e.which === 13) {
                this.handleSearch();
            }
        });
        
        // 添加页面跳转事件
        $('#goToPage').click(() => this.handlePageJump());
        $('#pageInput').keypress(e => {
            if (e.which === 13) {
                this.handlePageJump();
            }
        });
        
        // 添加归档按钮事件
        $('#archiveFiles').click(() => this.handleArchive());
    }
    
    handleMasterCheckbox(e) {
        $('.pic-checkbox').prop('checked', $(e.target).prop('checked'));
    }
    
    handleSelectAll() {
        $('.pic-checkbox').prop('checked', true);
        $('#masterCheckbox').prop('checked', true);
    }
    
    handleDeleteSelected() {
        const selectedPics = [];
        $('.pic-checkbox:checked').each(function() {
            selectedPics.push({
                filename: $(this).data('filename'),
                id: $(this).data('id')
            });
        });

        if (selectedPics.length === 0) {
            utils.showMessage('请先选择要删除的图片');
            return;
        }

        this.deletePics(selectedPics);
    }
    
    handleCheckInvalid() {
        $('.invalid-image').each(function() {
            $(this).closest('tr').find('.pic-checkbox').prop('checked', true);
        });
    }
    
    handleDelete(e) {
        const $btn = $(e.currentTarget);
        this.deletePics([{
            filename: $btn.data('filename'),
            id: $btn.data('id')
        }]);
    }
    
    deletePics(pics) {
        if (!confirm(`确定要删除选中的 ${pics.length} 张图片吗？`)) {
            return;
        }

        $.ajax({
            url: '/delete_pics',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ pics: pics }),
            success: (response) => {
                if (response.success) {
                    response.deleted_ids.forEach(id => {
                        $(`input[data-id="${id}"]`).closest('tr').remove();
                    });
                    utils.showMessage(`成功删除 ${response.deleted_ids.length} 张图片`);
                } else {
                    utils.showMessage('删除失败：' + response.message, true);
                }
            },
            error: () => {
                utils.showMessage('删除请求失败，请重试', true);
            }
        });
    }
    
    refreshTable() {
        const $refreshBtn = $('#refreshTable');
        const $refreshIcon = $refreshBtn.find('i');
        const $btn = $(this);
        
        $refreshIcon.addClass('fa-spin');
        $btn.prop('disabled', true);
        
        // 直接刷新页面
        window.location.reload();
        
        // 3秒后如果页面没有刷新，恢复按钮状态
        setTimeout(() => {
            $refreshIcon.removeClass('fa-spin');
            $btn.prop('disabled', false);
        }, 3000);
    }
    
    initializeEventListeners() {
        new ClipboardManager();
        this.bindEvents();
    }
    
    handleSearch() {
        const query = $('#searchInput').val().trim();
        if (!query) {
            this.refreshTable();
            return;
        }
        
        const urlParams = new URLSearchParams(window.location.search);
        const sort = urlParams.get('sort') || 'created';
        const order = urlParams.get('order') || 'DESC';
        
        this.searchPics(query, sort, order, 1);
    }
    
    searchPics(query, sort, order, page) {
        fetch(`/search_pics?query=${encodeURIComponent(query)}&sort=${sort}&order=${order}&page=${page}`)
            .then(response => response.json())
            .then(result => {
                if (result.items && result.items.length > 0) {
                    this.updateTableWithResults(result.items);
                    this.updatePagination(result.current_page, result.total_pages, result.total);
                } else {
                    const tbody = $('tbody');
                    tbody.html('<tr><td colspan="6" class="text-center">没有找到匹配的图片</td></tr>');
                }
            })
            .catch(error => {
                console.error('搜索失败:', error);
                utils.showMessage('搜索失败，请重试', true);
            });
    }
    
    updatePagination(currentPage, totalPages, totalItems) {
        const pagination = $('<nav aria-label="Page navigation"><ul class="pagination mb-0"></ul></nav>');
        const ul = pagination.find('ul');
        
        // 添加上一页按钮
        ul.append(`
            <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage-1}" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                </a>
            </li>
        `);
        
        // 添加页码
        for (let i = Math.max(1, currentPage-2); i <= Math.min(totalPages, currentPage+2); i++) {
            ul.append(`
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `);
        }
        
        // 添加下一页按钮
        ul.append(`
            <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
                <a class="page-link" href="#" data-page="${currentPage+1}" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                </a>
            </li>
        `);
        
        // 当总页数大于等于3页时，添加跳转输入框
        if (totalPages >= 3) {
            pagination.append(`
                <div class="input-group ml-2" style="width: 150px;">
                    <input type="number" class="form-control" id="searchPageInput" 
                           min="1" max="${totalPages}" 
                           placeholder="页码">
                    <div class="input-group-append">
                        <button class="btn btn-outline-secondary" type="button" id="searchGoToPage">
                            跳转
                        </button>
                    </div>
                </div>
            `);
        }
        
        // 替换分页导航
        $('.table-responsive').next('.d-flex').replaceWith(
            $('<div class="d-flex justify-content-between align-items-center mt-3"></div>')
                .append(`<div class="text-muted">共 ${totalItems} 条记录，当前第 ${currentPage}/${totalPages} 页</div>`)
                .append(pagination)
        );
        
        // 绑定页码点击事件
        $('.page-link').click(e => {
            e.preventDefault();
            const page = $(e.currentTarget).data('page');
            if (!page || $(e.currentTarget).parent().hasClass('disabled')) return;
            
            const query = $('#searchInput').val().trim();
            const urlParams = new URLSearchParams(window.location.search);
            const sort = urlParams.get('sort') || 'created';
            const order = urlParams.get('order') || 'DESC';
            
            this.searchPics(query, sort, order, page);
        });
        
        // 绑定搜索结果页面跳转事件
        $('#searchGoToPage').click(() => {
            const pageInput = $('#searchPageInput');
            const targetPage = parseInt(pageInput.val());
            
            if (isNaN(targetPage) || targetPage < 1 || targetPage > totalPages) {
                utils.showMessage(`请输入1到${totalPages}之间的页码`);
                return;
            }
            
            const query = $('#searchInput').val().trim();
            const urlParams = new URLSearchParams(window.location.search);
            const sort = urlParams.get('sort') || 'created';
            const order = urlParams.get('order') || 'DESC';
            
            this.searchPics(query, sort, order, targetPage);
        });
        
        // 绑定回车键事件
        $('#searchPageInput').keypress(e => {
            if (e.which === 13) {
                $('#searchGoToPage').click();
            }
        });
    }
    
    clearSearch() {
        $('#searchInput').val('');
        window.location.href = window.location.pathname;
    }
    
    updateTableWithResults(results) {
        const tbody = $('tbody');
        tbody.empty();
        
        if (results.length === 0) {
            tbody.append('<tr><td colspan="6" class="text-center">没有找到匹配的图片</td></tr>');
            return;
        }
        
        results.forEach(pic => {
            const row = this.createTableRow(pic);
            tbody.append(row);
        });
        
        // 重新绑定事件
        this.initializeEventListeners();
    }
    
    createTableRow(pic) {
        return `
            <tr>
                <td class="checkbox-column">
                    <input type="checkbox" class="pic-checkbox" 
                           data-id="${pic.id}" 
                           data-filename="${pic.filename}">
                </td>
                <td>${pic.id}</td>
                <td class="filename-cell" 
                    title="${pic.filename}"
                    data-clipboard-text="${pic.filename}">
                    ${pic.filename}
                </td>
                <td>
                    <img src="${pic.url}" 
                         style="max-width: 100px; max-height: 100px; object-fit: contain;" 
                         alt="预览"
                         onerror="this.classList.add('invalid-image')">
                </td>
                <td>${pic.created}</td>
                <td>
                    <div class="input-group">
                        <input type="text" class="form-control" 
                               value="${pic.url}" 
                               readonly>
                        <div class="input-group-append">
                            <button class="btn btn-outline-secondary copy-btn" 
                                    data-clipboard-text="${pic.url}">
                                复制链接
                            </button>
                            <button class="btn btn-outline-info copy-md-btn" 
                                    data-filename="${pic.filename}"
                                    data-url="${pic.url}">
                                复制Markdown
                            </button>
                            <button class="btn btn-outline-danger delete-btn" 
                                    data-filename="${pic.filename}"
                                    data-id="${pic.id}">
                                删除
                            </button>
                        </div>
                    </div>
                </td>
            </tr>
        `;
    }
    
    handlePageJump() {
        const pageInput = $('#pageInput');
        const targetPage = parseInt(pageInput.val());
        const maxPage = parseInt(pageInput.attr('max'));
        
        if (isNaN(targetPage) || targetPage < 1 || targetPage > maxPage) {
            utils.showMessage(`请输入1到${maxPage}之间的页码`);
            return;
        }
        
        const query = $('#searchInput').val().trim();
        const urlParams = new URLSearchParams(window.location.search);
        const sort = urlParams.get('sort') || 'created';
        const order = urlParams.get('order') || 'DESC';
        
        if (query) {
            this.searchPics(query, sort, order, targetPage);
        } else {
            window.location.href = `${window.location.pathname}?page=${targetPage}&sort=${sort}&order=${order}`;
        }
    }
    
    handleArchive() {
        if (!confirm('确定要将当前文件归档吗？\n归档后的文件将被移动到按日期命名的文件夹中。\n注意：这将改变文件的存储位置！')) {
            return;
        }
        
        const $btn = $('#archiveFiles');
        const $icon = $btn.find('i');
        $btn.prop('disabled', true);
        $icon.removeClass('fa-archive').addClass('fa-spinner fa-spin');
        
        fetch('/archive_files', {
            method: 'POST',
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                utils.showMessage(result.message);
            } else {
                utils.showMessage(result.message, true);
            }
        })
        .catch(error => {
            console.error('归档失败:', error);
            utils.showMessage('归档请求失败，请重试', true);
        })
        .finally(() => {
            $btn.prop('disabled', false);
            $icon.removeClass('fa-spinner fa-spin').addClass('fa-archive');
        });
    }
}

// 文件检查管理类
class FileCheckManager {
    constructor() {
        this.bindEvents();
        this.checkFiles();
    }
    
    bindEvents() {
        $('#restoreOrphaned').click(this.handleRestore.bind(this));
        $('#cleanOrphaned').click(this.handleCleanOrphaned.bind(this));
        $('#cleanSelectedMissing').click(() => this.handleCleanMissing(true));
        $('#keepSelectedMissing').click(() => this.handleCleanMissing(false));
        $('#cleanAll').click(() => this.handleCleanAll());
        $('#selectAllOrphaned').click(this.handleSelectAllOrphaned.bind(this));
        $('#selectAllMissing').click(this.handleSelectAllMissing.bind(this));
    }
    
    handleSelectAllOrphaned() {
        const isChecked = $('#selectAllOrphaned').prop('checked');
        $('.orphaned-file-checkbox').prop('checked', isChecked);
    }
    
    handleSelectAllMissing() {
        const isChecked = $('#selectAllMissing').prop('checked');
        $('.missing-file-checkbox').prop('checked', isChecked);
    }
    
    handleCleanMissing(deleteSelected) {
        const selectedFiles = $('.missing-file-checkbox:checked').map(function() {
            return {
                id: $(this).val(),
                filename: $(this).data('filename')
            };
        }).get();
        
        if (selectedFiles.length === 0) {
            utils.showMessage('请选择要处理的记录');
            return;
        }
        
        const action = deleteSelected ? '删除' : '保留';
        if (!confirm(`确定要${action}选中的 ${selectedFiles.length} 条记录吗？`)) {
            return;
        }
        
        fetch('/clean_files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                clean_records: true,
                missing_files: selectedFiles,
                keep_selected: !deleteSelected
            }),
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                utils.showMessage(`成功${action}选中记录`);
                $('#fileCheckModal').modal('hide');
                window.location.reload();
            } else {
                utils.showMessage('操作失败：' + result.message, true);
            }
        })
        .catch(error => {
            console.error('操作失败:', error);
            utils.showMessage('请求失败，请重试', true);
        });
    }
    
    checkFiles() {
        fetch('/check_files')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'mismatch') {
                    this.showModal(data);
                }
            })
            .catch(error => {
                console.error('检查文件失败:', error);
            });
    }
    
    showModal(data) {
        const modal = $('#fileCheckModal');
        const orphanedDiv = $('#orphanedFiles');
        const missingDiv = $('#missingFiles');
        
        // 显示孤立文件
        if (data.orphaned_files.length > 0) {
            orphanedDiv.show();
            const container = orphanedDiv.find('.file-list');
            container.empty();
            
            // 添加全选复选框
            container.append(`
                <div class="mb-2">
                    <input type="checkbox" id="selectAllOrphaned" checked>
                    <label for="selectAllOrphaned">全选/取消全选</label>
                </div>
            `);
            
            data.orphaned_files.forEach(filename => {
                container.append(`
                    <div class="form-check">
                        <input type="checkbox" class="form-check-input orphaned-file-checkbox" 
                               id="file-${filename}" value="${filename}" checked>
                        <label class="form-check-label" for="file-${filename}">
                            ${filename}
                        </label>
                    </div>
                `);
            });
        } else {
            orphanedDiv.hide();
        }
        
        // 显示丢失文件
        if (data.missing_files.length > 0) {
            missingDiv.show();
            const container = missingDiv.find('.file-list');
            container.empty();
            
            // 添加全选复选框
            container.append(`
                <div class="mb-2">
                    <input type="checkbox" id="selectAllMissing" checked>
                    <label for="selectAllMissing">全选/取消全选</label>
                </div>
            `);
            
            data.missing_files.forEach(file => {
                container.append(`
                    <div class="form-check">
                        <input type="checkbox" class="form-check-input missing-file-checkbox" 
                               id="missing-${file.id}" value="${file.id}" checked
                               data-filename="${file.filename}">
                        <label class="form-check-label" for="missing-${file.id}">
                            ${file.filename}
                        </label>
                    </div>
                `);
            });
        } else {
            missingDiv.hide();
        }
        
        modal.modal('show');
    }
    
    handleRestore() {
        const selectedFiles = $('.orphaned-file-checkbox:checked').map(function() {
            return $(this).val();
        }).get();
        
        if (selectedFiles.length === 0) {
            utils.showMessage('请选择要恢复的文件');
            return;
        }
        
        if (!confirm(`确定要恢复选中的 ${selectedFiles.length} 个文件到数据库吗？`)) {
            return;
        }
        
        fetch('/restore_files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                filenames: selectedFiles
            }),
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                const message = [];
                if (result.restored.length > 0) {
                    message.push(`成功恢复 ${result.restored.length} 个文件`);
                }
                if (result.failed.length > 0) {
                    message.push(`${result.failed.length} 个文件恢复失败`);
                }
                utils.showMessage(message.join('\n'));
                $('#fileCheckModal').modal('hide');
                window.location.reload();
            } else {
                utils.showMessage('恢复失败：' + result.message, true);
            }
        })
        .catch(error => {
            console.error('恢复失败:', error);
            utils.showMessage('恢复请求失败，请重试', true);
        });
    }
    
    handleCleanOrphaned() {
        const filesToDelete = [];
        $('.orphaned-file-checkbox:not(:checked)').each(function() {
            filesToDelete.push($(this).val());
        });
        
        if (filesToDelete.length === 0) {
            utils.showMessage('没有选择要删除的文件');
            return;
        }
        
        this.handleClean({ 
            clean_files: true,
            orphaned_files: filesToDelete
        });
    }
    
    handleClean(options) {
        let confirmMessage = '';
        if (options.clean_records) {
            confirmMessage = '确定要清理所有丢失文件的数据库记录吗？';
        } else if (options.clean_files && options.clean_records) {
            confirmMessage = '确定要一键清理所有问题吗？这将删除所有孤立文件并清理所有丢失文件的记录。';
        }
        
        if (confirmMessage && !confirm(confirmMessage)) {
            return;
        }
        
        // 确保传递正确的数据
        if (options.clean_records) {
            options.missing_files = $('#missingFiles .file-list div').map(function() {
                return { 
                    id: $(this).data('id'),
                    filename: $(this).text()
                };
            }).get();
        }
        
        fetch('/clean_files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(options),
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                $('#fileCheckModal').modal('hide');
                utils.showMessage('清理成功');
                window.location.reload();
            } else {
                utils.showMessage('清理失败：' + result.message, true);
            }
        })
        .catch(error => {
            console.error('清理失败:', error);
            utils.showMessage('清理请求失败，请重试', true);
        });
    }
    
    handleCleanAll() {
        const confirmMessage = 
            '此操作将：\n' +
            '1. 删除所有没有数据库记录的文件\n' +
            '2. 删除所有找不到对应文件的数据库记录\n\n' +
            '确定要执行吗？';
            
        if (!confirm(confirmMessage)) {
            return;
        }
        
        fetch('/clean_files', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                clean_files: true,
                clean_records: true
            }),
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                utils.showMessage('成功删除所有孤立文件并清理了数据库记录');
                $('#fileCheckModal').modal('hide');
                window.location.reload();
            } else {
                utils.showMessage('清理操作失败：' + result.message, true);
            }
        })
        .catch(error => {
            console.error('清理操作失败:', error);
            utils.showMessage('清理操作请求失败，请重试', true);
        });
    }
}

// 在文件开头添加主题管理类
class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'dark';
        this.init();
        this.bindEvents();
    }
    
    init() {
        document.documentElement.setAttribute('data-theme', this.theme);
        this.updateToggleButton();
    }
    
    bindEvents() {
        $('#themeToggle').click(() => this.toggleTheme());
    }
    
    toggleTheme() {
        this.theme = this.theme === 'dark' ? 'light' : 'dark';
        localStorage.setItem('theme', this.theme);
        document.documentElement.setAttribute('data-theme', this.theme);
        this.updateToggleButton();
    }
    
    updateToggleButton() {
        const $button = $('#themeToggle');
        const $icon = $button.find('i');
        
        if (this.theme === 'dark') {
            $icon.removeClass('fa-sun').addClass('fa-moon');
            $button.attr('title', '切换到亮色主题');
        } else {
            $icon.removeClass('fa-moon').addClass('fa-sun');
            $button.attr('title', '切换到深色主题');
        }
    }
}

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    new ClipboardManager();
    new TableManager();
    new FileCheckManager();
    new ThemeManager();  // 添加主题管理器
}); 