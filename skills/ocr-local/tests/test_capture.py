"""capture モジュールのテスト

Playwright の実際のブラウザ起動はテスト環境で重いため、
ユニットテストではモックを使う。
"""

from __future__ import annotations

import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import MagicMock, patch

from ocr_local.capture import CaptureOptions


def _setup_playwright_mock() -> tuple[MagicMock, MagicMock, MagicMock]:
    """Playwright モジュールのモックを構築し sys.modules に注入する"""
    mock_page = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page

    pw_instance = MagicMock()
    pw_instance.chromium.launch.return_value = mock_browser

    mock_sync_pw = MagicMock()
    mock_sync_pw.return_value.__enter__ = MagicMock(return_value=pw_instance)
    mock_sync_pw.return_value.__exit__ = MagicMock(return_value=False)

    mock_module = ModuleType("playwright.sync_api")
    mock_module.sync_playwright = mock_sync_pw  # type: ignore[attr-defined]

    return mock_page, mock_browser, mock_module


class TestCaptureFullPage:
    """capture_full_page 関数のテスト"""

    def test_single_page_capture(self, tmp_path: Path) -> None:
        """単一ページのスクショが保存される"""
        mock_page, _, mock_module = _setup_playwright_mock()

        with patch.dict(sys.modules, {"playwright.sync_api": mock_module, "playwright": MagicMock()}):
            from ocr_local.capture import capture_full_page  # noqa: PLC0415

            result = capture_full_page(
                url="https://example.com",
                output_dir=tmp_path,
                opts=CaptureOptions(wait_sec=0),
            )

        assert len(result) == 1
        assert result[0].name == "slide_01.png"
        mock_page.goto.assert_called_once()
        mock_page.screenshot.assert_called_once()

    def test_custom_prefix(self, tmp_path: Path) -> None:
        """カスタムプレフィックスが反映される"""
        _mock_page, _, mock_module = _setup_playwright_mock()

        with patch.dict(sys.modules, {"playwright.sync_api": mock_module, "playwright": MagicMock()}):
            from ocr_local.capture import capture_full_page  # noqa: PLC0415

            result = capture_full_page(
                url="https://example.com",
                output_dir=tmp_path,
                opts=CaptureOptions(prefix="page", wait_sec=0),
            )

        assert result[0].name == "page_01.png"

    def test_scroll_capture(self, tmp_path: Path) -> None:
        """スクロールキャプチャで複数枚取得される"""
        mock_page, _, mock_module = _setup_playwright_mock()
        mock_page.evaluate.side_effect = [2000, 500, None, None, None, None]

        with patch.dict(sys.modules, {"playwright.sync_api": mock_module, "playwright": MagicMock()}):
            from ocr_local.capture import capture_full_page  # noqa: PLC0415

            result = capture_full_page(
                url="https://example.com",
                output_dir=tmp_path,
                opts=CaptureOptions(scroll_capture=True, wait_sec=0),
            )

        expected_count = 4
        assert len(result) == expected_count

    def test_selector_capture(self, tmp_path: Path) -> None:
        """CSS セレクタで要素ごとにスクショが取れる"""
        mock_elem1 = MagicMock()
        mock_elem2 = MagicMock()
        mock_page, _, mock_module = _setup_playwright_mock()
        mock_page.query_selector_all.return_value = [mock_elem1, mock_elem2]

        with patch.dict(sys.modules, {"playwright.sync_api": mock_module, "playwright": MagicMock()}):
            from ocr_local.capture import capture_full_page  # noqa: PLC0415

            result = capture_full_page(
                url="https://example.com",
                output_dir=tmp_path,
                opts=CaptureOptions(selector=".slide", wait_sec=0),
            )

        expected_count = 2
        assert len(result) == expected_count
        mock_elem1.screenshot.assert_called_once()
        mock_elem2.screenshot.assert_called_once()

    def test_selector_no_match(self, tmp_path: Path) -> None:
        """セレクタにマッチしない場合は空リスト"""
        mock_page, _, mock_module = _setup_playwright_mock()
        mock_page.query_selector_all.return_value = []

        with patch.dict(sys.modules, {"playwright.sync_api": mock_module, "playwright": MagicMock()}):
            from ocr_local.capture import capture_full_page  # noqa: PLC0415

            result = capture_full_page(
                url="https://example.com",
                output_dir=tmp_path,
                opts=CaptureOptions(selector=".nonexistent", wait_sec=0),
            )

        assert result == []


class TestCaptureOptions:
    """CaptureOptions のテスト"""

    def test_defaults(self) -> None:
        from ocr_local.capture import DEFAULT_VIEWPORT_HEIGHT, DEFAULT_VIEWPORT_WIDTH  # noqa: PLC0415

        opts = CaptureOptions()
        assert opts.prefix == "slide"
        assert opts.scroll_capture is False
        assert opts.selector is None
        assert opts.viewport_width == DEFAULT_VIEWPORT_WIDTH
        assert opts.viewport_height == DEFAULT_VIEWPORT_HEIGHT

    def test_custom_values(self) -> None:
        opts = CaptureOptions(prefix="page", scroll_capture=True, selector=".main")
        assert opts.prefix == "page"
        assert opts.scroll_capture is True
        assert opts.selector == ".main"
