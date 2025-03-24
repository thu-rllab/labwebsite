import json 

class Pub2HTML:
    
    def __init__(self):
        self.pub_path = 'final_all_papers.json'
        self.member_path = 'final_all_members.json'
        with open(self.pub_path, 'r') as fp: 
            self.all_pubs = json.load(fp)
            fp.close()
        with open(self.member_path, 'r') as fp: 
            self.all_members = json.load(fp)
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
        filter_year, filter_author, filter_conference = {}, {}, {} 
        for cur_title in self.all_pubs.keys():
            cur_year, cur_conference, cur_authors, cur_paper_link, cur_code_link, cur_demo_link = self.all_pubs[cur_title]
            filter_year[cur_year] = 0
            cur_authors = cur_authors.split(',')
            for cur_every_author in cur_authors:
                filter_author[cur_every_author.replace('*', '').strip()] = 0
            filter_conference[cur_conference.replace(cur_year, '').strip()] = 0
        # filter_author = [
        #     'Yixiu Mao',
        #     'Yun Qu',
        #     'Qi (Cheems) Wang', 
        #     'Hongchang Zhang',
        #     'Boyuan Wang',
        #     'Shuncheng He',
        #     'Yuhang Jiang',
        #     'Jianzhun Shao',
        #     'Chang Liu', 
        #     'Mengge Liu' 
        # ] 
        filter_author = list(self.all_members.keys()) 
        return sorted(list(filter_year.keys()), reverse=True), sorted(filter_author), sorted(list(filter_conference.keys()))
    
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

    def json_to_html(self):  
        ###    step 1: get all filter conditions    ###
        filter_year, filter_author, filter_conference = self.get_all_filter_conditions()
        print('year: ', filter_year)
        print('author: ', filter_author)
        print('conference: ', filter_conference)
        ###    step 2: get all paper filter html    ###
        year_filter_html = self.get_filter_html('year', 'Year', filter_year)
        author_filter_html = self.get_filter_html('author', 'Author', filter_author)
        conference_filter_html = self.get_filter_html('conference', 'Conference', filter_conference)
        all_filter_html = f"""
<!-- wby: 注意，切勿删除，程序代码识别publications开始部分 -->

    <!-- 容器：让标题和下拉框在同一行 -->
    <div class="d-flex justify-content-between align-items-center mb-4" style="border-bottom: 2px solid #3498db">
      <h2 class="wby-section-title" style="margin-bottom: 1.5%;">Publications</h2> 
      <!-- 右侧的下拉框部分 -->
{year_filter_html}

{author_filter_html}

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
            cur_year, cur_conference, cur_authors, cur_paper_link, cur_code_link, cur_demo_link = cur_title_values

            ### if no paper/code/demo, then do not show ###
            cur_paper_link_html = '' if cur_paper_link == 'nan' else f'          <a href=" {cur_paper_link} " class="btn btn-secondary btn-sm" target="_blank">Paper</a>'
            cur_code_link_html = '' if cur_code_link == 'nan' else f'          <a href=" {cur_code_link} " class="btn btn-secondary btn-sm" target="_blank">Code</a>'
            cur_demo_link_html = '' if cur_demo_link == 'nan' else f'          <a href=" {cur_demo_link} " class="btn btn-secondary btn-sm" target="_blank">Demo</a>'

            html_template = f"""

      <div 
        class="card mb-3" style="display: none"
        data-year="{cur_year}" 
        data-authors="{cur_authors}"
        data-conference="{cur_conference}"
      > 
        <div class="card-body">
          <span class="badge badge-success" style="margin-bottom: 1em">{cur_conference}</span>
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
            degree, website, github, email, scholar, wechat = self.all_members[member_name]['degree'],\
                                                        self.all_members[member_name]['website'],\
                                                        self.all_members[member_name]['github'],\
                                                        self.all_members[member_name]['email'],\
                                                        self.all_members[member_name]['scholar'],\
                                                        self.all_members[member_name]['wechat']
            
            
            ### for different people's img ###
            if 'cheems' in member_name.lower(): img_path = f'resources/people_img/{wechat}.jfif'
            elif 'xiangyang' in member_name.lower(): img_path = f'resources/people_img/ji.jpg'
            else:  img_path = f'resources/people_img/{wechat}.jpg'

            ### for different people's wechat ###
            if 'xiangyang' in member_name.lower(): wechat_html = ""
            else: wechat_html = "" #f'<p style="margin-top: 5%"><strong>WeChat: </strong>{wechat}<p>'

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
        <div class="card-body" style="overflow: auto;">
            <!-- 让图片的父容器浮动到右侧 -->
            <div style="float: right; width: 200px; height: 100px; margin-left: 20px; text-align: center"> 
            <img src="{img_path}" alt="Profile Photo" style="width: 50%; height: 100%; object-fit: cover; border-radius: 8px">
            <br>
            {wechat_html}
            </div>
            <span class="{degree_style}" style="margin-bottom: 1em;{background_color}">{degree}</span>
            <h5 class="card-title" style="color:#576263"><strong>{member_name}</strong></h5>
            <p class="card-text">
{website_html}
{github_html}
{email_html}
{scholar_html}
            </p>
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

if __name__ == "__main__":

    pub2html = Pub2HTML()
    # pub2html.wang_to_json()
    pub2html.json_to_html()
    pub2html.member_json_to_html()