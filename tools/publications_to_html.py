import json 
from datetime import datetime
import os    
import markdown
import os
import json
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from pymdownx.arithmatex import ArithmatexExtension

import re
import urllib.request
import os.path
import uuid
from urllib.parse import urlparse, unquote
class Pub2HTML:
    
    def __init__(self):

        self.pub_path = 'final_all_papers.json'
        self.member_path = 'final_all_members.json'
        self.news_path = 'final_all_news.json'
        self.blog_path = 'final_all_blogs.json'

        with open(self.pub_path, 'r') as fp: 
            self.all_pubs = json.load(fp)
            fp.close()
        with open(self.member_path, 'r') as fp: 
            self.all_members = json.load(fp)
            fp.close()
        with open(self.news_path, 'r') as fp: 
            self.all_news = json.load(fp)
            ### sort by date ### 
            self.all_news = sorted(self.all_news, key = lambda x: x['date'], reverse = True)  
            fp.close()

        with open(self.blog_path, 'r') as fp: 
            self.all_blogs = json.load(fp)
            ### 按日期排序 ### 
            self.all_blogs = sorted(self.all_blogs, key = lambda x: x['date'], reverse = True)  
            fp.close()

    def wang_to_json(self):
        with open('wang_html_publications.txt', 'r') as fp:
            all_lines = fp.readlines()
            fp.close() 

        def get_link(s):
            first_i = s.index('"')
            second_i = s[first_i + 1:].index('"')
            return s[first_i + 1:first_i + 1 + second_i]

        index = 0
        total_papers = 0
        while index < len(all_lines):
            if '<div class="card">' in all_lines[index]:
                ### now start a paper ### 
                index += 1
                assert '<div class="card-body">' in all_lines[index], all_lines[index] 
                index += 1
                assert '<h5 class="card-title">' in all_lines[index], all_lines[index] 
                index += 1
                ### now the title ###
                cur_title = all_lines[index].strip() 
                index += 1
                ### now the conference ### 
                assert '<span class="badge badge-success">' in all_lines[index] and '</span>' in all_lines[index], all_lines[index] 
                cur_conference = all_lines[index].replace('<span class="badge badge-success">', '').replace('</span>', '').strip() 
                cur_year = cur_conference.split(' ')[-1].strip()
                index += 1 
                assert '</h5>' in all_lines[index], all_lines[index] 
                index += 1
                assert '<p class="card-text">' in all_lines[index] and '</p>' in all_lines[index], all_lines[index] 
                cur_authors_start_index = all_lines[index].index('</strong>')
                cur_authors = all_lines[index][cur_authors_start_index:].replace('</strong>', '').replace('</p>', '').strip() 
                index += 1
                ### now the links ### 
                assert '<a href' in all_lines[index], all_lines[index] 
                cur_paper_link = get_link(all_lines[index]).strip() 
                index += 1
                assert '<a href' in all_lines[index], all_lines[index] 
                cur_code_link = get_link(all_lines[index]).strip() 
                index += 1
                assert '<a href' in all_lines[index], all_lines[index] 
                cur_demo_link = get_link(all_lines[index]).strip() 
                index += 1
                ### now the last two divs ### 
                assert '</div>' in all_lines[index], all_lines[index] 
                index += 1 
                assert '</div>' in all_lines[index], all_lines[index] 
                
                total_papers += 1

                if cur_title in self.all_pubs.keys():
                    print(f'... Paper {cur_title} Already Exist ...')
                else:
                    self.all_pubs[cur_title] = [
                        cur_year,
                        cur_conference,
                        cur_authors,
                        cur_paper_link,
                        cur_code_link,
                        cur_demo_link
                    ]  

            index += 1
        
        print(f'A total of {total_papers} papers detected')

        ### transfer them to json ###  
        with open('final_all_papers.json', 'w') as fp:
            json.dump(self.all_pubs, fp, indent=4)
            fp.close()
    
    def get_all_filter_conditions(self):
        ### now get all filter conditions ### 
        filter_year, filter_author, filter_conference, filter_tag = {}, {}, {}, {}
        for cur_title in self.all_pubs.keys():
            cur_year, cur_conference, cur_authors, cur_paper_link, cur_code_link, cur_demo_link, cur_tag = self.all_pubs[cur_title]
            filter_year[cur_year] = 0
            cur_authors = cur_authors.split(',')
            for cur_every_author in cur_authors:
                filter_author[cur_every_author.replace('*', '').strip()] = 0
            filter_conference[cur_conference.replace(cur_year, '').strip()] = 0
            if cur_tag != 'nan':
                filter_tag[cur_tag] = 0
        ### now get all filter conditions ###
        filter_author = list(self.all_members.keys()) 
        return sorted(list(filter_year.keys()), reverse=True), sorted(filter_author), sorted(list(filter_conference.keys())), sorted(list(filter_tag.keys()))
    
    def get_filter_html(self, id_name, show_name, filter_values):
        option_value = ''
        for value in filter_values:
            option_value += f'          <option value="{value}">{value}</option>\n'
        filter_html = f"""
      <div class="tech-dropdown-container" style="margin-bottom: 1.5%;"> 
        <select id="{id_name}FilterDropdown" class="tech-dropdown-select">
          <option value="">All {show_name}s</option>
{option_value}
        </select>
      </div>
"""
        return filter_html

    def update_copy_new_new(self, src_path, backup_path, start_label, end_label, update_html):
        ###    final step: 进行牛牛备案 以及 更新源网页   ###
        with open(src_path, 'r') as fp:
            all_source_html = fp.read()
            fp.close()
        with open(backup_path, 'w') as fp:
            fp.write(all_source_html)
            fp.close()
        start_index = all_source_html.index(start_label)
        end_index = all_source_html.index(end_label)
        to_be_replace = all_source_html[start_index:end_index]  
        all_source_html = all_source_html.replace(to_be_replace, update_html)

        ### write to source html ###
        with open(src_path, 'w') as fp:
            fp.write(all_source_html)
            fp.close()

    def paper_json_to_html(self):  
        ###    step 1: get all filter conditions    ###
        filter_year, filter_author, filter_conference, filter_tag = self.get_all_filter_conditions()
        print('year: ', filter_year)
        print('author: ', filter_author)
        print('conference: ', filter_conference)
        ###    step 2: get all paper filter html    ###
        year_filter_html = self.get_filter_html('year', 'Year', filter_year)
        author_filter_html = self.get_filter_html('author', 'Author', filter_author)
        conference_filter_html = self.get_filter_html('conference', 'Conferences/Journal', filter_conference)
        tag_filter_html = self.get_filter_html('tag', 'Tag', filter_tag)
        all_filter_html = f"""
<!-- wby: 注意，切勿删除，程序代码识别publications开始部分 -->

    <!-- 容器：让标题和下拉框在同一行 -->
    <div class="d-flex justify-content-between align-items-center mb-4" style="border-bottom: 2px solid #3498db">
      <h2 class="wby-section-title" style="margin-bottom: 1.5%;">Publications</h2> 
      <!-- 右侧的下拉框部分 -->
{year_filter_html}

{author_filter_html}

{tag_filter_html}

{conference_filter_html}
</div>
""" 
        ###    step 3: get all paper html   ####
        all_paper_html = """
    <!-- 论文列表容器 -->
    <div id="publicationsList">
"""
        time_sorted_papers = sorted(self.all_pubs.items(), key = lambda x: x[1][0], reverse=True) 
        for cur_title, cur_title_values in time_sorted_papers:
            cur_year, cur_conference, cur_authors, cur_paper_link, cur_code_link, cur_demo_link, cur_tag = cur_title_values

            ### if no paper/code/demo, then do not show ###
            cur_paper_link_html = '' if cur_paper_link == 'nan' else f'          <a href=" {cur_paper_link} " class="btn btn-secondary btn-sm" target="_blank">Paper</a>'
            cur_code_link_html = '' if cur_code_link == 'nan' else f'          <a href=" {cur_code_link} " class="btn btn-secondary btn-sm" target="_blank">Code</a>'
            cur_demo_link_html = '' if cur_demo_link == 'nan' else f'          <a href=" {cur_demo_link} " class="btn btn-secondary btn-sm" target="_blank">Demo</a>'
            cur_tag_html = '' if cur_tag == 'nan' else f'          <span class="badge badge-info" style="margin-bottom: 1em; margin-left: 0.5em; background-color: #17a2b8;">{cur_tag}</span>'
            html_template = f"""

      <div 
        class="card mb-3" style="display: none"
        data-year="{cur_year}" 
        data-authors="{cur_authors}"
        data-conference="{cur_conference}"
        data-tag="{cur_tag}"
      > 
        <div class="card-body">
          <span class="badge badge-success" style="margin-bottom: 1em">{cur_conference}</span>
          {cur_tag_html}
          <h5 class="card-title" style="color:#576263">
            <strong>{cur_title}</strong>
          </h5>
          <p class="card-text">
            <strong>Authors:</strong> {cur_authors}
          </p>
{cur_paper_link_html}
{cur_code_link_html}
{cur_demo_link_html}
        </div>
      </div>

"""
            all_paper_html += html_template
        all_paper_html += """
    <!-- 这里可继续添加更多论文 ... -->
    </div>
"""
        self.update_copy_new_new(src_path='../new_new_index.html', backup_path='../new_new_backup.html', 
                                 start_label='<!-- wby: 注意，切勿删除，程序代码识别publications开始部分 -->',
                                 end_label='<!-- wby: 注意，切勿删除，程序代码识别publications结束部分 -->',
                                 update_html=all_filter_html + '\n\n' + all_paper_html) 
    
    def member_json_to_html(self):
        ### first step: get all member filter conditions ### 
        all_degree_filter_conditions = ['Associate Professor', 'Postdoctoral Fellow', 'Doctor Student', 'Master Student']
        ### second step: get all filter html ### 
        degree_filter_html = self.get_filter_html('degree', 'Position', all_degree_filter_conditions)
        all_filter_html = f"""
<!-- wby: 注意，切勿删除，程序代码识别team开始部分 -->

    <!-- 容器：让标题和下拉框在同一行 -->
    <div class="d-flex justify-content-between align-items-center mb-4" style="border-bottom: 2px solid #3498db">
      <h2 class="wby-section-title" style="margin-bottom: 1.5%;">Team Members</h2>
      <!-- 右侧的下拉框部分 -->
{degree_filter_html} 
    </div>
"""     
        ### 程序性生成整个成员 ### 
        all_member_html = """
    <!-- 团队成员列表容器 -->
    <div id="teamList" class="row">
"""
        for member_name in self.all_members.keys():
            degree, website, github, email, scholar, member_name = self.all_members[member_name]['degree'],\
                                                        self.all_members[member_name]['website'],\
                                                        self.all_members[member_name]['github'],\
                                                        self.all_members[member_name]['email'],\
                                                        self.all_members[member_name]['scholar'],\
                                                        member_name
            
            
            ### for different people's img ###
            if 'xiangyang' in member_name.lower(): img_path = f'resources/people_img/ji.jpg'
            else:  img_path = f'resources/people_img/{member_name}.jpg'

            ### for different people's degree ###
            background_color = ''
            if 'associate professor' in degree.lower(): degree_style = 'badge badge-warning'
            elif 'professor' in degree.lower(): degree_style = 'badge badge-info'
            elif 'doctor' in degree.lower(): 
                degree_style = 'badge badge-primary'
                background_color = 'background-color: #007bff'
            else: degree_style = 'badge badge-success'

            ### for different people's website, email, google scholar ###
            if 'nan' in website: website_html = ''
            else: website_html = f"""
                            <strong>Website:</strong> 
                            <a href="{website}" target="_blank">view</a><br>
"""
            if 'nan' in github: github_html = ''
            else: github_html = f"""
                            <strong>Github:</strong> 
                            <a href="{github}" target="_blank">view</a><br>
"""
            if 'nan' in email: email_html = ''
            else: email_html = f"""
                            <strong>Email:</strong> {email}<br>
"""
            if 'nan' in scholar: scholar_html = ''
            else: scholar_html = f"""
                            <strong>Google Scholar:</strong> 
                            <a href="{scholar}" target="_blank">View</a>
"""
            ### set img margin top ### 
            # if '' in [website, email, scholar]: img_margin_top = 0
            # else: img_margin_top = 5

            member_template = f"""
      <div 
        class="col-md-6 mb-3" style="display: none"
        data-position="{degree}"  
      > 
      <div class="card h-100">
        <div class="card-body" style="display: table; width: 100%;">
            <!-- 一行(table-row)里分为两列(table-cell)：左侧放文字，右侧放图片 -->
            <div style="display: table-row;">
                <!-- 左侧文字内容，竖直居中 -->
                <div style="display: table-cell; vertical-align: middle;">
                    <span class="{degree_style}" style="margin-bottom: 1em;{background_color}">{degree}</span>
                    <div style="margin-left: 3%;">
                        <h5 class="card-title" style="color:#576263"><strong>{member_name}</strong></h5>
                        <p class="card-text">
{website_html}
{github_html}
{email_html}
{scholar_html}
                        </p>
                    </div>
                </div>
                """
            member_template+=f"""
                <!-- 右侧图片，竖直居中 -->
                <div style="display: table-cell; vertical-align: middle; width: 225px; text-align: center;">
                    <img src="{img_path}" alt="Profile Photo" style="width: 50%; height: 100%; object-fit: cover; border-radius: 8px">
                </div>
            """ if img_path !='nan' else """"""
            member_template+="""
            </div>
        </div>
      </div>
    </div>

""" 
            all_member_html += member_template
        all_member_html += """
    <!-- 这里可继续添加更多成员 ... -->
    </div>
""" 
        self.update_copy_new_new(src_path='../new_new_index.html', backup_path='../new_new_backup.html', 
                            start_label='<!-- wby: 注意，切勿删除，程序代码识别team开始部分 -->',
                            end_label='<!-- wby: 注意，切勿删除，程序代码识别team结束部分 -->',
                            update_html=all_filter_html + '\n\n' + all_member_html) 

    def news_json_to_html(self):
        ### first step: get all news date filter conditions ### 
        all_news_date_filter_conditions = {}
        for every_news in self.all_news:
            all_news_date_filter_conditions[every_news['date'][:4]] = 1 
        all_news_date_filter_conditions = sorted(list(all_news_date_filter_conditions.keys()), reverse=True)
        ### second step: get all filter html ### 
        news_date_filter_html = self.get_filter_html('newsYear', 'Year', all_news_date_filter_conditions)
        all_filter_html = f"""
<!-- wby: 注意，切勿删除，程序代码识别news开始部分 -->

    <!-- 容器：让标题和下拉框在同一行 -->
    <div class="d-flex justify-content-between align-items-center mb-4" style="border-bottom: 2px solid #3498db">
      <h2 class="wby-section-title" style="margin-bottom: 1.5%;">News</h2>
      <!-- 右侧的下拉框部分 -->
{news_date_filter_html} 
    </div>
"""
        ### third step: get all news html   ####
        all_news_html = """
    <!-- 新闻列表容器 -->
    <div id="newsList">
"""
        for every_news in self.all_news:
            cur_date, cur_content = every_news['date'], every_news['content']
            # 解析输入的日期字符串
            cur_date = datetime.strptime(cur_date, "%Y%m%d")
            # 格式化为需要的输出格式
            cur_month = cur_date.strftime("%b") 
            cur_day = str(cur_date.day) 
            cur_year = str(cur_date.year)  

            every_news_html_template = f"""
      <div 
        class="news-item mb-3" style="display: none"
        data-year="{cur_year}"  
      > 
        <div class="news-item-body">
            <div class="news-date">{cur_month} {cur_day}, {cur_year}</div>
            <div class="news-text">
                {cur_content}
            </div>
        </div>
      </div>

"""
            all_news_html += every_news_html_template
        all_news_html += """
    <!-- 这里可继续添加更多新闻 ... -->
    </div>
"""
        all_news_html += """
    <!-- 分页或"加载更多"按钮 -->
    <div class="text-center mt-4">
      <button id="showMoreNewsBtn" class="btn btn-primary showMoreBtn">Show More</button>
      <div id="thatsAllNewsBtn" class="section-small-title" style="text-align: center; display: none">That's all news!</div>
      <div id="noNews" class="section-small-title" style="text-align: center; display: none">No news matching current filter.</div>
    </div>
    </div>
"""
        self.update_copy_new_new(src_path='../new_new_index.html', backup_path='../new_new_backup.html', 
                            start_label='<!-- wby: 注意，切勿删除，程序代码识别news开始部分 -->',
                            end_label='<!-- wby: 注意，切勿删除，程序代码识别news结束部分 -->',
                            update_html=all_filter_html + '\n\n' + all_news_html) 
    
    def blog_json_to_html(self):
        ### 首先，加载博客数据文件
        self.blog_path = 'final_all_blogs.json'
        try:
            with open(self.blog_path, 'r') as fp: 
                self.all_blogs = json.load(fp)
                ### 按日期对博客排序 ### 
                self.all_blogs = sorted(self.all_blogs, key = lambda x: x['date'], reverse = True)  
                fp.close()
        except FileNotFoundError:
            self.all_blogs = []  # 如果文件不存在，初始化为空列表
            
        ### first step: 获取所有博客日期筛选条件 ### 
        all_blog_date_filter_conditions = {}
        for every_blog in self.all_blogs:
            # 按年份筛选
            all_blog_date_filter_conditions[every_blog['date'][:4]] = 1
        
        all_blog_date_filter_conditions = sorted(list(all_blog_date_filter_conditions.keys()), reverse=True)
        
        ### second step: 生成筛选条件的HTML ### 
        blog_date_filter_html = self.get_filter_html('blogYear', 'Year', all_blog_date_filter_conditions)
        
        all_filter_html = f"""
    <!-- wby: 注意，切勿删除，程序代码识别blog开始部分 -->

        <!-- 容器：让标题和下拉框在同一行 -->
        <div class="d-flex justify-content-between align-items-center mb-4" style="border-bottom: 2px solid #3498db">
        <h2 class="wby-section-title" style="margin-bottom: 1.5%;">Blogs</h2>
        <!-- 右侧的下拉框部分 -->
    {blog_date_filter_html} 
        </div>
    """
        
        ### third step: 生成所有博客的HTML ####
        all_blog_html = """
        <!-- 博客列表容器 -->
        <div id="blogList">
    """
        
        for every_blog in self.all_blogs:
            cur_date = every_blog['date']
            cur_content = every_blog['content']
            cur_cn_link = every_blog['cn_link']
            cur_en_link = every_blog['en_link']
            
            # 解析输入的日期字符串
            parsed_date = datetime.strptime(cur_date, "%Y%m%d")
            # 格式化为需要的输出格式
            cur_month = parsed_date.strftime("%b") 
            cur_day = str(parsed_date.day) 
            cur_year = str(parsed_date.year)
            
    #         # 简化的博客HTML模板，类似新闻项目的样式
    #         every_blog_html_template = f"""
    #     <div 
    #         class="blog-item mb-3" style="display: none"
    #         data-year="{cur_year}"  
    #     > 
    #         <div class="blog-item-body">
    #             <div class="blog-date">{cur_month} {cur_day}, {cur_year}</div>
    #             <div class="blog-text">
    #                 {cur_content}
    #             </div>
    #         </div>
    #     </div>
    # """
    #         all_blog_html += every_blog_html_template
            # 处理链接按钮 - 如果链接为"nan"则不显示对应按钮
            cn_link_html = '' if cur_cn_link == 'nan' else f'<a href="{cur_cn_link}" class="btn btn-secondary btn-sm" target="_blank" style="margin-right: 5px;">中文</a>'
            en_link_html = '' if cur_en_link == 'nan' else f'<a href="{cur_en_link}" class="btn btn-secondary btn-sm" target="_blank">English</a>'

            # 对英文链接的处理，无论是markdown还是html都通过博客查看器显示
            # en_link_html = ''
            # if cur_en_link != 'nan':
            #     # 统一使用blog-viewer.html来显示内容
            #     en_link_html = f'<a href="blog-viewer.html?path={cur_en_link}" class="btn btn-secondary btn-sm" target="_blank">English</a>'
            # 更新的博客HTML模板，包含链接按钮
            every_blog_html_template = f"""
        <div 
            class="blog-item mb-3" style="display: none"
            data-year="{cur_year}"  
        > 
            <div class="blog-item-body">
                <div class="blog-date">{cur_month} {cur_day}, {cur_year}</div>
                <div class="blog-text">
                    {cur_content}
                </div>
                <div class="blog-links" style="margin-top: 10px;">
                    {cn_link_html}{en_link_html}
                </div>
            </div>
        </div>
        """
            all_blog_html += every_blog_html_template
        
        all_blog_html += """
        </div>
    """
        all_blog_html += """
    <!-- 分页或"加载更多"按钮 -->
    <div class="text-center mt-4">
      <button id="showMoreBlogsBtn" class="btn btn-primary showMoreBtn">Show More</button>
      <div id="thatsAllBlogsBtn" class="section-small-title" style="text-align: center; display: none">That's all blogs!</div>
      <div id="noBlogs" class="section-small-title" style="text-align: center; display: none">No blogs matching current filter.</div>
    </div>
    </div>
"""
        
        # 更新HTML文件
        self.update_copy_new_new(src_path='../new_new_index.html', backup_path='../new_new_backup.html', 
                            start_label='<!-- wby: 注意，切勿删除，程序代码识别blog开始部分 -->',
                            end_label='<!-- wby: 注意，切勿删除，程序代码识别blog结束部分 -->',
                            update_html=all_filter_html + '\n\n' + all_blog_html)    

    def convert_markdown_to_html(self):
        """将Markdown文件转换为HTML文件，包括数学公式和图片支持，并下载图片到本地"""
        
        blogs_dir = os.path.join('..', 'resources', 'blogs')
        html_dir = os.path.join('..', 'resources', 'blogs', 'html')
        img_dir = os.path.join('..', 'resources', 'blogs', 'images')
        
        # 确保目录存在
        for directory in [html_dir, img_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        # 配置Markdown扩展
        # extensions = [
        #     'markdown.extensions.tables',
        #     'markdown.extensions.fenced_code',
        #     ExtraExtension(),
        #     CodeHiliteExtension(css_class='highlight'),
        #     ArithmatexExtension(generic=True)  # 用于LaTeX数学公式
        # ]
        extensions = [
            'markdown.extensions.tables',
            'markdown.extensions.fenced_code',
            'markdown.extensions.sane_lists',    # 处理混合符号列表
            'markdown.extensions.attr_list',     # 支持元素属性
            ExtraExtension(),
            CodeHiliteExtension(css_class='highlight'),
            ArithmatexExtension(generic=True)
        ]

        # 配置转换器
        md = markdown.Markdown(extensions=extensions)
        
        # 改进的图片链接正则表达式，支持多行文本
        md_img_pattern = re.compile(r'!\[([\s\S]*?)\]\((https?://[^)]+)\)', re.DOTALL)
        
        # 遍历博客列表，处理所有Markdown文件
        for blog in self.all_blogs:
            en_link = blog.get('en_link', '')
            if not en_link.endswith('.md'):
                continue
            if en_link.endswith('.md'):
                md_path = os.path.join('..', en_link)
                if os.path.exists(md_path):
                    # 读取Markdown内容
                    with open(md_path, 'r', encoding='utf-8') as f:
                        md_content = f.read()
                    md = markdown.Markdown(extensions=extensions, output_format='html5')
                    
                    # 找到所有图片链接
                    img_matches = md_img_pattern.findall(md_content)
                    print(f"找到 {len(img_matches)} 个图片链接")
                    
                    # 逐个处理图片
                    for alt_text, img_url in img_matches:
                        print(f"处理图片URL: {img_url}")
                        
                        # 下载图片到本地
                        local_path = self.download_image(img_url, img_dir)
                        
                        if local_path:
                            # 使用直接替换而不是正则表达式替换
                            # 这样可以避免alt_text中的特殊字符被解释为正则表达式
                            original_md = f'![{alt_text}]({img_url})'
                            new_md = f'![{alt_text}]({local_path})'
                            md_content = md_content.replace(original_md, new_md)
                            print(f'成功替换图片: {img_url} -> {local_path}')
                        else:
                            print(f'无法下载图片: {img_url}，保留原始链接')
                    
                    # 保存修改后的Markdown文件(可选，用于调试)
                    # debug_md_path = os.path.join(html_dir, os.path.basename(en_link) + '.debug')
                    # with open(debug_md_path, 'w', encoding='utf-8') as f:
                    #     f.write(md_content)
                    
                    # 转换为HTML
                    html_content = md.convert(md_content)
                    md.reset()
                    
                    # 创建完整的HTML文档，包含MathJax支持
                    html_doc = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>{blog.get('content', 'Blog Post')}</title>
        <link rel="stylesheet" href="../../css/bootstrap-flatly.min.css">
        
        <!-- 代码高亮样式 -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/github.min.css">
        
        <!-- MathJax支持 -->
        <script>
        MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
                processEscapes: true,
                processEnvironments: true
            }},
            options: {{
                skipHtmlTags: ['script', 'noscript', 'style', 'textarea', 'pre']
            }}
        }};
        </script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        
        <style>
            body {{
                font-family: 'Montserrat', sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f4f7f9;
                padding-top: 20px;
            }}
            .blog-content {{
                max-width: 800px;
                margin: 30px auto;
                padding: 40px;
                background: #fff;
                border-radius: 15px;
                box-shadow: 0 2px 15px rgba(0,0,0,0.1);
            }}
            .blog-content img {{
                max-width: 100%;
                height: auto;
                margin: 20px auto;
                display: block;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}
            h1, h2, h3, h4, h5, h6 {{
                color: #2c3e50;
                margin-top: 1.5em;
                margin-bottom: 0.8em;
            }}
            h1 {{
                font-size: 2.2em;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                font-size: 1.8em;
            }}
            a {{
                color: #3498db;
            }}
            pre {{
                background: #f8f9fa;
                border-radius: 5px;
                padding: 15px;
                overflow: auto;
            }}
            blockquote {{
                border-left: 4px solid #3498db;
                padding-left: 15px;
                color: #555;
                background: #f9f9f9;
                border-radius: 0 5px 5px 0;
            }}
            .back-btn {{
                margin: 20px auto;
                width: 800px;
            }}
            .highlight {{
                background: #f8f9fa;
                border-radius: 5px;
                padding: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="blog-content">
            {html_content}
        </div>
        
        <!-- 代码高亮 -->
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
        <script>hljs.highlightAll();</script>
    </body>
    </html>
    """
                    
                    # 生成HTML文件名
                    html_filename = os.path.basename(en_link).replace('.md', '.html')
                    html_path = os.path.join(html_dir, html_filename)
                    
                    # 保存HTML文件
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(html_doc)
                    
                    # 更新博客数据中的链接
                    blog['en_link'] = f"resources/blogs/html/{html_filename}"
        
        # 保存更新后的博客数据
        with open(self.blog_path, 'w', encoding='utf-8') as f:
            json.dump(self.all_blogs, f, indent=4)
        
        print(f"已成功将Markdown文件转换为HTML，下载图片到本地，并更新了博客数据")
    
    def download_image(self, img_url, img_dir):
        """专用图片下载函数，尝试多种下载方法"""
        try:
            # 从URL解析文件名
            parsed_url = urlparse(unquote(img_url))
            img_filename = os.path.basename(parsed_url.path)
            
            # 处理无效文件名
            if not img_filename or '.' not in img_filename:
                img_filename = f"{uuid.uuid4().hex[:8]}.jpg"
            
            # 确保文件名安全
            img_filename = re.sub(r'[^\w\.-]', '_', img_filename)
            
            # 本地保存路径
            local_img_path = os.path.join(img_dir, img_filename)
            relative_img_path = f"../images/{img_filename}"
            
            # 如果文件已存在，直接返回
            if os.path.exists(local_img_path) and os.path.getsize(local_img_path) > 0:
                print(f"图片已存在: {local_img_path}")
                return relative_img_path
            
            print(f"开始下载图片: {img_url}")
            
            # 方法1: 使用urllib
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Referer': 'https://mdnice.com/'
                }
                req = urllib.request.Request(img_url, headers=headers)
                with urllib.request.urlopen(req, timeout=15) as response, open(local_img_path, 'wb') as out_file:
                    out_file.write(response.read())
                
                if os.path.exists(local_img_path) and os.path.getsize(local_img_path) > 0:
                    print(f"urllib下载成功: {img_url}")
                    return relative_img_path
            except Exception as e:
                print(f"urllib下载失败: {e}")
            
            # 方法2: 使用wget命令
            try:
                print(f"尝试使用wget下载: {img_url}")
                subprocess.run([
                    'wget', 
                    '-O', local_img_path, 
                    img_url,
                    '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    '--timeout=30',
                    '--tries=3'
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if os.path.exists(local_img_path) and os.path.getsize(local_img_path) > 0:
                    print(f"wget下载成功: {img_url}")
                    return relative_img_path
            except Exception as e:
                print(f"wget下载失败: {e}")
            
            # 方法3: 使用curl命令
            try:
                print(f"尝试使用curl下载: {img_url}")
                subprocess.run([
                    'curl', 
                    '-o', local_img_path,
                    '-A', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    '-L', img_url,
                    '--max-time', '30'
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                if os.path.exists(local_img_path) and os.path.getsize(local_img_path) > 0:
                    print(f"curl下载成功: {img_url}")
                    return relative_img_path
            except Exception as e:
                print(f"curl下载失败: {e}")
            
            raise Exception("所有下载方法都失败")
            
        except Exception as e:
            print(f"图片下载完全失败: {img_url}, 错误: {e}")
            return None
if __name__ == "__main__":

    pub2html = Pub2HTML()
    pub2html.convert_markdown_to_html()  # 添加这一行
    # pub2html.wang_to_json()
    pub2html.news_json_to_html()
    pub2html.paper_json_to_html()
    pub2html.member_json_to_html()
    pub2html.blog_json_to_html()
