"""Check local files and HTML fragments in a built Sphinx site."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[tuple[str, bool]] = []

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if values.get("name") and tag == "a":
            self.ids.add(values["name"])

        if tag == "a" and values.get("href"):
            self.links.append((values["href"], True))
        elif tag in {"img", "script"} and values.get("src"):
            self.links.append((values["src"], False))
        elif tag == "link" and values.get("href"):
            self.links.append((values["href"], False))


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def resolve_target(site: Path, page: Path, target: str) -> Path:
    if target.startswith("/"):
        resolved = site / unquote(target.lstrip("/"))
    else:
        resolved = page.parent / unquote(target)
    if target.endswith("/"):
        resolved = resolved / "index.html"
    return resolved.resolve()


def main() -> None:
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("site", type=Path)
    args = argument_parser.parse_args()

    site = args.site.resolve()
    pages = sorted(site.rglob("*.html"))
    parsed = {page.resolve(): parse_page(page) for page in pages}
    problems: list[str] = []

    for page, page_data in parsed.items():
        for raw_link, check_fragment in page_data.links:
            split = urlsplit(raw_link)
            if split.scheme or split.netloc or raw_link.startswith(
                ("mailto:", "javascript:", "data:")
            ):
                continue

            target = resolve_target(site, page, split.path or page.name)
            if not target.exists():
                problems.append(
                    f"{page.relative_to(site)} -> missing {raw_link}"
                )
                continue

            if (
                check_fragment
                and split.fragment
                and target.suffix.lower() in {"", ".html"}
            ):
                target_page = target
                if target_page.is_dir():
                    target_page = target_page / "index.html"
                target_data = parsed.get(target_page.resolve())
                if target_data is None:
                    target_data = parse_page(target_page)
                fragment = unquote(split.fragment)
                if fragment not in target_data.ids:
                    problems.append(
                        f"{page.relative_to(site)} -> missing fragment "
                        f"{raw_link}"
                    )

    if problems:
        print("\n".join(problems))
        raise SystemExit(f"{len(problems)} local link problem(s) found.")

    print(
        f"Checked {len(pages)} HTML pages: "
        "all local files and fragments resolve."
    )


if __name__ == "__main__":
    main()
