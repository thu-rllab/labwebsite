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


class Pub2HTML:
    """实验室网站 HTML 生成器：从 JSON 数据生成学术风格的网页内容。"""

    # ── 成员分类排序权重 ──
    MEMBER_ORDER = {
        "Faculty": 0,
        "Postdoc": 1,
        "Graduate Student": 2,
        "Undergraduate": 3,
        "Alumni": 4,
    }

    # ── 学位 → badge 样式映射 ──
    DEGREE_STYLE_MAP = {
        "associate professor": ("badge badge-warning", ""),
        "postdoctoral fellow": ("badge badge-info", ""),
        "ph.d. student": ("badge badge-primary", "background-color:#007bff"),
        "master student": ("badge badge-success", ""),
        "undergraduate student": ("badge badge-secondary", ""),
        "ph.d. student (graduated)": ("badge badge-light", "background-color:#adb5bd; color:#fff"),
    }

    def __init__(self):
        self.pub_path = "final_all_papers.json"
        self.member_path = "final_all_members.json"
        self.news_path = "final_all_news.json"
        self.blog_path = "final_all_blogs.json"

        self.all_pubs = self._load_json(self.pub_path)
        self.all_members = self._load_json(self.member_path)

        self.all_news = self._load_json(self.news_path)
        self.all_news = sorted(self.all_news, key=lambda x: x["date"], reverse=True)

        self.all_blogs = self._load_json(self.blog_path)
        self.all_blogs = sorted(self.all_blogs, key=lambda x: x["date"], reverse=True)

    # ──────────────────── 工具方法 ────────────────────

    @staticmethod
    def _load_json(path):
        with open(path, "r", encoding="utf-8") as fp:
            return json.load(fp)

    @staticmethod
    def _format_date(date_str):
        """将 '20250709' 解析为 (month_abbr, day, year)"""
        d = datetime.strptime(date_str, "%Y%m%d")
        return d.strftime("%b"), str(d.day), str(d.year)

    @staticmethod
    def _link_btn(url, label, css_class="btn btn-outline-secondary btn-sm"):
        """仅在 url 有效时生成按钮 HTML。"""
        if not url or url == "nan":
            return ""
        return f'<a href="{url.strip()}" class="{css_class}" target="_blank">{label}</a>\n'

    def update_copy_new_new(self, src_path, backup_path, start_label, end_label, update_html):
        with open(src_path, "r", encoding="utf-8") as fp:
            all_source_html = fp.read()
        with open(backup_path, "w", encoding="utf-8") as fp:
            fp.write(all_source_html)
        start_index = all_source_html.index(start_label)
        end_index = all_source_html.index(end_label)
        to_be_replace = all_source_html[start_index:end_index]
        all_source_html = all_source_html.replace(to_be_replace, update_html)
        with open(src_path, "w", encoding="utf-8") as fp:
            fp.write(all_source_html)

    # ──────────────────── 筛选器 ────────────────────

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

    def get_filter_html(self, id_name, show_name, filter_values):
        options = "\n".join(
            f'          <option value="{v}">{v}</option>' for v in filter_values
        )
        return f"""
      <div class="tech-dropdown-container" style="margin-bottom:1.5%;">
        <select id="{id_name}FilterDropdown" class="tech-dropdown-select">
          <option value="">All {show_name}s</option>
{options}
        </select>
      </div>"""

    # ──────────────────── 旧 HTML → JSON (保留) ────────────────────

    def wang_to_json(self):
        with open("wang_html_publications.txt", "r", encoding="utf-8") as fp:
            all_lines = fp.readlines()

        def get_link(s):
            first_i = s.index('"')
            second_i = s[first_i + 1 :].index('"')
            return s[first_i + 1 : first_i + 1 + second_i]

        index, total_papers = 0, 0
        while index < len(all_lines):
            if '<div class="card">' in all_lines[index]:
                index += 1
                assert '<div class="card-body">' in all_lines[index]
                index += 1
                assert '<h5 class="card-title">' in all_lines[index]
                index += 1
                cur_title = all_lines[index].strip()
                index += 1
                assert '<span class="badge badge-success">' in all_lines[index]
                cur_conference = (
                    all_lines[index]
                    .replace('<span class="badge badge-success">', "")
                    .replace("</span>", "")
                    .strip()
                )
                cur_year = cur_conference.split(" ")[-1].strip()
                index += 1
                assert "</h5>" in all_lines[index]
                index += 1
                assert '<p class="card-text">' in all_lines[index]
                ci = all_lines[index].index("</strong>")
                cur_authors = (
                    all_lines[index][ci:]
                    .replace("</strong>", "")
                    .replace("</p>", "")
                    .strip()
                )
                index += 1
                cur_paper_link = get_link(all_lines[index]).strip(); index += 1
                cur_code_link = get_link(all_lines[index]).strip(); index += 1
                cur_demo_link = get_link(all_lines[index]).strip(); index += 1
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

    # ──────────────────── Publications HTML ────────────────────

    def paper_json_to_html(self):
        filter_year, filter_author, filter_conference, filter_tag = (
            self.get_all_filter_conditions()
        )

        all_filter_html = f"""
<!-- wby: 注意，切勿删除，程序代码识别publications开始部分 -->

    <div class="d-flex justify-content-between align-items-center mb-4" style="border-bottom:2px solid #3498db">
      <h2 class="wby-section-title" style="margin-bottom:1.5%;">Publications</h2>
{self.get_filter_html('year', 'Year', filter_year)}
{self.get_filter_html('author', 'Author', filter_author)}
{self.get_filter_html('tag', 'Tag', filter_tag)}
{self.get_filter_html('conference', 'Conferences/Journal', filter_conference)}
    </div>
"""

        # 按年份降序 → 会议名排序
        time_sorted = sorted(
            self.all_pubs.items(),
            key=lambda x: (-int(x[1][0]), x[1][1]),
        )

        cards = []
        for title, vals in time_sorted:
            year, conf, authors, paper_url, code_url, demo_url, tag = vals

            paper_btn = self._link_btn(paper_url, "Paper", "btn btn-outline-primary btn-sm")
            code_btn = self._link_btn(code_url, "Code", "btn btn-outline-success btn-sm")
            demo_btn = self._link_btn(demo_url, "Demo", "btn btn-outline-info btn-sm")
            tag_badge = (
                ""
                if tag == "nan"
                else f'<span class="badge badge-pill" style="background-color:#17a2b8;color:#fff;margin-left:.5em;vertical-align:middle;">{tag}</span>'
            )

            card = f"""
      <div class="card mb-3 pub-card" style="display:none;border-left:4px solid #3498db;"
           data-year="{year}" data-authors="{authors}" data-conference="{conf}" data-tag="{tag}">
        <div class="card-body">
          <div style="margin-bottom:.6em;">
            <span class="badge" style="background-color:#2c3e50;color:#fff;">{conf}</span>
            {tag_badge}
          </div>
          <h5 class="card-title" style="color:#2c3e50;font-size:1.05rem;"><strong>{title}</strong></h5>
          <p class="card-text" style="color:#555;font-size:.9rem;">
            {authors}
          </p>
          <div class="btn-group" role="group" style="margin-top:.5em;">
            {paper_btn}{code_btn}{demo_btn}
          </div>
        </div>
      </div>
"""
            cards.append(card)

        all_paper_html = """
    <div id="publicationsList">
""" + "".join(cards) + """
    </div>
"""

        self.update_copy_new_new(
            src_path="../new_new_index.html",
            backup_path="../new_new_backup.html",
            start_label="<!-- wby: 注意，切勿删除，程序代码识别publications开始部分 -->",
            end_label="<!-- wby: 注意，切勿删除，程序代码识别publications结束部分 -->",
            update_html=all_filter_html + "\n" + all_paper_html,
        )

    # ──────────────────── Team Members HTML ────────────────────

    def member_json_to_html(self):
        degree_filter = ["Associate Professor", "Postdoctoral Fellow", "Ph.D. Student", "Master Student", "Undergraduate Student"]
        degree_filter_html = self.get_filter_html("degree", "Position", degree_filter)

        all_filter_html = f"""
<!-- wby: 注意，切勿删除，程序代码识别team开始部分 -->

    <div class="d-flex justify-content-between align-items-center mb-4" style="border-bottom:2px solid #3498db">
      <h2 class="wby-section-title" style="margin-bottom:1.5%;">Team Members</h2>
{degree_filter_html}
    </div>
"""

        # 按 title 权重排序
        sorted_members = sorted(
            self.all_members.items(),
            key=lambda x: self.MEMBER_ORDER.get(x[1].get("title", ""), 99),
        )

        # 按类别分组
        current_title = None
        member_cards = []

        for name, info in sorted_members:
            title = info.get("title", "Graduate Student")
            degree = info["degree"]

            # 插入分组标题
            if title != current_title:
                current_title = title
                section_label = {
                    "Faculty": "Faculty",
                    "Postdoc": "Postdoctoral Researchers",
                    "Graduate Student": "Graduate Students",
                    "Undergraduate": "Undergraduate Students",
                    "Alumni": "Alumni",
                }.get(title, title)
                member_cards.append(f"""
      <div class="col-12 member-section-header" data-position="{degree}">
        <h4 style="color:#2c3e50;border-bottom:1px solid #e0e0e0;padding-bottom:.4em;margin-top:1.5em;margin-bottom:.8em;font-weight:600;">
          {section_label}
        </h4>
      </div>
""")

            # 头像路径
            if "xiangyang" in name.lower():
                img_path = "resources/people_img/ji.jpg"
            else:
                img_path = f"resources/people_img/{name}.jpg"

            # badge 样式
            degree_style, bg_color = self.DEGREE_STYLE_MAP.get(
                degree.lower(), ("badge badge-secondary", "")
            )
            bg_attr = f"background-color:{bg_color};" if bg_color else ""

            # 链接行
            links = []
            if info.get("website", "nan") != "nan":
                links.append(f'<a href="{info["website"]}" target="_blank" title="Homepage"><i class="fas fa-globe"></i></a>')
            if info.get("github", "nan") != "nan":
                links.append(f'<a href="{info["github"]}" target="_blank" title="GitHub"><i class="fab fa-github"></i></a>')
            if info.get("scholar", "nan") != "nan":
                links.append(f'<a href="{info["scholar"]}" target="_blank" title="Google Scholar"><i class="fas fa-graduation-cap"></i></a>')
            if info.get("email", "nan") != "nan":
                links.append(f'<a href="mailto:{info["email"]}" title="Email"><i class="fas fa-envelope"></i></a>')

            links_html = " &nbsp; ".join(links) if links else ""
            bio_html = f'<p class="card-text text-muted" style="font-size:.85rem;margin-top:.4em;">{info.get("bio","")}</p>' if info.get("bio") else ""

            member_cards.append(f"""
      <div class="col-md-6 col-lg-4 mb-4" style="display:none" data-position="{degree}">
        <div class="card h-100 member-card" style="border:none;box-shadow:0 2px 8px rgba(0,0,0,.08);transition:box-shadow .3s;">
          <div class="card-body text-center" style="padding:1.8rem 1.2rem;">
            <img src="{img_path}" alt="{name}"
                 style="width:100px;height:100px;object-fit:cover;border-radius:50%;margin-bottom:1rem;border:3px solid #f0f0f0;"
                 onerror="this.src='resources/people_img/default.jpg'">
            <h6 style="color:#2c3e50;font-weight:600;margin-bottom:.3em;">{name}</h6>
            <span class="{degree_style}" style="{bg_attr}font-size:.75rem;">{degree}</span>
            {bio_html}
            <div style="margin-top:.8em;font-size:1.1rem;" class="member-links">
              {links_html}
            </div>
          </div>
        </div>
      </div>
""")

        all_member_html = """
    <div id="teamList" class="row">
""" + "".join(member_cards) + """
    </div>
"""

        self.update_copy_new_new(
            src_path="../new_new_index.html",
            backup_path="../new_new_backup.html",
            start_label="<!-- wby: 注意，切勿删除，程序代码识别team开始部分 -->",
            end_label="<!-- wby: 注意，切勿删除，程序代码识别team结束部分 -->",
            update_html=all_filter_html + "\n" + all_member_html,
        )

    # ──────────────────── News HTML ────────────────────

    def news_json_to_html(self):
        year_set = sorted(
            {n["date"][:4] for n in self.all_news}, reverse=True
        )
        news_date_filter_html = self.get_filter_html("newsYear", "Year", year_set)

        all_filter_html = f"""
<!-- wby: 注意，切勿删除，程序代码识别news开始部分 -->

    <div class="d-flex justify-content-between align-items-center mb-4" style="border-bottom:2px solid #3498db">
      <h2 class="wby-section-title" style="margin-bottom:1.5%;">News</h2>
{news_date_filter_html}
    </div>
"""

        items = []
        for n in self.all_news:
            mon, day, year = self._format_date(n["date"])
            items.append(f"""
      <div class="news-item mb-3" style="display:none" data-year="{year}">
        <div class="news-item-body" style="display:flex;align-items:flex-start;">
          <div class="news-date" style="min-width:100px;font-weight:600;color:#3498db;font-size:.9rem;">{mon} {day}, {year}</div>
          <div class="news-text" style="flex:1;color:#444;font-size:.95rem;">{n["content"]}</div>
        </div>
      </div>
""")

        all_news_html = """
    <div id="newsList">
""" + "".join(items) + """
    </div>

    <div class="text-center mt-4">
      <button id="showMoreNewsBtn" class="btn btn-primary showMoreBtn">Show More</button>
      <div id="thatsAllNewsBtn" class="section-small-title" style="text-align:center;display:none">That's all news!</div>
      <div id="noNews" class="section-small-title" style="text-align:center;display:none">No news matching current filter.</div>
    </div>
    </div>
"""

        self.update_copy_new_new(
            src_path="../new_new_index.html",
            backup_path="../new_new_backup.html",
            start_label="<!-- wby: 注意，切勿删除，程序代码识别news开始部分 -->",
            end_label="<!-- wby: 注意，切勿删除，程序代码识别news结束部分 -->",
            update_html=all_filter_html + "\n" + all_news_html,
        )

    # ──────────────────── Blogs HTML ────────────────────

    def blog_json_to_html(self):
        year_set = sorted({b["date"][:4] for b in self.all_blogs}, reverse=True)
        blog_date_filter_html = self.get_filter_html("blogYear", "Year", year_set)

        all_filter_html = f"""
<!-- wby: 注意，切勿删除，程序代码识别blog开始部分 -->

    <div class="d-flex justify-content-between align-items-center mb-4" style="border-bottom:2px solid #3498db">
      <h2 class="wby-section-title" style="margin-bottom:1.5%;">Blogs</h2>
{blog_date_filter_html}
    </div>
"""

        items = []
        for b in self.all_blogs:
            mon, day, year = self._format_date(b["date"])
            cn_btn = self._link_btn(b.get("cn_link", "nan"), "中文", "btn btn-outline-secondary btn-sm")
            en_btn = self._link_btn(b.get("en_link", "nan"), "English", "btn btn-outline-secondary btn-sm")

            items.append(f"""
      <div class="blog-item mb-3" style="display:none" data-year="{year}">
        <div class="blog-item-body" style="display:flex;align-items:flex-start;">
          <div class="blog-date" style="min-width:100px;font-weight:600;color:#3498db;font-size:.9rem;">{mon} {day}, {year}</div>
          <div style="flex:1;">
            <div class="blog-text" style="color:#444;font-size:.95rem;">{b["content"]}</div>
            <div class="blog-links" style="margin-top:.5em;">
              {cn_btn}{en_btn}
            </div>
          </div>
        </div>
      </div>
""")

        all_blog_html = """
    <div id="blogList">
""" + "".join(items) + """
    </div>

    <div class="text-center mt-4">
      <button id="showMoreBlogsBtn" class="btn btn-primary showMoreBtn">Show More</button>
      <div id="thatsAllBlogsBtn" class="section-small-title" style="text-align:center;display:none">That's all blogs!</div>
      <div id="noBlogs" class="section-small-title" style="text-align:center;display:none">No blogs matching current filter.</div>
    </div>
    </div>
"""

        self.update_copy_new_new(
            src_path="../new_new_index.html",
            backup_path="../new_new_backup.html",
            start_label="<!-- wby: 注意，切勿删除，程序代码识别blog开始部分 -->",
            end_label="<!-- wby: 注意，切勿删除，程序代码识别blog结束部分 -->",
            update_html=all_filter_html + "\n" + all_blog_html,
        )

    # ──────────────────── Markdown → HTML ────────────────────

    def convert_markdown_to_html(self):
        """将 Markdown 博客文件转换为独立 HTML 页面。"""
        html_dir = os.path.join("..", "resources", "blogs", "html")
        img_dir = os.path.join("..", "resources", "blogs", "images")
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

            # 下载图片并替换链接
            for alt_text, img_url in md_img_pattern.findall(md_content):
                local_path = self.download_image(img_url, img_dir)
                if local_path:
                    md_content = md_content.replace(img_url, local_path)

            html_body = md_converter.convert(md_content)
            md_converter.reset()

            # 完整 HTML 页面模板
            full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{blog['content']}</title>
<style>
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; max-width: 860px; margin: 2rem auto; padding: 0 1.5rem; color: #333; line-height: 1.8; }}
  img {{ max-width: 100%; height: auto; border-radius: 6px; margin: 1em 0; }}
  h1,h2,h3 {{ color: #2c3e50; }}
  pre {{ background: #f6f8fa; padding: 1em; border-radius: 6px; overflow-x: auto; }}
  code {{ font-size: .9em; }}
  .highlight {{ background: #f6f8fa; }}
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

            # 更新博客链接指向 HTML
            blog["en_link"] = f"resources/blogs/html/{html_filename}"

        with open(self.blog_path, "w", encoding="utf-8") as f:
            json.dump(self.all_blogs, f, indent=4)

        print("Markdown → HTML conversion complete.")

    def download_image(self, img_url, img_dir):
        """下载远程图片到本地，返回相对路径。"""
        try:
            parsed = urlparse(unquote(img_url))
            filename = os.path.basename(parsed.path)
            if not filename or "." not in filename:
                filename = f"{uuid.uuid4().hex[:8]}.jpg"
            filename = re.sub(r"[^\w.\-]", "_", filename)
            local_path = os.path.join(img_dir, filename)
            relative_path = f"../images/{filename}"

            if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                return relative_path

            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            req = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp, open(local_path, "wb") as out:
                out.write(resp.read())

            if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
                return relative_path
        except Exception as e:
            print(f"Image download failed: {img_url} — {e}")
        return None


if __name__ == "__main__":
    pub = Pub2HTML()
    pub.convert_markdown_to_html()
    pub.news_json_to_html()
    pub.paper_json_to_html()
    pub.member_json_to_html()
    pub.blog_json_to_html()
    print("All sections generated successfully.")