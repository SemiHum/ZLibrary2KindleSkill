"""Tests for zlibrary_service.py — parsing helpers and data structures."""

import pytest

from src.services.zlibrary_service import ZLibraryService


class TestParseLabel:
    """Test _parse_label helper method."""

    def test_parse_label_year_found(self):
        text = "书名\n作者\n年: 2021\n语言: en\n文件: EPUB, 2.1 MB"
        year = ZLibraryService._parse_label(text, "年:")
        assert year == "2021"

    def test_parse_label_year_not_found(self):
        text = "书名\n作者\n语言: en\n文件: EPUB, 2.1 MB"
        year = ZLibraryService._parse_label(text, "年:")
        assert year == ""

    def test_parse_label_language_found(self):
        text = "书名\n作者\n年: 2021\n语言: zh\n文件: EPUB, 2.1 MB"
        lang = ZLibraryService._parse_label(text, "语言:")
        assert lang == "zh"

    def test_parse_label_file_info_found(self):
        text = "书名\n作者\n年: 2021\n语言: en\n文件: EPUB, 2.1 MB"
        file_info = ZLibraryService._parse_label(text, "文件:")
        assert file_info == "EPUB, 2.1 MB"


class TestParseFileInfo:
    """Test _parse_file_info helper method."""

    def test_parse_file_info_epub(self):
        format_, size = ZLibraryService._parse_file_info("EPUB, 2.1 MB")
        assert format_ == "EPUB"
        assert size == "2.1 MB"

    def test_parse_file_info_pdf(self):
        format_, size = ZLibraryService._parse_file_info("PDF, 5.4 MB")
        assert format_ == "PDF"
        assert size == "5.4 MB"

    def test_parse_file_info_mobi(self):
        format_, size = ZLibraryService._parse_file_info("MOBI, 1.0 MB")
        assert format_ == "MOBI"
        assert size == "1.0 MB"

    def test_parse_file_info_no_match(self):
        format_, size = ZLibraryService._parse_file_info("unknown format")
        assert format_ == "unknown"
        assert size == ""
