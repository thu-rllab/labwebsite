  document.addEventListener('DOMContentLoaded', function () {
    // wby: 根据id获得下拉框的元素
    const yearFilterDropdown = document.getElementById('yearFilterDropdown');
    const authorFilterDropdown = document.getElementById('authorFilterDropdown');
    const conferenceFilterDropdown = document.getElementById('conferenceFilterDropdown');
    // for team members
    const degreeFilterDropdown = document.getElementById('degreeFilterDropdown');
    // for news-year
    const newsYearFilterDropdown = document.getElementById('newsYearFilterDropdown');
    const blogYearFilterDropdown = document.getElementById('blogYearFilterDropdown');
    
    // wby: 获得论文列表的元素
    const cardsContainer = document.getElementById('publicationsList');
    const teamcardsContainer = document.getElementById('teamList');
    const newsContainer = document.getElementById('newsList');
    const blogContainer = document.getElementById('blogList');
    // wby: 获得展示更多的按钮
    const showMoreBtn = document.getElementById('showMoreBtn');
    // wby: 增加thats-all-button
    const thatsAllBtn = document.getElementById('thatsAllBtn');
    // wby: 增加noPapers提示
    const noPapersBtn = document.getElementById('noPapers');

    // 将所有 card 存入数组，方便后续操作
    const cards = Array.from(cardsContainer.querySelectorAll('.card'));
    const teamcards = Array.from(teamcardsContainer.querySelectorAll('[data-position]'));
    const newscards = Array.from(newsContainer.querySelectorAll('[data-year]'));
    const blogItems = Array.from(blogContainer?.querySelectorAll('.blog-item') || []);
    
    // 点击"Show More News"时，显示当前筛选条件下的全部新闻
    const showMoreNewsBtn = document.getElementById('showMoreNewsBtn');
    if (showMoreNewsBtn) {
      showMoreNewsBtn.addEventListener('click', function () {
        showAllNews = true; 
        newsfilterAndSort();
      });
    }

    // 点击"Show More Blogs"时，显示当前筛选条件下的全部博客
    const showMoreBlogsBtn = document.getElementById('showMoreBlogsBtn');
    if (showMoreBlogsBtn) {
      showMoreBlogsBtn.addEventListener('click', function () {
        showAllBlogs = true; 
        blogFilterAndSort();
      });
    }

    // 初始只显示前多少条
    const itemsToShow = 5;  // 论文显示条数
    const newsToShow = 3;   // 新闻显示条数
    const blogsToShow = 3;  // 博客显示条数

    // 控制是否显示全部内容的变量
    let showAll = false;      // 控制论文显示
    let showAllNews = false;  // 控制新闻显示
    let showAllBlogs = false; // 控制博客显示

    // 筛选并排序的函数
    function filterAndSort() {
      // 获取下拉框的当前值
      // wby: 获得当前选中的值，如果什么都没有选，则为空值 ''
      const selectedYear = yearFilterDropdown.value.trim(); 
      const selectedAuthor = authorFilterDropdown.value.trim().toLowerCase();
      const selectedConference = conferenceFilterDropdown.value.trim().toLowerCase();

      // 1. 根据下拉框的值进行过滤
      //    年份需要精确匹配，作者采用包含匹配，会议也采用包含匹配的模式
      let filteredCards = cards.filter(card => {
        // wby: card是cards数组中的元素，根据card进行筛选
        // wby: card.dataset中包含两个值，分别是year和authors，将其提取出来方便筛选
        const cardYear = card.dataset.year;                  // data-year
        const cardAuthors = card.dataset.authors.toLowerCase(); // data-authors
        const cardConference = card.dataset.conference.toLowerCase(); // data-conference
        
        // 注意这里和上面的selectedYear、selectedAuthor为空值对应上了
        // 当为空值时，筛选bool值自动设置为了true，也就是一开始不进行任何筛选
        //筛选条件是要么空、要么不为空时筛选值要匹配(cardYear === selectedYear)或包含(cardAuthors.includes(selectedAuthor))
        const matchYear = !selectedYear || cardYear === selectedYear;
        let matchAuthor = false;
        if (selectedAuthor.includes('Qi (Cheems) Wang'.toLowerCase())) {
          matchAuthor = !selectedAuthor || cardAuthors.includes(selectedAuthor) || cardAuthors.includes('Qi Wang'.toLowerCase()) || cardAuthors.includes('Cheems Wang'.toLowerCase());
        }
        else { 
          matchAuthor = !selectedAuthor || cardAuthors.includes(selectedAuthor); 
        }
        const matchConference = !selectedConference || cardConference.includes(selectedConference);

        return matchYear && matchAuthor && matchConference;
      });

      // 2. 按年份 (data-year) 从大到小降序排序
      filteredCards = filteredCards.sort((a, b) => {
        return Number(b.dataset.year) - Number(a.dataset.year);
      });

      // 3. 先隐藏所有 card
      cards.forEach(card => {
        card.style.display = 'none';
      });

      // 4. 只显示过滤后前 10 条
      filteredCards.forEach((card, index) => {
        if (showAll || index < itemsToShow) {
          card.style.display = 'block';
        }
      });

      // 5. 如果过滤后结果超过 10 条，则显示“Show More”按钮，否则隐藏
      if (filteredCards.length == 0) {
        showMoreBtn.style.display = 'none';
        thatsAllBtn.style.display = 'none';
        noPapersBtn.style.display = 'block';
      }
      else if (!showAll && filteredCards.length > itemsToShow) {
        showMoreBtn.style.display = 'inline-block';
        // wby: add how many papers in total 
        showMoreBtn.textContent = String(itemsToShow) + " of " + String(filteredCards.length) + " Publications Displayed, Click to Show All";
        thatsAllBtn.style.display = 'none';
        noPapersBtn.style.display = 'none';
      } 
      else {
        showMoreBtn.style.display = 'none';
        thatsAllBtn.style.display = 'block';
        thatsAllBtn.textContent = "That's all " + String(filteredCards.length) + " publications under current filter conditions."
        noPapersBtn.style.display = 'none';
      }
    }
    
    // 筛选并排序的函数
    function teamfilterAndSort() { 
      const selectedDegree = degreeFilterDropdown.value.trim().toLowerCase();   

      let filteredCards = teamcards.filter(card => { 
        const cardDegree = card.dataset.position.toLowerCase();   

        let matchDegree = false;
        if (selectedDegree.includes('associate professor')) {
          matchDegree = !selectedDegree || cardDegree.includes(selectedDegree);
        }
        else if (selectedDegree.includes('professor')) {
          matchDegree = !selectedDegree || (cardDegree.includes(selectedDegree) && !cardDegree.includes('associate professor'));
        }
        else if (selectedDegree.includes('postdoctoral fellow')) {
          matchDegree = !selectedDegree || cardDegree.includes(selectedDegree);
        }
        else if (selectedDegree.includes('doctor')) {
          matchDegree = !selectedDegree || (cardDegree.includes(selectedDegree) && !cardDegree.includes('postdoctoral'));
        }
        else { 
          matchDegree = !selectedDegree || cardDegree.includes(selectedDegree);
        } 

        return matchDegree;
      }); 

      // 3. 先隐藏所有 card
      teamcards.forEach(card => {
        card.style.display = 'none';
      }); 

      filteredCards.forEach((card, index) => {
        card.style.display = 'block';
      }); 
    }


    // 重写新闻筛选函数，模仿 filterAndSort() 的结构
    function newsfilterAndSort() {
      // 获取下拉框的当前值
      const selectedNewsYear = newsYearFilterDropdown.value.trim();

      // 1. 根据下拉框的值进行过滤
      let filteredCards = newscards.filter(card => {
        const cardYear = card.dataset.year;
        // 年份需要精确匹配
        const matchYear = !selectedNewsYear || cardYear === selectedNewsYear;
        return matchYear;
      });

      // 2. 按年份从大到小降序排序
      filteredCards = filteredCards.sort((a, b) => {
        return Number(b.dataset.year) - Number(a.dataset.year);
      });

      // 3. 先隐藏所有新闻项目
      newscards.forEach(card => {
        card.style.display = 'none';
      });

      // 4. 只显示过滤后前 newsToShow 条
      filteredCards.forEach((card, index) => {
        if (showAllNews || index < newsToShow) {
          card.style.display = 'block';
        }
      });

      // 5. 控制"显示更多"和"全部显示"按钮的显示
      const newsMoreBtn = document.getElementById('showMoreNewsBtn');
      const thatsAllNewsBtn = document.getElementById('thatsAllNewsBtn');
      const noNewsBtn = document.getElementById('noNews');

      if (filteredCards.length == 0) {
        if (newsMoreBtn) newsMoreBtn.style.display = 'none';
        if (thatsAllNewsBtn) thatsAllNewsBtn.style.display = 'none';
        if (noNewsBtn) noNewsBtn.style.display = 'block';
      }
      else if (!showAllNews && filteredCards.length > newsToShow) {
        if (newsMoreBtn) {
          newsMoreBtn.style.display = 'inline-block';
          newsMoreBtn.textContent = `${newsToShow} of ${filteredCards.length} News Displayed, Click to Show All`;
        }
        if (thatsAllNewsBtn) thatsAllNewsBtn.style.display = 'none';
        if (noNewsBtn) noNewsBtn.style.display = 'none';
      } 
      else {
        if (newsMoreBtn) newsMoreBtn.style.display = 'none';
        if (thatsAllNewsBtn) {
          thatsAllNewsBtn.style.display = 'block';
          thatsAllNewsBtn.textContent = `That's all ${filteredCards.length} news items under current filter conditions.`;
        }
        if (noNewsBtn) noNewsBtn.style.display = 'none';
      }
    }

    // 重写博客筛选函数，模仿 filterAndSort() 的结构
    function blogFilterAndSort() {
      // 简单检查博客容器是否存在
      if (!blogContainer || !blogYearFilterDropdown) return;
      
      // 获取下拉框的当前值
      const selectedYear = blogYearFilterDropdown.value.trim();
      
      // 1. 根据下拉框的值进行过滤
      let filteredBlogs = blogItems.filter(item => { 
        if (!item.dataset || !item.dataset.year) return false;
        
        const itemYear = item.dataset.year;
        // 年份需要精确匹配
        return !selectedYear || itemYear === selectedYear;
      });
      
      // 2. 按年份从大到小降序排序
      filteredBlogs = filteredBlogs.sort((a, b) => {
        if (!a.dataset || !b.dataset) return 0;
        return Number(b.dataset.year) - Number(a.dataset.year);
      });
      
      // 3. 先隐藏所有博客项目
      blogItems.forEach(item => { 
        item.style.display = 'none';
      });
      
      // 4. 只显示过滤后前 blogsToShow 条
      filteredBlogs.forEach((item, index) => {
        if (showAllBlogs || index < blogsToShow) {
          item.style.display = 'block';
        }
      });
      
      // 5. 控制"显示更多"和"全部显示"按钮的显示
      const blogMoreBtn = document.getElementById('showMoreBlogsBtn');
      const thatsAllBlogsBtn = document.getElementById('thatsAllBlogsBtn');
      const noBlogsBtn = document.getElementById('noBlogs');
      
      if (filteredBlogs.length == 0) {
        if (blogMoreBtn) blogMoreBtn.style.display = 'none';
        if (thatsAllBlogsBtn) thatsAllBlogsBtn.style.display = 'none';
        if (noBlogsBtn) noBlogsBtn.style.display = 'block';
      }
      else if (!showAllBlogs && filteredBlogs.length > blogsToShow) {
        if (blogMoreBtn) {
          blogMoreBtn.style.display = 'inline-block';
          blogMoreBtn.textContent = `${blogsToShow} of ${filteredBlogs.length} Blogs Displayed, Click to Show All`;
        }
        if (thatsAllBlogsBtn) thatsAllBlogsBtn.style.display = 'none';
        if (noBlogsBtn) noBlogsBtn.style.display = 'none';
      } 
      else {
        if (blogMoreBtn) blogMoreBtn.style.display = 'none';
        if (thatsAllBlogsBtn) {
          thatsAllBlogsBtn.style.display = 'block';
          thatsAllBlogsBtn.textContent = `That's all ${filteredBlogs.length} blog posts under current filter conditions.`;
        }
        if (noBlogsBtn) noBlogsBtn.style.display = 'none';
      }
    }
    
    // 筛选新闻的函数
    // function newsfilterAndSort() { 
    //   const selectedNewsYear = newsYearFilterDropdown.value.trim();   

    //   let filteredCards = newscards.filter(card => { 
    //     const cardYear = card.dataset.year;   

    //     let matchYear = !selectedNewsYear || (cardYear == selectedNewsYear); 

    //     return matchYear;
    //   }); 

    //   // 3. 先隐藏所有 card
    //   newscards.forEach(card => {
    //     card.style.display = 'none';
    //   }); 

    //   filteredCards.forEach((card, index) => {
    //     card.style.display = 'block';
    //   }); 
    // }
  //   function blogFilterAndSort() {
  //     if (!blogContainer || !blogYearFilterDropdown) return;
      
  //     const selectedYear = blogYearFilterDropdown.value.trim();
      
  //     let filteredBlogs = blogItems.filter(item => { 
  //         if (!item.dataset || !item.dataset.year) return false;
          
  //         const itemYear = item.dataset.year;
  //         return !selectedYear || itemYear === selectedYear;
  //     });
      
  //     // 隐藏所有博客项目
  //     blogItems.forEach(item => { 
  //         item.style.display = 'none';
  //     });
      
  //     // 显示过滤后的所有博客
  //     filteredBlogs.forEach(item => {
  //         item.style.display = 'block';
  //     });
  // }


  // 当下拉框发生变化时，重新执行过滤+排序
    yearFilterDropdown.addEventListener('change', function() {
      // wby: 选择筛选条件后，回到默认的 10 条显示模式
      showAll = false; 
      filterAndSort();
    });
    authorFilterDropdown.addEventListener('change', function() {
      // wby: 选择筛选条件后，回到默认的 10 条显示模式
      showAll = false; 
      filterAndSort();
    });
    conferenceFilterDropdown.addEventListener('change', function() {
      // wby: 选择筛选条件后，回到默认的 10 条显示模式
      showAll = false; 
      filterAndSort();
    });
    // for team-members
    degreeFilterDropdown.addEventListener('change', function() { 
      teamfilterAndSort();
    });
    // for news
    newsYearFilterDropdown.addEventListener('change', function() { 
      newsfilterAndSort();
    });
    
    blogYearFilterDropdown.addEventListener('change', function() {
      blogFilterAndSort();
    });
    

    // 点击“Show More”时，显示当前筛选条件下的全部卡片
    showMoreBtn.addEventListener('click', function () {
      // wby: 设置showAll为true进行全部展示 
      showAll = true; 
      filterAndSort();
    });

    // for news
    newsYearFilterDropdown.addEventListener('change', function() { 
      showAllNews = false;  // 重置为默认显示模式
      newsfilterAndSort();
    });

    // for blogs
    blogYearFilterDropdown.addEventListener('change', function() {
      showAllBlogs = false;  // 重置为默认显示模式
      blogFilterAndSort();
    });

    // 页面加载后，默认先执行一次，保证初始状态下就有结果
    filterAndSort();
    teamfilterAndSort();
    newsfilterAndSort();
    blogFilterAndSort();
  }); 
