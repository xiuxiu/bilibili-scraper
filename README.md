# Bilibili视频详情页HTML逆向采集

直接请求Bilibili视频页面HTML，解析关键信息。

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

```bash
python bilibili_scraper.py <视频BV号/AV号/URL>
```

### 示例

```bash
# 使用BV号
python bilibili_scraper.py BV1xx411c7XD

# 使用AV号
python bilibili_scraper.py av123456789

# 使用完整URL
python bilibili_scraper.py https://www.bilibili.com/video/BV1xx411c7XD/
```

## 输出文件

- `output/{video_id}.html` - 原始HTML页面
- `output/{video_id}_info.json` - 解析后的JSON信息

## 采集信息

- 标题、描述
- UP主名称
- 发布时间
- 播放量、点赞、投币、收藏、分享
- 弹幕数
- 封面图
- 视频时长
- Tags

## 注意事项

1. 此脚本仅用于学习和研究
2. 请遵守Bilibili的服务条款
3. 过于频繁的请求可能导致IP被封禁
