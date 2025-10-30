import re
import time
from pathlib import Path

from git import Repo

_git_repo = None


def get_repo() -> Repo:
    global _git_repo
    if _git_repo is None:
        _git_repo = Repo(Path(__file__).parent, search_parent_directories=True)
    return _git_repo


CHINESE_PATTERN = re.compile(r"[\u4e00-\u9fa5]")
ENGLISH_PATTERN = re.compile(r"[a-zA-Z0-9]*?(?![a-zA-Z0-9])")
CODE_BLOCK_PATTERN = re.compile(r"```[^\n].*?```", re.S)
COMMENT_PATTERN = re.compile(r"<!--.*?-->", re.DOTALL | re.MULTILINE)
CODE_BLOCK_SUB_PATTERN = re.compile(r"```[^\n].*?```", re.DOTALL | re.MULTILINE)
SPACES_PATTERN = re.compile(r"[ ]{2,}")
LINK_REF_PATTERN = re.compile(r"^\[[^]]*\][^(].*", re.MULTILINE)
ANCHOR_PATTERN = re.compile(r"{#.*}")
IMAGE_PATTERN = re.compile(r"!\[[^\]]*\]\([^)]*\)")
LINK_PATTERN = re.compile(r"\[([^\]]*)\]\([^)]*\)")
HTML_TAG_PATTERN = re.compile(r"</?[^>]*>")
SPECIAL_CHARS_PATTERN = re.compile(r"[#*`~\-–^=<>+|/:]")
FOOTNOTE_PATTERN = re.compile(r"\[[0-9]*\]")
NUMBER_DOT_PATTERN = re.compile(r"[0-9#]*\.")


def _words_count(markdown: str) -> tuple[int, int, int]:
    chinese, english, codes = _split_markdown(markdown)
    code_lines = 0
    words = len(chinese) + len(english.split())
    for code in codes:
        code_lines += len(code.splitlines()) - 2
    read_time = round(words / 300 + code_lines / 80)
    return words, code_lines, read_time


def _split_markdown(markdown: str) -> tuple[str, str, list]:
    markdown, codes = _clean_markdown(markdown)
    chinese = "".join(CHINESE_PATTERN.findall(markdown))
    english = " ".join(ENGLISH_PATTERN.findall(markdown))
    return chinese, english, codes


def _clean_markdown(markdown: str) -> tuple[str, list]:
    codes = CODE_BLOCK_PATTERN.findall(markdown)
    markdown = CODE_BLOCK_SUB_PATTERN.sub("", markdown)
    markdown = COMMENT_PATTERN.sub("", markdown)
    markdown = markdown.replace("\t", "    ")
    markdown = SPACES_PATTERN.sub("    ", markdown)
    markdown = LINK_REF_PATTERN.sub("", markdown)
    markdown = ANCHOR_PATTERN.sub("", markdown)
    markdown = markdown.replace("\n", " ")
    markdown = IMAGE_PATTERN.sub("", markdown)
    markdown = LINK_PATTERN.sub(r"\1", markdown)
    markdown = HTML_TAG_PATTERN.sub("", markdown)
    markdown = SPECIAL_CHARS_PATTERN.sub("", markdown)
    markdown = FOOTNOTE_PATTERN.sub("", markdown)
    markdown = NUMBER_DOT_PATTERN.sub("", markdown)
    return markdown, codes


def get_statistics(path: str, base: str) -> tuple[int, int, int]:
    words, codes, read_time = 0, 0, 0
    full_path = Path(base) / path

    if full_path.exists() and full_path.is_dir():
        # Directory: iterate all .md files
        for md_file in full_path.rglob("*.md"):
            markdown = md_file.read_text(encoding="utf-8")
            w, c, r = _words_count(markdown)
            words += w
            codes += c
            read_time += r
    else:
        # File: try with .md extension if needed
        if not full_path.exists():
            full_path = full_path.with_suffix(".md")

        if full_path.exists() and full_path.is_file():
            markdown = full_path.read_text(encoding="utf-8")
            words, codes, read_time = _words_count(markdown)

    return words, codes, read_time


def get_update_time(path: str, base: str) -> int:
    repo = get_repo()
    full_path = Path(base) / path

    # Try as-is first, then with .md extension if needed
    if not full_path.exists():
        full_path = full_path.with_suffix(".md")
        if not full_path.exists():
            return 0

    # Get path relative to repo root
    repo_root = Path(repo.working_dir)
    relative_path = full_path.resolve().relative_to(repo_root)

    if commit := next(repo.iter_commits(paths=str(relative_path), max_count=1), None):
        return int(commit.committed_date)

    return int(time.time())
