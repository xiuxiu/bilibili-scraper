#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bilibili视频详情页面HTML逆向采集脚本
直接请求视频页面HTML，解析关键信息
"""

import requests
from urllib.parse import urlparse, parse_qs
import re
import json
import sys

# 请求头，模拟浏览器
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Referer': 'https://www.bilibili.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

BILIBILI_BASE_URL = 'https://www.bilibili.com'


def parse_video_id(url_or_id: str) -> str:
    """
    解析输入的视频ID或URL，返回BV号或AV号
    支持格式:
    - BV1xx411c7XD
    - av123456789
    - https://www.bilibili.com/video/BV1xx411c7XD/
    - https://www.bilibili.com/video/av123456789/
    - https://b23.tv/xxxxx (短链接)
    """
    import requests
    
    url_or_id = url_or_id.strip()
    
    # 如果是完整URL（包括短链接）
    if url_or_id.startswith('http'):
        # 处理短链接，先获取重定向后的真实URL
        if 'b23.tv' in url_or_id:
            try:
                response = requests.head(url_or_id, headers=HEADERS, timeout=10, allow_redirects=True)
                final_url = response.url
                print(f"短链接重定向到: {final_url}")
                url_or_id = final_url
            except Exception as e:
                print(f"解析短链接失败: {e}")
        
        parsed = urlparse(url_or_id)
        path = parsed.path.rstrip('/')
        # 提取BV号或AV号
        if '/video/' in path:
            video_id = path.split('/video/')[-1]
            return video_id
    
    # 如果是BV号
    if url_or_id.startswith('BV'):
        return url_or_id
    
    # 如果是AV号
    if url_or_id.startswith('av'):
        return url_or_id
    
    # 尝试直接作为BV号处理
    return url_or_id


def fetch_video_page(video_id: str) -> requests.Response:
    """
    获取视频详情页HTML
    """
    url = f"{BILIBILI_BASE_URL}/video/{video_id}/"
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response


def extract_video_info(html: str) -> dict:
    """
    从HTML中提取视频信息
    """
    info = {}
    
    # 提取标题
    title_match = re.search(r'<title>([^<]+)', html)
    if title_match:
        info['title'] = title_match.group(1).replace('_哔哩哔哩_bilibili', '').strip()
    
    # 提取UP主
    up_match = re.search(r'"upName":"([^"]+)"', html)
    if up_match:
        info['up_name'] = up_match.group(1)
    
    # 提取发布时间
    pubtime_match = re.search(r'"pubdate":(\d+)', html)
    if pubtime_match:
        import time
        info['publish_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(pubtime_match.group(1))))
    
    # 提取视频简介
    desc_match = re.search(r'"desc":"([^"]+)"', html)
    if desc_match:
        info['description'] = desc_match.group(1).replace('\\n', '\n')
    
    # 提取播放量
    view_match = re.search(r'"view":(\d+)', html)
    if view_match:
        info['views'] = int(view_match.group(1))
    
    # 提取点赞数
    like_match = re.search(r'"like":(\d+)', html)
    if like_match:
        info['likes'] = int(like_match.group(1))
    
    # 提取投币数
    coin_match = re.search(r'"coin":(\d+)', html)
    if coin_match:
        info['coins'] = int(coin_match.group(1))
    
    # 提取收藏数
    favorite_match = re.search(r'"favorite":(\d+)', html)
    if favorite_match:
        info['favorites'] = int(favorite_match.group(1))
    
    # 提取分享数
    share_match = re.search(r'"share":(\d+)', html)
    if share_match:
        info['shares'] = int(share_match.group(1))
    
    # 提取弹幕数
    danmaku_match = re.search(r'"danmaku":(\d+)', html)
    if danmaku_match:
        info['danmakus'] = int(danmaku_match.group(1))
    
    # 提取BV号
    bv_match = re.search(r'"bvid":"([^"]+)"', html)
    if bv_match:
        info['bvid'] = bv_match.group(1)
    
    # 提取AV号
    aid_match = re.search(r'"aid":(\d+)', html)
    if aid_match:
        info['aid'] = int(aid_match.group(1))
    
    # 提取分P数量
    pages_match = re.search(r'"pages":(\d+)', html)
    if pages_match:
        info['pages'] = int(pages_match.group(1))
    
    # 提取时长
    duration_match = re.search(r'"duration":(\d+)', html)
    if duration_match:
        total_seconds = int(duration_match.group(1))
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        info['duration'] = f"{minutes}:{seconds:02d}"
    
    # 提取封面图
    cover_match = re.search(r'"cover":"([^"]+)"', html)
    if cover_match:
        info['cover'] = cover_match.group(1).replace('\\/', '/')
    
    # 提取视频Tags
    tags_match = re.search(r'"tag".*?"tag_name":"([^"]+)"', html)
    if tags_match:
        info['tag'] = tags_match.group(1)
    
    return info


def save_html(html: str, video_id: str, output_dir: str = 'output'):
    """
    保存原始HTML到文件
    """
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # 清理文件名中的非法字符
    safe_id = re.sub(r'[<>:"/\\|?*]', '_', video_id)
    filename = f"{safe_id}.html"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML已保存到: {filepath}")
    return filepath


def main():
    """
    主函数
    """
    if len(sys.argv) < 2:
        print("用法: python bilibili_scraper.py <视频BV号/AV号/URL>")
        print("示例:")
        print("  python bilibili_scraper.py BV1xx411c7XD")
        print("  python bilibili_scraper.py av123456789")
        print("  python bilibili_scraper.py https://www.bilibili.com/video/BV1xx411c7XD/")
        sys.exit(1)
    
    video_input = sys.argv[1]
    
    # 解析视频ID
    video_id = parse_video_id(video_input)
    print(f"正在获取视频: {video_id}")
    
    # 获取视频页面
    print("请求页面中...")
    response = fetch_video_page(video_id)
    print(f"页面状态码: {response.status_code}")
    print(f"页面大小: {len(response.text)} 字节")
    
    # 保存原始HTML
    html_file = save_html(response.text, video_id)
    
    # 解析视频信息
    print("\n解析视频信息中...")
    info = extract_video_info(response.text)
    
    # 打印结果
    print("\n" + "="*50)
    print("视频信息:")
    print("="*50)
    for key, value in info.items():
        print(f"  {key}: {value}")
    print("="*50)
    
    # 保存JSON结果
    import os
    os.makedirs('output', exist_ok=True)
    json_file = f"output/{video_id}_info.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)
    print(f"\nJSON信息已保存到: {json_file}")


if __name__ == '__main__':
    main()
