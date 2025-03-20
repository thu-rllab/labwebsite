import json 

class Pub2HTML:
    
    def __init__(self):
        self.all_pubs = {}

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
 

if __name__ == "__main__":

    pub2html = Pub2HTML()
    pub2html.wang_to_json()