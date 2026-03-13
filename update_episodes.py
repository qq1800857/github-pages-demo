import os
import json
import re

html_files = ["exception_log.html", "doc_stealth.html", "github_stealth.html", "baidu_stealth.html"]

prefixes = [f"Episode {i} " for i in range(1, 11)]
txt_files = [f for f in os.listdir(".") if f.endswith(".txt") and any(f.startswith(p) for p in prefixes)]

# Sort by episode number then act number
def sort_key(name):
    # Extract episode number
    m = re.match(r"Episode (\d+) ", name)
    ep = int(m.group(1)) if m else 0
    # Extract act
    act_order = {"ACT I.txt": 1, "ACT II.txt": 2, "ACT III.txt": 3}
    act = 0
    for k, v in act_order.items():
        if name.endswith(k):
            act = v
            break
    return (ep, act)

txt_files.sort(key=sort_key)
total = len(txt_files)
print(f"Found {total} episodes to inject.")

def get_title(html_file, idx, filename):
    base = filename.replace('.txt', '')
    if html_file == "exception_log.html":
        return f"var/log/syslog - {base}"
    elif html_file == "doc_stealth.html":
        return f"Version 3.{idx}.0.RELEASE"
    elif html_file == "github_stealth.html":
        os_list = ["ubuntu-latest", "macos-latest", "windows-latest"]
        return f"Job: {os_list[idx % 3]} (matrix {idx+1}/{total})"
    elif html_file == "baidu_stealth.html":
        tabs = ["全网热榜", "今日关注", "百度热搜", "小说推荐", "实时新闻",
                "知乎热议", "学术前沿", "每日推荐", "视频精选", "科技快讯",
                "体育赛事", "娱乐八卦", "历史今天", "美食探店", "旅行攻略",
                "健康养生", "财经要闻", "汽车资讯", "教育考试", "职场技能",
                "影视综艺", "音乐排行", "游戏热点", "动漫世界", "时尚穿搭",
                "家居装修", "宠物萌宠", "公益慈善", "天气预报", "星座运势"]
        return tabs[idx % len(tabs)]
    return f"Ep {idx+1}"

episodes_by_file = {f: [] for f in html_files}

for idx, txt_file in enumerate(txt_files):
    mp3_file = txt_file.replace(".txt", ".mp3")
    with open(txt_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
        
    for html_file in html_files:
        title = get_title(html_file, idx, txt_file)
        episodes_by_file[html_file].append({
            "title": title,
            "mp3": mp3_file,
            "text": lines
        })

for html_file in html_files:
    if not os.path.exists(html_file): continue
    
    with open(html_file, "r", encoding="utf-8") as f:
        content = f.read()
        
    js_data = json.dumps(episodes_by_file[html_file], ensure_ascii=False)
    
    start_tag = "const episodes = ["
    end_tag = "];"
    start_idx = content.find(start_tag)
    
    if start_idx != -1:
        end_idx = content.find(end_tag, start_idx)
        if end_idx != -1:
            content = content[:start_idx] + f"const episodes = {js_data};" + content[end_idx + len(end_tag):]
            
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Updated {html_file}")

print(f"Done! Injected {total} episodes into all stealth themes.")
