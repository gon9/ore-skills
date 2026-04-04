import argparse
from collections import defaultdict
from pathlib import Path


def extract_tags(content):
    """ファイル内容からタグを抽出"""
    tags = []
    for line in content.splitlines():
        if line.strip().startswith("tags:"):
            # tags: #tag1 #tag2 形式を想定
            tag_line = line.strip().replace("tags:", "").strip()
            tags = [t.strip() for t in tag_line.split("#") if t.strip()]
            break
    return tags

def categorize_by_tags(tags):
    """タグからカテゴリを決定"""
    # タグの優先順位でカテゴリ分類
    # topic系タグを優先的に使用
    topic_tags = [t for t in tags if t.startswith("topic/")]
    
    if not topic_tags:
        # type系タグで分類
        type_tags = [t for t in tags if t.startswith("type/")]
        if type_tags:
            return type_tags[0].replace("type/", "").replace("-", " ").title()
        # status系タグで分類
        status_tags = [t for t in tags if t.startswith("status/")]
        if status_tags:
            return "Status: " + status_tags[0].replace("status/", "").replace("-", " ").title()
        return "その他"
    
    # topic系タグから主要カテゴリを抽出
    main_topic = topic_tags[0].split("/")[1] if "/" in topic_tags[0] else topic_tags[0]
    
    # カテゴリマッピング
    category_map = {
        "self-reflection": "自己省察",
        "productivity": "生産性・効率化",
        "motivation": "モチベーション",
        "tech": "技術",
        "communication": "コミュニケーション",
        "management": "マネジメント",
        "lifehack": "ライフハック",
        "ai": "AI",
    }
    
    for key, value in category_map.items():
        if key in main_topic.lower():
            return value
    
    return main_topic.replace("-", " ").title()

def infer_category_from_content(file_path, content):
    """タグがない場合、ファイル名と内容からカテゴリを推測"""
    filename = file_path.stem.lower()
    content_lower = content.lower()
    
    # ファイル名ベースの推測
    if "adhd" in filename or "落合" in filename:
        return "生産性・効率化"
    if "pw" in filename or "パスワード" in filename:
        return "リソース・参考情報"
    if "chatgpt" in filename or "パーソナライズ" in filename:
        return "リソース・参考情報"
    if "やること" in filename or "todo" in filename:
        return "タスク管理"
    if "夢日記" in filename:
        return "日記・記録"
    if "旅行" in filename:
        return "日記・記録"
    if "アントラーズ" in filename or "サッカー" in filename:
        return "趣味・関心"
    
    # 内容ベースの推測（キーワード頻度）
    keywords = {
        "自己省察": ["自分", "価値観", "性格", "目標", "キャリア"],
        "生産性・効率化": ["adhd", "タスク", "効率", "生産性", "tips"],
        "技術": ["機械学習", "エンジニア", "開発", "システム", "api"],
        "マネジメント": ["チーム", "組織", "マネージャー", "リーダー"],
    }
    
    scores = defaultdict(int)
    for category, words in keywords.items():
        for word in words:
            if word in content_lower:
                scores[category] += 1
    
    if scores:
        return max(scores, key=scores.get)
    
    return "未分類"

def update_index(vault_dir: Path):
    target_dir = vault_dir / "docs_obsidian/10_Notes/Personal"
    index_file = target_dir / "つれづれメモ.md"
    
    # マーカー定義
    START_MARKER = "<!-- INDEX_START -->"
    END_MARKER = "<!-- INDEX_END -->"
    
    if not target_dir.exists():
        print(f"Error: Directory {target_dir} not found.")
        return

    if not index_file.exists():
        print(f"Error: {index_file} not found.")
        return

    # ファイル一覧取得とカテゴリ分類
    files = sorted([f for f in target_dir.glob("*.md") if f.name != index_file.name])
    
    categorized_files = defaultdict(list)
    
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
            tags = extract_tags(content)
            
            if tags:
                category = categorize_by_tags(tags)
            else:
                # タグがない場合は内容から推測
                category = infer_category_from_content(f, content)
            
            categorized_files[category].append(f)
        except Exception as e:
            print(f"Warning: Could not process {f.name}: {e}")
            categorized_files["エラー"].append(f)
    
    # Index生成
    index_lines = []
    for category in sorted(categorized_files.keys()):
        index_lines.append(f"### {category}\n")
        for f in sorted(categorized_files[category]):
            title = f.stem
            link = f"- [{title}]({f.name})"
            index_lines.append(link)
        index_lines.append("")
    
    index_content = "\n".join(index_lines)
    new_section = f"{START_MARKER}\n\n## Index\n\n{index_content}{END_MARKER}"
    
    # ファイル読み込み
    try:
        content = index_file.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # マーカーが存在するか確認して置換または追記
    if START_MARKER in content and END_MARKER in content:
        parts = content.split(START_MARKER)
        pre = parts[0]
        remainder = parts[1]
        if END_MARKER in remainder:
            post = remainder.split(END_MARKER, 1)[1]
            new_content = pre + new_section + post
        else:
            print("Error: Markers are corrupted.")
            return
    else:
        lines = content.splitlines()
        last_tags_index = -1
        for i, line in enumerate(lines):
            if line.strip().startswith("tags:"):
                last_tags_index = i
                break
        
        if last_tags_index != -1:
            lines.insert(last_tags_index, "")
            lines.insert(last_tags_index, new_section)
            new_content = "\n".join(lines)
        else:
            new_content = content + "\n\n" + new_section + "\n"

    # 書き込み
    try:
        index_file.write_text(new_content, encoding="utf-8")
        print(f"Successfully updated index in {index_file}")
        print(f"Categories: {', '.join(sorted(categorized_files.keys()))}")
    except Exception as e:
        print(f"Error writing file: {e}")

def main():
    parser = argparse.ArgumentParser(description="Update Obsidian Personal Index")
    parser.add_argument("--vault-dir", required=True, help="Path to the workspace root containing docs_obsidian")
    args = parser.parse_args()
    
    vault_dir = Path(args.vault_dir).resolve()
    update_index(vault_dir)

if __name__ == "__main__":
    main()
