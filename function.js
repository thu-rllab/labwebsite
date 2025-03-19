  document.addEventListener('DOMContentLoaded', function () {
    // wby: 根据id获得下拉框的元素
    const yearFilterDropdown = document.getElementById('yearFilterDropdown');
    const authorFilterDropdown = document.getElementById('authorFilterDropdown');
    // wby: 获得论文列表的元素
    const cardsContainer = document.getElementById('publicationsList');
    // wby: 获得展示更多的按钮
    const showMoreBtn = document.getElementById('showMoreBtn');
    // wby: 增加thats-all-button
    const thatsAllBtn = document.getElementById('thatsAllBtn');

    // 将所有 card 存入数组，方便后续操作
    const cards = Array.from(cardsContainer.querySelectorAll('.card'));

    // 初始只显示前多少条
    const itemsToShow = 1;

    // 筛选并排序的函数
    function filterAndSort() {
      // 获取下拉框的当前值
      // wby: 获得当前选中的值，如果什么都没有选，则为空值 ''
      const selectedYear = yearFilterDropdown.value.trim(); 
      const selectedAuthor = authorFilterDropdown.value.trim().toLowerCase();

      // 1. 根据下拉框的值进行过滤
      //    年份需要精确匹配，作者采用包含匹配
      let filteredCards = cards.filter(card => {
        // wby: card是cards数组中的元素，根据card进行筛选
        // wby: card.dataset中包含两个值，分别是year和authors，将其提取出来方便筛选
        const cardYear = card.dataset.year;                  // data-year
        const cardAuthors = card.dataset.authors.toLowerCase(); // data-authors
        
        // 注意这里和上面的selectedYear、selectedAuthor为空值对应上了
        // 当为空值时，筛选bool值自动设置为了true，也就是一开始不进行任何筛选
        //筛选条件是要么空、要么不为空时筛选值要匹配(cardYear === selectedYear)或包含(cardAuthors.includes(selectedAuthor))
        const matchYear = !selectedYear || cardYear === selectedYear;
        const matchAuthor = !selectedAuthor || cardAuthors.includes(selectedAuthor);

        return matchYear && matchAuthor;
      });

      // 2. 按年份 (data-year) 从大到小降序排序
      filteredCards.sort((a, b) => {
        return parseInt(b.dataset.year) - parseInt(a.dataset.year);
      });

      // 3. 先隐藏所有 card
      cards.forEach(card => {
        card.style.display = 'none';
      });

      // 4. 只显示过滤后前 10 条
      filteredCards.forEach((card, index) => {
        if (index < itemsToShow) {
          card.style.display = 'block';
        }
      });

      // 5. 如果过滤后结果超过 10 条，则显示“Show More”按钮，否则隐藏
      if (filteredCards.length > itemsToShow) {
        showMoreBtn.style.display = 'inline-block';
        thatsAllBtn.style.display = 'none';
      } else {
        showMoreBtn.style.display = 'none';
        thatsAllBtn.style.display = 'inline-block';
      }
    }

    // 当下拉框发生变化时，重新执行过滤+排序
    yearFilterDropdown.addEventListener('change', filterAndSort);
    authorFilterDropdown.addEventListener('change', filterAndSort);

    // 点击“Show More”时，显示当前筛选条件下的全部卡片
    showMoreBtn.addEventListener('click', function () {
      // 重新获取当前筛选条件
      const selectedYear = yearFilterDropdown.value.trim();
      const selectedAuthor = authorFilterDropdown.value.trim().toLowerCase();

      // 再次过滤
      let filteredCards = cards.filter(card => {
        const cardYear = card.dataset.year;
        const cardAuthors = card.dataset.authors.toLowerCase();
        const matchYear = !selectedYear || cardYear === selectedYear;
        const matchAuthor = !selectedAuthor || cardAuthors.includes(selectedAuthor);
        return matchYear && matchAuthor;
      });

      // 全部显示
      filteredCards.forEach(card => {
        card.style.display = 'block';
      });

      // 隐藏“Show More”按钮
      showMoreBtn.style.display = 'none';
      thatsAllBtn.style.display = 'inline-block';
    });

    // 页面加载后，默认先执行一次，保证初始状态下就有结果
    filterAndSort();
  }); 
