"""Web ページの自動スクリーンショット取得モジュール

Playwright (headless Chromium) を使い、Web ビューア上のスライド/ページを
自動でスクショ保存する。外部 API は一切使わずローカルで完結する。
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from pathlib import Path

from common import setup_logger

logger = setup_logger(__name__)

DEFAULT_WAIT_SEC = 2.0
DEFAULT_VIEWPORT_WIDTH = 1920
DEFAULT_VIEWPORT_HEIGHT = 1080
DEFAULT_MAX_PAGES = 100


@dataclass
class CaptureOptions:
    """キャプチャ設定"""

    prefix: str = "slide"
    wait_sec: float = DEFAULT_WAIT_SEC
    viewport_width: int = DEFAULT_VIEWPORT_WIDTH
    viewport_height: int = DEFAULT_VIEWPORT_HEIGHT
    selector: str | None = None
    scroll_capture: bool = False
    max_pages: int = DEFAULT_MAX_PAGES


def capture_full_page(
    url: str,
    output_dir: Path,
    opts: CaptureOptions | None = None,
) -> list[Path]:
    """URL にアクセスし、ページ全体または指定要素のスクショを取得する

    Args:
        url: スクショ対象の URL
        output_dir: スクショ保存先ディレクトリ
        opts: キャプチャ設定 (None の場合はデフォルト値)

    Returns:
        保存されたスクショファイルパスのリスト
    """
    try:
        from playwright.sync_api import sync_playwright  # noqa: PLC0415
    except ImportError as exc:
        sys.stderr.write(
            "playwright がインストールされていません。\n"
            "`uv add playwright && playwright install chromium` を実行してください。\n"
        )
        raise SystemExit(1) from exc

    if opts is None:
        opts = CaptureOptions()

    output_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": opts.viewport_width, "height": opts.viewport_height},
            locale="ja-JP",
        )
        page = context.new_page()

        logger.info("ページにアクセス: %s", url)
        sys.stderr.write(f"アクセス中: {url}\n")
        page.goto(url, wait_until="networkidle")
        time.sleep(opts.wait_sec)

        if opts.scroll_capture:
            saved = _scroll_and_capture(page, output_dir, opts.prefix, opts.wait_sec, opts.max_pages)
        elif opts.selector:
            saved = _capture_elements(page, output_dir, opts.prefix, opts.selector)
        else:
            path = output_dir / f"{opts.prefix}_01.png"
            page.screenshot(path=str(path), full_page=True)
            saved.append(path)
            logger.info("スクショ保存: %s", path.name)
            sys.stderr.write(f"保存: {path.name}\n")

        browser.close()

    logger.info("キャプチャ完了: %d 枚", len(saved))
    sys.stderr.write(f"キャプチャ完了: {len(saved)} 枚 -> {output_dir}\n")
    return saved


def _scroll_and_capture(
    page: object,
    output_dir: Path,
    prefix: str,
    wait_sec: float,
    max_pages: int,
) -> list[Path]:
    """ページをビューポート単位でスクロールしながらスクショを取る"""
    saved: list[Path] = []
    total_height = page.evaluate("document.body.scrollHeight")  # type: ignore[union-attr]
    viewport_height = page.evaluate("window.innerHeight")  # type: ignore[union-attr]
    current_y = 0
    idx = 1

    while current_y < total_height and idx <= max_pages:
        page.evaluate(f"window.scrollTo(0, {current_y})")  # type: ignore[union-attr]
        time.sleep(wait_sec)

        path = output_dir / f"{prefix}_{idx:02d}.png"
        page.screenshot(path=str(path))  # type: ignore[union-attr]
        saved.append(path)
        sys.stderr.write(f"[{idx}] 保存: {path.name} (y={current_y})\n")

        current_y += viewport_height
        idx += 1

    return saved


def _capture_elements(
    page: object,
    output_dir: Path,
    prefix: str,
    selector: str,
) -> list[Path]:
    """CSS セレクタにマッチする要素ごとにスクショを取る"""
    saved: list[Path] = []
    elements = page.query_selector_all(selector)  # type: ignore[union-attr]

    if not elements:
        sys.stderr.write(f"セレクタ '{selector}' にマッチする要素が見つかりません\n")
        return saved

    for idx, element in enumerate(elements, start=1):
        path = output_dir / f"{prefix}_{idx:02d}.png"
        element.screenshot(path=str(path))
        saved.append(path)
        sys.stderr.write(f"[{idx}/{len(elements)}] 保存: {path.name}\n")

    return saved
