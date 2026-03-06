from common import setup_logger

logger = setup_logger(__name__)

def check_spec_file(content: str) -> list[str]:
    """
    仕様書（Markdown）の内容を簡易チェックし、問題点をリストで返します。
    
    Args:
        content (str): 仕様書の内容
        
    Returns:
        list[str]: 検出された問題点のリスト
    """
    issues = []
    
    if not content.strip():
        return ["仕様書が空です。"]
        
    required_sections = ["# 概要", "# 要件", "# 構成"]
    for section in required_sections:
        if section not in content:
            issues.append(f"必須セクション '{section}' が見つかりません。")
            
    logger.info(f"Spec check completed. Found {len(issues)} issues.")
    return issues
