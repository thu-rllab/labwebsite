import json 

class Pub2HTML:
    
    def __init__(self):
        self.pub_path = 'final_all_papers.json'
        with open('final_all_papers.json', 'r') as fp: 
            self.all_pubs = json.load(fp)
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
        filter_author = [
            'Yixiu Mao',
            'Yun Qu',
            'Qi (Cheems) Wang',
            'Chen Chen',
            'Hongchang Zhang',
            'Boyuan Wang',
            'Shuncheng He',
            'Yuhang Jiang',
            'Jianzhun Shao',
            'Chang Liu', 
            'Xiangyang Ji'
        ] 
        return sorted(list(filter_year.keys()), reverse=True), sorted(filter_author), sorted(list(filter_conference.keys()))
    
    def get_filter_html(self, id_name, show_name, filter_values):
        option_value = ''
        for value in filter_values:
            option_value += f'          <option value="{value}">{value}</option>\n'
        filter_html = f"""
      <div style="margin-right: 1em">
        <label for="{id_name}FilterDropdown" class="form-label me-2" style="margin-right: 1em">{show_name}:</label>
        <select id="{id_name}FilterDropdown" class="form-select d-inline-block w-auto" style="margin-right: 1em">
          <option value="">All {show_name}s</option>
{option_value}
        </select>
      </div>
"""
        return filter_html

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
    <!-- wby: 增设筛选下拉框 -->
    <div class="d-flex justify-content-end align-items-center gap-3 mb-3">

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
          <a href=" {cur_paper_link} " class="btn btn-secondary btn-sm" target="_blank">Paper</a>
          <a href=" {cur_code_link} " class="btn btn-secondary btn-sm" target="_blank">Code</a>
          <a href=" {cur_demo_link} " class="btn btn-info btn-sm" target="_blank">Demo</a>
        </div>
      </div>

"""
            all_paper_html += html_template
        all_paper_html += """
    <!-- 这里可继续添加更多论文 ... -->
    </div>
"""
        ###    final step: 进行牛牛备案 以及 更新源网页   ###
        with open('../new_new_index.html', 'r') as fp:
            all_source_html = fp.read()
            fp.close()
        with open('../new_new_backup.html', 'w') as fp:
            fp.write(all_source_html)
            fp.close()
        start_index = all_source_html.index('<!-- wby: 增设筛选下拉框 -->')
        end_index = all_source_html.index('<!-- “Show All” 按钮 -->')
        to_be_replace = all_source_html[start_index:end_index]  
        all_source_html = all_source_html.replace(to_be_replace, all_filter_html + '\n\n' + all_paper_html)

        ### write to source html ###
        with open('../new_new_index.html', 'w') as fp:
            fp.write(all_source_html)
            fp.close()

if __name__ == "__main__":

    pub2html = Pub2HTML()
    # pub2html.wang_to_json()
    pub2html.json_to_html()