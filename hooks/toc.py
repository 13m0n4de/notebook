import logging
import os
import re
from pathlib import Path

import yaml
from jinja2 import Template
from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import Files
from mkdocs.structure.pages import Page
from utils.stats import get_statistics, get_update_time

enabled = os.getenv("TOC", "1") == "1" or os.getenv("FULL", "0") == "true"
logger = logging.getLogger("mkdocs.hooks.toc")

if enabled:
    logger.info("hook - toc is loaded and enabled")
else:
    logger.info("hook - toc is disabled")

HOOKS_DIR = Path(__file__).resolve().parent
TEMPLATE_PATH = HOOKS_DIR / "templates" / "toc.html"

TEMPLATE = TEMPLATE_PATH.read_text(encoding="utf-8")


def on_page_markdown(
    markdown: str, page: Page, config: MkDocsConfig, files: Files, **kwargs
) -> str:
    if not enabled:
        return markdown
    if "{{ BEGIN_TOC }}" not in markdown or "{{ END_TOC }}" not in markdown:
        return markdown

    if page.file.abs_src_path is None:
        return markdown
    base_dir = str(Path(page.file.abs_src_path).parent)

    toc_yaml = markdown.split("{{ BEGIN_TOC }}")[1].split("{{ END_TOC }}")[0]
    toc = yaml.load(toc_yaml, Loader=yaml.SafeLoader)
    toc_items = _get_toc_items(toc, base_dir)
    toc_html = Template(TEMPLATE).render(items=toc_items)
    markdown = re.sub(
        r"\{\{ BEGIN_TOC \}\}.*\{\{ END_TOC \}\}",
        toc_html,
        markdown,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return markdown


def _get_toc_items(toc: dict, base: str) -> list:
    ret = []
    for i, part in enumerate(toc):
        item = dict()
        item["n"] = i
        part_key = next(iter(part))
        title = part_key
        if "<!-- note -->" in title:
            item["note"] = True
            title = title.replace("<!-- note -->", "").strip()
        else:
            item["note"] = False
        item["title"] = title
        details = []
        for d in part[part_key]:
            key = next(iter(d))
            value = d[key]
            if key == "index":
                item["link"] = value
                continue
            detail = dict()
            t = key
            detail["note"] = False
            detail["lab"] = False
            if "<!-- note -->" in t:
                detail["note"] = True
                t = t.replace("<!-- note -->", "")
            if "<!-- lab -->" in t:
                detail["lab"] = True
                t = t.replace("<!-- lab -->", "")
            detail["title"] = t.strip()
            detail["link"] = value
            detail["words"], detail["codes"], detail["read_time"] = get_statistics(
                value, base
            )
            detail["update_time"] = get_update_time(value, base)
            details.append(detail)
        details.sort(key=lambda x: x["update_time"], reverse=True)
        item["contents"] = details
        ret.append(item)
    return ret
