  document.addEventListener('DOMContentLoaded', function () {
    // wby: 根据id获得下拉框的元素
    const yearFilterDropdown = document.getElementById('yearFilterDropdown');
    const authorFilterDropdown = document.getElementById('authorFilterDropdown');
    const conferenceFilterDropdown = document.getElementById('conferenceFilterDropdown');
    const degreeFilterDropdown = document.getElementById('degreeFilterDropdown');
    // wby: 获得论文列表的元素
    const cardsContainer = document.getElementById('publicationsList');
    const teamcardsContainer = document.getElementById('teamList');
    // wby: 获得展示更多的按钮
    const showMoreBtn = document.getElementById('showMoreBtn');
    // wby: 增加thats-all-button
    const thatsAllBtn = document.getElementById('thatsAllBtn');
    // wby: 增加noPapers提示
    const noPapersBtn = document.getElementById('noPapers');

    // 将所有 card 存入数组，方便后续操作
    const cards = Array.from(cardsContainer.querySelectorAll('.card'));
    const teamcards = Array.from(teamcardsContainer.querySelectorAll('.card'));

    // 初始只显示前多少条
    const itemsToShow = 5;
    
    // wby: 新增一个变量来控制是否显示全部论文
    let showAll = false; 

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
    degreeFilterDropdown.addEventListener('change', function() { 
      teamfilterAndSort();
    });

    // 点击“Show More”时，显示当前筛选条件下的全部卡片
    showMoreBtn.addEventListener('click', function () {
      // wby: 设置showAll为true进行全部展示 
      showAll = true; 
      filterAndSort();
    });

    // 页面加载后，默认先执行一次，保证初始状态下就有结果
    filterAndSort();
    teamfilterAndSort();
  }); 
