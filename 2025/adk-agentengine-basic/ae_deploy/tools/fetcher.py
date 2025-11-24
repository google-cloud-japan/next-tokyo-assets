from typing import List
from trafilatura import extract, fetch_url
from trafilatura.settings import use_config

trafilatura_config = use_config()
trafilatura_config.set("DEFAULT", "EXTRACTION_TIMEOUT", "0")

def fetch_urls_content(urls: List[str]) -> str:
    """
    指定されたURLからコンテンツをフェッチするツール。

    Args:
        urls: コンテンツをフェッチするURLのリスト。

    Returns:
        各URLから取得したコンテンツをマージした文字列。
        失敗した場合は "コンテンツの取得に失敗しました。" を返却します。
    """
    contents = ""
    for url in urls:
        downloaded = fetch_url(url)
        result = extract(downloaded, output_format="markdown", with_metadata=True, config=trafilatura_config)
        if result is None:
            return "コンテンツの取得に失敗しました。"
        contents += result
    return contents