import os
from pathlib import Path
import math
import argparse

os.chdir(os.path.dirname(__file__))

def generate_image_wall(directory='.', output_file='image_wall.html', images_per_page=20):
    """
    生成带分页、图片预览和懒加载功能的图片墙HTML文件
    
    参数:
        directory: 要扫描的图片目录，默认为当前目录
        output_file: 输出的HTML文件名
        images_per_page: 每页显示的图片数量，默认为20
    """
    # 支持的图片扩展名
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    
    # 获取目录下的所有图片文件
    image_files = []
    try:
        for entry in os.scandir(directory):
            if entry.is_file() and Path(entry.name).suffix.lower() in image_extensions:
                image_files.append(entry.name)
    except FileNotFoundError:
        print(f"错误：目录 '{directory}' 不存在")
        return
    except PermissionError:
        print(f"错误：没有权限访问目录 '{directory}'")
        return
    
    # 对图片按文件名排序
    image_files.sort()
    
    # 计算总页数
    total_pages = math.ceil(len(image_files) / images_per_page) if image_files else 1
    
    # 生成HTML内容
    html_content = generate_html_content(directory, image_files, total_pages, images_per_page)
    
    # 写入HTML文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"图片墙已生成: {output_file}")
        print(f"共找到 {len(image_files)} 张图片")
        print(f"共分为 {total_pages} 页，每页 {images_per_page} 张图片")
    except IOError as e:
        print(f"错误：无法写入文件 '{output_file}': {e}")

def generate_pagination_links(total_pages):
    """生成分页链接HTML"""
    return f"""
        <a href="#" id="prevPage" onclick="changePage(-1)" style="display:none">上一页</a>
        <a href="#" id="nextPage" onclick="changePage(1)" {'style="display:none"' if total_pages <= 1 else ''}>下一页</a>
    """

def generate_image_containers(image_files, images_per_page):
    """生成图片容器HTML"""
    if not image_files:
        return """
        <div class="no-images">
            没有找到图片文件
        </div>
"""
    
    containers = []
    for i, image_file in enumerate(image_files, 1):
        page_num = math.ceil(i / images_per_page)
        display_style = "block" if page_num == 1 else "none"
        containers.append(f"""
        <div class="image-container" data-page="{page_num}" style="display:{display_style}" onclick="openModal('{image_file}', {i-1})">
            <div class="image-placeholder">点击加载图片</div>
            <img data-src="{image_file}" alt="{image_file}" style="display:none">
            <div class="image-name">{image_file}</div>
        </div>
""")
    return "".join(containers)

def generate_html_content(directory, image_files, total_pages, images_per_page):
    """生成HTML内容"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>图片墙 - {directory}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        h1 {{
            text-align: center;
            color: #333;
        }}
        .image-wall {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            padding: 20px;
        }}
        .image-container {{
            position: relative;
            overflow: hidden;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            background-color: white;
            transition: transform 0.3s ease;
            cursor: pointer;
            min-height: 250px;
        }}
        .image-container:hover {{
            transform: scale(1.03);
        }}
        .image-container img {{
            width: 100%;
            height: 200px;
            object-fit: cover;
            display: none; /* 初始隐藏，懒加载后显示 */
        }}
        .image-placeholder {{
            width: 100%;
            height: 200px;
            background-color: #eee;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #999;
        }}
        .image-name {{
            padding: 10px;
            text-align: center;
            font-size: 14px;
            color: #555;
            word-break: break-all;
        }}
        .no-images {{
            text-align: center;
            padding: 40px;
            font-size: 18px;
            color: #888;
            grid-column: 1 / -1;
        }}
        .pagination {{
            display: flex;
            justify-content: center;
            margin: 20px 0;
            flex-wrap: wrap;
        }}
        .pagination a {{
            color: #333;
            padding: 8px 16px;
            margin: 0 4px;
            text-decoration: none;
            border: 1px solid #ddd;
            border-radius: 4px;
            transition: background-color 0.3s;
        }}
        .pagination a.active {{
            background-color: #4CAF50;
            color: white;
            border: 1px solid #4CAF50;
        }}
        .pagination a:hover:not(.active) {{
            background-color: #ddd;
        }}
        .page-info {{
            text-align: center;
            margin: 10px 0;
            color: #666;
        }}
        /* 图片预览模态框样式 */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.9);
            overflow: auto;
        }}
        .modal-content {{
            margin: auto;
            display: block;
            max-width: 90%;
            max-height: 90%;
            margin-top: 20px;
        }}
        .modal-info {{
            color: white;
            text-align: center;
            padding: 10px;
            font-size: 16px;
        }}
        .close {{
            position: absolute;
            top: 15px;
            right: 35px;
            color: #f1f1f1;
            font-size: 40px;
            font-weight: bold;
            transition: 0.3s;
            cursor: pointer;
        }}
        .close:hover {{
            color: #bbb;
        }}
        .prev, .next {{
            cursor: pointer;
            position: absolute;
            top: 50%;
            width: auto;
            padding: 16px;
            margin-top: -50px;
            color: white;
            font-weight: bold;
            font-size: 20px;
            transition: 0.3s;
            user-select: none;
        }}
        .next {{
            right: 0;
            border-radius: 3px 0 0 3px;
        }}
        .prev {{
            left: 0;
            border-radius: 0 3px 3px 0;
        }}
        .prev:hover, .next:hover {{
            background-color: rgba(0, 0, 0, 0.8);
        }}
        /* 加载动画 */
        .loading-spinner {{
            border: 4px solid rgba(0, 0, 0, 0.1);
            border-radius: 50%;
            border-top: 4px solid #3498db;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }}
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
    </style>
</head>
<body>
    <h1>{directory} 目录图片墙</h1>
    <div class="page-info" id="pageInfo">第1页，共{total_pages}页</div>
    <div class="pagination" id="pagination">
        {generate_pagination_links(total_pages)}
    </div>
    <div class="image-wall">
        {generate_image_containers(image_files, images_per_page)}
    </div>
    
    <!-- 图片预览模态框 -->
    <div id="imageModal" class="modal">
        <span class="close" onclick="closeModal()">&times;</span>
        <span class="prev" onclick="changeImage(-1)">&#10094;</span>
        <span class="next" onclick="changeImage(1)">&#10095;</span>
        <img class="modal-content" id="modalImage">
        <div class="modal-info" id="modalInfo"></div>
    </div>

    <script>
        // 图片数据
        const imagesPerPage = {images_per_page};
        const totalPages = {total_pages};
        const allImages = {image_files};
        let currentPage = 1;
        let currentImageIndex = 0;
        const modal = document.getElementById('imageModal');
        let observer;
        
        // 修改分页函数
        function changePage(step) {{
            const newPage = currentPage + step;
            if (newPage < 1 || newPage > totalPages) return;
            
            currentPage = newPage;
            showPage(currentPage);
        }}
        
        // 修改showPage函数
        function showPage(page) {{
            // 更新页码信息
            document.getElementById('pageInfo').textContent = `第${{page}}页，共${{totalPages}}页`;
            
            // 更新分页按钮显示状态
            document.getElementById('prevPage').style.display = page > 1 ? 'inline' : 'none';
            document.getElementById('nextPage').style.display = page < totalPages ? 'inline' : 'none';
            
            // 显示对应页的图片
            updateVisibleImages(page);
            
            // 重新初始化观察者
            resetObserver();
            
            // 滚动到顶部
            window.scrollTo({{top: 0, behavior: 'smooth'}});
        }}
        
        // 更新可见图片
        function updateVisibleImages(page) {{
            const images = document.querySelectorAll('.image-container');
            images.forEach(img => {{
                const imgPage = parseInt(img.dataset.page);
                img.style.display = imgPage === page ? 'block' : 'none';
            }});
        }}
        
        // 初始化IntersectionObserver用于懒加载
        function initObserver() {{
            observer = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        const container = entry.target;
                        const img = container.querySelector('img');
                        const placeholder = container.querySelector('.image-placeholder');
                        
                        if (img && !img.src) {{
                            // 显示加载动画
                            placeholder.innerHTML = '<div class="loading-spinner"></div>';
                            
                            img.src = img.dataset.src;
                            img.onload = () => {{
                                img.style.display = 'block';
                                placeholder.style.display = 'none';
                            }};
                            img.onerror = () => {{
                                placeholder.innerHTML = '加载失败';
                            }};
                            observer.unobserve(container);
                        }}
                    }}
                }});
            }}, {{
                rootMargin: '200px',
                threshold: 0.01
            }});
            
            // 观察当前页的所有图片容器
            document.querySelectorAll('.image-container[style*="display: block"]').forEach(container => {{
                observer.observe(container);
            }});
        }}
        
        // 重置观察者
        function resetObserver() {{
            if (observer) {{
                observer.disconnect();
            }}
            initObserver();
        }}
        
        // 打开图片预览
        function openModal(imgSrc, imgIndex) {{
            currentImageIndex = imgIndex;
            const modalImg = document.getElementById('modalImage');
            modalImg.src = imgSrc;
            document.getElementById('modalInfo').textContent = `${{imgSrc}} (${{imgIndex+1}}/${{allImages.length}})`;
            modal.style.display = "block";
        }}
        
        // 关闭图片预览
        function closeModal() {{
            modal.style.display = "none";
        }}
        
        // 切换图片
        function changeImage(step) {{
            currentImageIndex += step;
            // 循环浏览
            if (currentImageIndex >= allImages.length) {{
                currentImageIndex = 0;
            }} else if (currentImageIndex < 0) {{
                currentImageIndex = allImages.length - 1;
            }}
            document.getElementById('modalImage').src = allImages[currentImageIndex];
            document.getElementById('modalInfo').textContent = `${{allImages[currentImageIndex]}} (${{currentImageIndex+1}}/${{allImages.length}})`;
        }}
        
        // 点击模态框外部关闭
        modal.addEventListener('click', function(event) {{
            if (event.target === modal) {{
                closeModal();
            }}
        }});
        
        // 键盘导航
        document.addEventListener('keydown', function(event) {{
            if (modal.style.display === "block") {{
                if (event.key === 'Escape') {{
                    closeModal();
                }} else if (event.key === 'ArrowRight') {{
                    changeImage(1);
                }} else if (event.key === 'ArrowLeft') {{
                    changeImage(-1);
                }}
            }}
        }});
        
        // 初始化页面
        document.addEventListener('DOMContentLoaded', function() {{
            initObserver();
        }});
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='生成带分页、图片预览和懒加载功能的图片墙HTML文件')
    parser.add_argument('-d', '--directory', default='.', 
                       help='要扫描的图片目录，默认为当前目录')
    parser.add_argument('-o', '--output', default='image_wall.html', 
                       help='输出的HTML文件名，默认为image_wall.html')
    parser.add_argument('-n', '--number', type=int, default=50,
                       help='每页显示的图片数量，默认为20')
    
    args = parser.parse_args()
    
    generate_image_wall(args.directory, args.output, args.number)
