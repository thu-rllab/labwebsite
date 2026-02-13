import json
import os
import re
import uuid
import urllib.request
import subprocess
import markdown
from datetime import datetime
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from pymdownx.arithmatex import ArithmatexExtension
from urllib.parse import urlparse, unquote


# ── Venues that get the dark "venue-top" badge ──
TOP_VENUES = {
    'neurips', 'nips', 'icml', 'iclr', 'cvpr', 'iccv', 'eccv',
    'aaai', 'kdd', 'acl', 'emnlp', 'naacl', 'ijcai', 'colt',
    'aistats', 'uai', 'sigkdd', 'the innovation',
}


class Pub2HTML:
    """实验室网站 HTML 生成器：从 JSON 数据生成学术风格的网页内容。"""

    MEMBER_ORDER = {
        "Faculty":  0,
        "Students": 1,
        "Alumni":   2,
    }

    # Secondary sort within each group.
    # More-specific keys (longer suffixes) MUST come before their prefix to avoid
    # false prefix matches, e.g. "master student (graduated)" before "master student".
    DEGREE_SUB_ORDER = {
        "professor":                   0,
        "associate professor":          1,
        "postdoctoral fellow":          2,
        "ph.d. student (graduated)":   0,
        "master student (graduated)":  1,
        "ph.d. student":               3,
        "master student":              4,
        "undergraduate student":       5,
    }

    DEGREE_BADGE_MAP = {
        "professor":                    "badge-faculty",
        "associate professor":          "badge-faculty",
        "postdoctoral fellow":          "badge-postdoc",
        "ph.d. student (graduated)":    "badge-alumni",
        "master student (graduated)":   "badge-alumni",
        "ph.d. student":                "badge-phd",
        "master student":               "badge-master",
        "undergraduate student":        "badge-undergrad",
    }

    TITLE_SECTION_LABEL = {
        "Faculty":  "Faculty",
        "Students": "Students",
        "Alumni":   "Alumni",
    }

    def __init__(self):
        self.pub_path    = "final_all_papers.json"
        self.member_path = "final_all_members.json"
        self.news_path   = "final_all_news.json"
        self.blog_path   = "final_all_blogs.json"

        self.all_pubs    = self._load_json(self.pub_path)
        self.all_members = self._load_json(self.member_path)

        self.all_news  = sorted(self._load_json(self.news_path),  key=lambda x: x["date"], reverse=True)
        self.all_blogs = sorted(self._load_json(self.blog_path),  key=lambda x: x["date"], reverse=True)

    # ──────────────── Utilities ────────────────

    @staticmethod
    def _load_json(path):
        with open(path, "r", encoding="utf-8") as fp:
            return json.load(fp)

    @staticmethod
    def _format_date(date_str):
        d = datetime.strptime(date_str, "%Y%m%d")
        return d.strftime("%b"), str(d.day), str(d.year)

    @staticmethod
    def _venue_class(conf: str) -> str:
        """Map a venue string to a CSS badge class."""
        first_word = conf.split()[0].lower().rstrip('.,')
        if first_word in TOP_VENUES:
            return "venue-top"
        if "arxiv" in conf.lower() or "preprint" in conf.lower():
            return "venue-arxiv"
        return "venue-good"

    @staticmethod
    def _link_btn(url, label, css_class):
        if not url or url == "nan":
            return ""
        return f'<a href="{url.strip()}" class="{css_class}" target="_blank">{label}</a>\n'

    def _member_group(self, info):
        """Derive one of three display groups from a member's degree field."""
        degree = info.get("degree", "").lower()
        if "professor" in degree or "postdoc" in degree:
            return "Faculty"
        elif "graduated" in degree:
            return "Alumni"
        else:
            return "Students"

    def update_copy_new_new(self, src_path, backup_path, start_label, end_label, update_html):
        with open(src_path, "r", encoding="utf-8") as fp:
            content = fp.read()
        with open(backup_path, "w", encoding="utf-8") as fp:
            fp.write(content)
        start_i = content.index(start_label)
        end_i   = content.index(end_label)
        content = content.replace(content[start_i:end_i], update_html)
        with open(src_path, "w", encoding="utf-8") as fp:
            fp.write(content)

    # ──────────────── Filter HTML ────────────────

    def get_filter_html(self, id_name, show_name, filter_values):
        options = "\n".join(
            f'          <option value="{v}">{v}</option>' for v in filter_values
        )
        return f"""
      <select id="{id_name}FilterDropdown" class="filter-select">
          <option value="">All {show_name}s</option>
{options}
        </select>"""

    def get_all_filter_conditions(self):
        filter_year, filter_conference, filter_tag = {}, {}, {}
        for title, vals in self.all_pubs.items():
            cur_year, cur_conference, cur_authors, *_, cur_tag = vals
            filter_year[cur_year] = 0
            filter_conference[cur_conference.replace(cur_year, "").strip()] = 0
            if cur_tag != "nan":
                filter_tag[cur_tag] = 0
        filter_author = list(self.all_members.keys())
        return (
            sorted(filter_year.keys(), reverse=True),
            sorted(filter_author),
            sorted(filter_conference.keys()),
            sorted(filter_tag.keys()),
        )

    # ──────────────── Legacy: wang_to_json ────────────────

    def wang_to_json(self):
        with open("wang_html_publications.txt", "r", encoding="utf-8") as fp:
            all_lines = fp.readlines()

        def get_link(s):
            first_i  = s.index('"')
            second_i = s[first_i + 1:].index('"')
            return s[first_i + 1: first_i + 1 + second_i]

        index, total_papers = 0, 0
        while index < len(all_lines):
            if '<div class="card">' in all_lines[index]:
                index += 1
                assert '<div class="card-body">'   in all_lines[index]; index += 1
                assert '<h5 class="card-title">'   in all_lines[index]; index += 1
                cur_title = all_lines[index].strip(); index += 1
                assert '<span class="badge badge-success">' in all_lines[index]
                cur_conference = (all_lines[index]
                    .replace('<span class="badge badge-success">', "")
                    .replace("</span>", "").strip())
                cur_year = cur_conference.split(" ")[-1].strip(); index += 1
                assert "</h5>" in all_lines[index]; index += 1
                assert '<p class="card-text">' in all_lines[index]
                ci = all_lines[index].index("</strong>")
                cur_authors = (all_lines[index][ci:]
                    .replace("</strong>", "").replace("</p>", "").strip()); index += 1
                cur_paper_link = get_link(all_lines[index]).strip(); index += 1
                cur_code_link  = get_link(all_lines[index]).strip(); index += 1
                cur_demo_link  = get_link(all_lines[index]).strip(); index += 1
                assert "</div>" in all_lines[index]; index += 1
                assert "</div>" in all_lines[index]
                total_papers += 1
                if cur_title not in self.all_pubs:
                    self.all_pubs[cur_title] = [
                        cur_year, cur_conference, cur_authors,
                        cur_paper_link, cur_code_link, cur_demo_link,
                    ]
            index += 1
        print(f"A total of {total_papers} papers detected")
        with open("final_all_papers.json", "w", encoding="utf-8") as fp:
            json.dump(self.all_pubs, fp, indent=4)

    # ──────────────── Publications HTML ────────────────

    def paper_json_to_html(self):
        filter_year, filter_author, filter_conference, filter_tag = (
            self.get_all_filter_conditions()
        )

        filters_html = (
            self.get_filter_html("year",       "Year",               filter_year)
            + self.get_filter_html("author",     "Author",             filter_author)
            + self.get_filter_html("tag",        "Tag",                filter_tag)
            + self.get_filter_html("conference", "Conferences/Journal", filter_conference)
        )

        header_html = f"""
<!-- wby: 注意，切勿删除，程序代码识别publications开始部分 -->

    <div class="section-header">
      <h2 class="section-title">Publications</h2>
      <div class="section-filters">
        {filters_html}
      </div>
    </div>
"""

        # Sort: year descending, then conference name
        time_sorted = sorted(
            self.all_pubs.items(),
            key=lambda x: (-int(x[1][0]), x[1][1]),
        )

        cards = []
        for title, vals in time_sorted:
            year, conf, authors, paper_url, code_url, demo_url, tag = vals

            venue_cls = self._venue_class(conf)
            tag_badge = (
                ""
                if tag == "nan"
                else f'<span class="tag-badge">{tag}</span>'
            )

            paper_btn = self._link_btn(
                paper_url, '<i class="fas fa-file-pdf"></i> Paper', "pub-btn pub-btn-paper"
            )
            code_btn = self._link_btn(
                code_url, '<i class="fab fa-github"></i> Code', "pub-btn pub-btn-code"
            )
            demo_btn = self._link_btn(
                demo_url, '<i class="fas fa-play"></i> Project', "pub-btn pub-btn-demo"
            )

            cards.append(f"""
      <div class="card mb-3 pub-card" style="display:none"
           data-year="{year}" data-authors="{authors}" data-conference="{conf}" data-tag="{tag}">
        <div class="card-body">
          <div class="pub-venue-row">
            <span class="venue-badge {venue_cls}">{conf}</span>
            {tag_badge}
          </div>
          <div class="pub-title">{title}</div>
          <div class="pub-authors">{authors}</div>
          <div>
            {paper_btn}{code_btn}{demo_btn}
          </div>
        </div>
      </div>
""")

        pub_list_html = """
    <div id="publicationsList">
""" + "".join(cards) + """
    </div>
"""

        self.update_copy_new_new(
            src_path    = "../new_new_index.html",
            backup_path = "../new_new_backup.html",
            start_label = "<!-- wby: 注意，切勿删除，程序代码识别publications开始部分 -->",
            end_label   = "<!-- wby: 注意，切勿删除，程序代码识别publications结束部分 -->",
            update_html = header_html + pub_list_html,
        )

    # ──────────────── Team Members HTML ────────────────

    def member_json_to_html(self):
        header_html = """
<!-- wby: 注意，切勿删除，程序代码识别team开始部分 -->

    <div class="section-header">
      <h2 class="section-title">Team Members</h2>
    </div>
"""

        def _sub_order(info):
            deg = info.get("degree", "").lower()
            return next(
                (v for k, v in self.DEGREE_SUB_ORDER.items() if deg.startswith(k)),
                5,
            )

        sorted_members = sorted(
            self.all_members.items(),
            key=lambda x: (
                self.MEMBER_ORDER.get(self._member_group(x[1]), 99),
                _sub_order(x[1]),
            ),
        )

        current_group = None
        member_cards = []

        for name, info in sorted_members:
            group  = self._member_group(info)
            degree = info["degree"]

            # Section group header (no data-position — always visible)
            if group != current_group:
                current_group = group
                section_label = self.TITLE_SECTION_LABEL.get(group, group)
                member_cards.append(f"""
      <div class="col-12 member-section-header">
        <h4>{section_label}</h4>
      </div>
""")

            # Avatar path
            if "xiangyang" in name.lower():
                img_path = "resources/people_img/ji.jpg"
            else:
                img_path = f"resources/people_img/{name}.jpg"

            # Badge class — use prefix match to handle compound degrees like
            # "Associate Professor / Postdoctoral Fellow"
            deg_lower = degree.lower()
            badge_cls = next(
                (cls for key, cls in self.DEGREE_BADGE_MAP.items() if deg_lower.startswith(key)),
                "badge-alumni",
            )

            # Social links
            links = []
            if info.get("website", "nan") != "nan":
                links.append(f'<a href="{info["website"]}" target="_blank" title="Homepage"><i class="fas fa-globe"></i></a>')
            if info.get("github", "nan") != "nan":
                links.append(f'<a href="{info["github"]}" target="_blank" title="GitHub"><i class="fab fa-github"></i></a>')
            if info.get("scholar", "nan") != "nan":
                links.append(f'<a href="{info["scholar"]}" target="_blank" title="Google Scholar"><i class="fas fa-graduation-cap"></i></a>')
            if info.get("email", "nan") != "nan":
                links.append(f'<a href="mailto:{info["email"]}" title="Email"><i class="fas fa-envelope"></i></a>')
            links_html = "\n              ".join(links)

            bio_html = (
                f'<div class="member-bio">{info["bio"]}</div>'
                if info.get("bio") else ""
            )

            member_cards.append(f"""
      <div class="col-md-6 col-lg-4 mb-3" style="display:none;padding:.5rem;" data-position="{degree}">
        <div class="card h-100 member-card">
          <div class="card-body">
            <img src="{img_path}" alt="{name}"
                 class="member-avatar" onerror="this.onerror=null;this.src='resources/people_img/default.svg'">
            <div class="member-name">{name}</div>
            <span class="member-badge {badge_cls}">{degree}</span>
            {bio_html}
            <div class="member-links">
              {links_html}
            </div>
          </div>
        </div>
      </div>
""")

        team_list_html = """
    <div id="teamList" class="row" style="margin-left:-.5rem;margin-right:-.5rem;">
""" + "".join(member_cards) + """
    </div>
"""

        self.update_copy_new_new(
            src_path    = "../new_new_index.html",
            backup_path = "../new_new_backup.html",
            start_label = "<!-- wby: 注意，切勿删除，程序代码识别team开始部分 -->",
            end_label   = "<!-- wby: 注意，切勿删除，程序代码识别team结束部分 -->",
            update_html = header_html + team_list_html,
        )

    # ──────────────── News HTML ────────────────

    def news_json_to_html(self):
        year_set = sorted({n["date"][:4] for n in self.all_news}, reverse=True)
        news_filter_html = self.get_filter_html("newsYear", "Year", year_set)

        header_html = f"""
<!-- wby: 注意，切勿删除，程序代码识别news开始部分 -->

    <div class="section-header">
      <h2 class="section-title">News</h2>
      <div class="section-filters">
        {news_filter_html}
      </div>
    </div>
"""

        items = []
        for n in self.all_news:
            mon, day, year = self._format_date(n["date"])
            items.append(f"""
      <div class="news-item" style="display:none" data-year="{year}">
        <div class="news-item-body">
          <div class="news-date">{mon} {day}, {year}</div>
          <div class="news-text">{n["content"]}</div>
        </div>
      </div>
""")

        news_list_html = """
    <div id="newsList">
""" + "".join(items) + """
    </div>

    <div class="text-center mt-4">
      <button id="showMoreNewsBtn" class="btn show-more-btn">Show More</button>
      <div id="thatsAllNewsBtn" class="status-all" style="text-align:center;display:none">That's all news!</div>
      <div id="noNews" class="status-none" style="text-align:center;display:none">No news matching current filter.</div>
    </div>
"""

        self.update_copy_new_new(
            src_path    = "../new_new_index.html",
            backup_path = "../new_new_backup.html",
            start_label = "<!-- wby: 注意，切勿删除，程序代码识别news开始部分 -->",
            end_label   = "<!-- wby: 注意，切勿删除，程序代码识别news结束部分 -->",
            update_html = header_html + news_list_html,
        )

    # ──────────────── Blogs HTML ────────────────

    def blog_json_to_html(self):
        year_set = sorted({b["date"][:4] for b in self.all_blogs}, reverse=True)
        blog_filter_html = self.get_filter_html("blogYear", "Year", year_set)

        header_html = f"""
<!-- wby: 注意，切勿删除，程序代码识别blog开始部分 -->

    <div class="section-header">
      <h2 class="section-title">Blogs</h2>
      <div class="section-filters">
        {blog_filter_html}
      </div>
    </div>
"""

        items = []
        for b in self.all_blogs:
            mon, day, year = self._format_date(b["date"])
            cn_btn = self._link_btn(b.get("cn_link", "nan"), "中文",   "btn btn-sm")
            en_btn = self._link_btn(b.get("en_link", "nan"), "English", "btn btn-sm")

            items.append(f"""
      <div class="blog-item" style="display:none" data-year="{year}">
        <div class="blog-item-body">
          <div class="blog-date">{mon} {day}, {year}</div>
          <div style="flex:1;">
            <div class="blog-text">{b["content"]}</div>
            <div class="blog-links">
              {cn_btn}{en_btn}
            </div>
          </div>
        </div>
      </div>
""")

        blog_list_html = """
    <div id="blogList">
""" + "".join(items) + """
    </div>

    <div class="text-center mt-4">
      <button id="showMoreBlogsBtn" class="btn show-more-btn">Show More</button>
      <div id="thatsAllBlogsBtn" class="status-all" style="text-align:center;display:none">That's all blogs!</div>
      <div id="noBlogs" class="status-none" style="text-align:center;display:none">No blogs matching current filter.</div>
    </div>
"""

        self.update_copy_new_new(
            src_path    = "../new_new_index.html",
            backup_path = "../new_new_backup.html",
            start_label = "<!-- wby: 注意，切勿删除，程序代码识别blog开始部分 -->",
            end_label   = "<!-- wby: 注意，切勿删除，程序代码识别blog结束部分 -->",
            update_html = header_html + blog_list_html,
        )

    # ──────────────── Markdown → HTML ────────────────

    def convert_markdown_to_html(self):
        """Convert Markdown blog files to standalone HTML pages."""
        html_dir = os.path.join("..", "resources", "blogs", "html")
        img_dir  = os.path.join("..", "resources", "blogs", "images")
        for d in [html_dir, img_dir]:
            os.makedirs(d, exist_ok=True)

        extensions = [
            "markdown.extensions.tables",
            "markdown.extensions.fenced_code",
            "markdown.extensions.sane_lists",
            "markdown.extensions.attr_list",
            ExtraExtension(),
            CodeHiliteExtension(css_class="highlight"),
            ArithmatexExtension(generic=True),
        ]

        md_img_pattern = re.compile(r"!\[([\s\S]*?)\]\((https?://[^)]+)\)", re.DOTALL)

        for blog in self.all_blogs:
            en_link = blog.get("en_link", "")
            if not en_link.endswith(".md"):
                continue
            md_path = os.path.join("..", en_link)
            if not os.path.exists(md_path):
                continue

            with open(md_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            md_converter = markdown.Markdown(extensions=extensions, output_format="html5")

            for alt_text, img_url in md_img_pattern.findall(md_content):
                local_path = self.download_image(img_url, img_dir)
                if local_path:
                    md_content = md_content.replace(img_url, local_path)

            html_body = md_converter.convert(md_content)
            md_converter.reset()

            full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{blog['content']}</title>
<style>
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; max-width: 860px; margin: 2rem auto; padding: 0 1.5rem; color: #1e293b; line-height: 1.8; }}
  img {{ max-width: 100%; height: auto; border-radius: 8px; margin: 1em 0; }}
  h1,h2,h3 {{ color: #1e3a5f; }}
  pre {{ background: #f1f5f9; padding: 1em; border-radius: 8px; overflow-x: auto; }}
  code {{ font-size: .9em; }}
  .highlight {{ background: #f1f5f9; }}
</style>
<script>
  MathJax = {{ tex: {{ inlineMath: [['$','$'],['\\\\(','\\\\)']], displayMath: [['$$','$$'],['\\\\[','\\\\]']] }} }};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>
</head>
<body>
{html_body}
</body>
</html>"""

            html_filename = os.path.splitext(os.path.basename(en_link))[0] + ".html"
            html_path = os.path.join(html_dir, html_filename)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(full_html)

            blog["en_link"] = f"resources/blogs/html/{html_filename}"

        with open(self.blog_path, "w", encoding="utf-8") as f:
            json.dump(self.all_blogs, f, indent=4)

        print("Markdown → HTML conversion complete.")

    def download_image(self, img_url, img_dir):
        try:
            parsed   = urlparse(unquote(img_url))
            filename = os.path.basename(parsed.path)
            if not filename or "." not in filename:
                filename = f"{uuid.uuid4().hex[:8]}.jpg"
            filename   = re.sub(r"[^\w.\-]", "_", filename)
            local_path = os.path.join(img_dir, filename)
            rel_path   = f"../images/{filename}"

            if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                return rel_path

            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            req = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp, open(local_path, "wb") as out:
                out.write(resp.read())

            if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                return rel_path
        except Exception as e:
            print(f"Image download failed: {img_url} — {e}")
        return None


    # ──────────────── Hero Stats ────────────────

    def update_hero_stats(self):
        """Auto-update hero stat numbers in new_new_index.html."""
        # Publications: floor to nearest 5 and append '+'
        pub_total   = len(self.all_pubs)
        pub_display = f"{(pub_total // 5) * 5}+"

        # Active members: exclude anyone with "(Graduated)" in their degree
        active = sum(
            1 for info in self.all_members.values()
            if "graduated" not in info.get("degree", "").lower()
        )

        html_path = "../new_new_index.html"
        with open(html_path, "r", encoding="utf-8") as f:
            content = f.read()

        def _replace_stat(html, label, new_val):
            pattern = (
                r'(<div class="hero-stat-num">)[^<]+'
                r'(</div>\s*<div class="hero-stat-label">'
                + re.escape(label)
                + r'</div>)'
            )
            return re.sub(pattern, rf'\g<1>{new_val}\2', html)

        content = _replace_stat(content, "Publications",    pub_display)
        content = _replace_stat(content, "Current Members", active)

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"  Hero stats → {pub_display} papers | {active} members")


if __name__ == "__main__":
    pub = Pub2HTML()
    pub.convert_markdown_to_html()
    pub.news_json_to_html()
    pub.paper_json_to_html()
    pub.member_json_to_html()
    pub.blog_json_to_html()
    pub.update_hero_stats()
    print("All sections generated successfully.")
