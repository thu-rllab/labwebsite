  document.addEventListener('DOMContentLoaded', function () {
    const yearFilterDropdown       = document.getElementById('yearFilterDropdown');
    const authorFilterDropdown     = document.getElementById('authorFilterDropdown');
    const conferenceFilterDropdown = document.getElementById('conferenceFilterDropdown');
    const tagFilterDropdown        = document.getElementById('tagFilterDropdown');
    const newsYearFilterDropdown   = document.getElementById('newsYearFilterDropdown');
    const blogYearFilterDropdown   = document.getElementById('blogYearFilterDropdown');

    const cardsContainer     = document.getElementById('publicationsList');
    const teamcardsContainer = document.getElementById('teamList');
    const newsContainer      = document.getElementById('newsList');
    const blogContainer      = document.getElementById('blogList');

    const cards     = Array.from(cardsContainer.querySelectorAll('.card'));
    const teamcards = Array.from(teamcardsContainer.querySelectorAll('[data-position]'));
    const newscards = Array.from(newsContainer.querySelectorAll('[data-year]'));
    const blogItems = Array.from(blogContainer?.querySelectorAll('.blog-item') || []);

    // Initial display limits
    const PUB_LIMIT  = 5;
    const NEWS_LIMIT = 3;
    const BLOG_LIMIT = 3;

    let showAllPubs  = false;
    let showAllNews  = false;
    let showAllBlogs = false;

    const noPapersBtn = document.getElementById('noPapers');
    const noNewsBtn   = document.getElementById('noNews');
    const noBlogsBtn  = document.getElementById('noBlogs');
    const showMoreBtn = document.getElementById('showMoreBtn');
    const thatsAllBtn = document.getElementById('thatsAllBtn');

    // ── Publications ──────────────────────────────────────────
    function filterAndSort() {
      const selectedYear       = yearFilterDropdown.value.trim();
      const selectedAuthor     = authorFilterDropdown.value.trim().toLowerCase();
      const selectedConference = conferenceFilterDropdown.value.trim().toLowerCase();
      const selectedTag        = tagFilterDropdown.value.trim().toLowerCase();

      let filtered = cards.filter(card => {
        const matchYear = !selectedYear || card.dataset.year === selectedYear;

        const cardAuthors = card.dataset.authors.toLowerCase();
        let matchAuthor;
        if (selectedAuthor.includes('qi (cheems) wang')) {
          matchAuthor = !selectedAuthor || cardAuthors.includes(selectedAuthor)
            || cardAuthors.includes('qi wang') || cardAuthors.includes('cheems wang');
        } else {
          matchAuthor = !selectedAuthor || cardAuthors.includes(selectedAuthor);
        }

        const matchConference = !selectedConference
          || card.dataset.conference.toLowerCase().includes(selectedConference);
        const matchTag = !selectedTag || card.dataset.tag.toLowerCase().includes(selectedTag);

        return matchYear && matchAuthor && matchConference && matchTag;
      });

      filtered.sort((a, b) => Number(b.dataset.year) - Number(a.dataset.year));

      cards.forEach(c => { c.style.display = 'none'; });
      filtered.forEach((c, i) => {
        if (showAllPubs || i < PUB_LIMIT) c.style.display = 'block';
      });

      if (filtered.length === 0) {
        if (showMoreBtn) showMoreBtn.style.display = 'none';
        if (thatsAllBtn) thatsAllBtn.style.display = 'none';
        if (noPapersBtn) noPapersBtn.style.display = 'block';
      } else if (!showAllPubs && filtered.length > PUB_LIMIT) {
        if (showMoreBtn) {
          showMoreBtn.style.display = 'inline-block';
          showMoreBtn.textContent =
            `${PUB_LIMIT} of ${filtered.length} Publications Displayed — Click to Show All`;
        }
        if (thatsAllBtn) thatsAllBtn.style.display = 'none';
        if (noPapersBtn) noPapersBtn.style.display = 'none';
      } else {
        if (showMoreBtn) showMoreBtn.style.display = 'none';
        if (thatsAllBtn) {
          thatsAllBtn.style.display = 'block';
          thatsAllBtn.textContent = `All ${filtered.length} publications shown.`;
        }
        if (noPapersBtn) noPapersBtn.style.display = 'none';
      }
    }

    if (showMoreBtn) {
      showMoreBtn.addEventListener('click', function () {
        showAllPubs = true;
        filterAndSort();
      });
    }

    yearFilterDropdown.addEventListener('change', function () {
      showAllPubs = false;
      filterAndSort();
    });
    authorFilterDropdown.addEventListener('change', function () {
      showAllPubs = false;
      filterAndSort();
    });
    conferenceFilterDropdown.addEventListener('change', function () {
      showAllPubs = false;
      filterAndSort();
    });
    tagFilterDropdown.addEventListener('change', function () {
      showAllPubs = false;
      filterAndSort();
    });

    // ── Team Members ──────────────────────────────────────────
    function teamfilterAndSort() {
      teamcards.forEach(c => { c.style.display = 'block'; });
    }

    // ── News ──────────────────────────────────────────────────
    function newsfilterAndSort() {
      if (!newsYearFilterDropdown) return;
      const selectedYear = newsYearFilterDropdown.value.trim();

      let filtered = newscards.filter(c => !selectedYear || c.dataset.year === selectedYear);
      filtered.sort((a, b) => Number(b.dataset.year) - Number(a.dataset.year));

      newscards.forEach(c => { c.style.display = 'none'; });
      filtered.forEach((c, i) => {
        if (showAllNews || i < NEWS_LIMIT) c.style.display = 'block';
      });

      const newsMoreBtn    = document.getElementById('showMoreNewsBtn');
      const thatsAllNews   = document.getElementById('thatsAllNewsBtn');

      if (filtered.length === 0) {
        if (newsMoreBtn)  newsMoreBtn.style.display  = 'none';
        if (thatsAllNews) thatsAllNews.style.display = 'none';
        if (noNewsBtn)    noNewsBtn.style.display    = 'block';
      } else if (!showAllNews && filtered.length > NEWS_LIMIT) {
        if (newsMoreBtn) {
          newsMoreBtn.style.display = 'inline-block';
          newsMoreBtn.textContent =
            `${NEWS_LIMIT} of ${filtered.length} News Displayed — Click to Show All`;
        }
        if (thatsAllNews) thatsAllNews.style.display = 'none';
        if (noNewsBtn)    noNewsBtn.style.display    = 'none';
      } else {
        if (newsMoreBtn)  newsMoreBtn.style.display  = 'none';
        if (thatsAllNews) {
          thatsAllNews.style.display = 'block';
          thatsAllNews.textContent = `All ${filtered.length} news items shown.`;
        }
        if (noNewsBtn) noNewsBtn.style.display = 'none';
      }
    }

    const showMoreNewsBtn = document.getElementById('showMoreNewsBtn');
    if (showMoreNewsBtn) {
      showMoreNewsBtn.addEventListener('click', function () {
        showAllNews = true;
        newsfilterAndSort();
      });
    }
    if (newsYearFilterDropdown) {
      newsYearFilterDropdown.addEventListener('change', function () {
        showAllNews = false;
        newsfilterAndSort();
      });
    }

    // ── Blogs ─────────────────────────────────────────────────
    function blogFilterAndSort() {
      if (!blogContainer || !blogYearFilterDropdown) return;
      const selectedYear = blogYearFilterDropdown.value.trim();

      let filtered = blogItems.filter(item =>
        item.dataset && item.dataset.year && (!selectedYear || item.dataset.year === selectedYear)
      );
      filtered.sort((a, b) => Number(b.dataset.year) - Number(a.dataset.year));

      blogItems.forEach(i => { i.style.display = 'none'; });
      filtered.forEach((item, i) => {
        if (showAllBlogs || i < BLOG_LIMIT) item.style.display = 'block';
      });

      const blogMoreBtn   = document.getElementById('showMoreBlogsBtn');
      const thatsAllBlogs = document.getElementById('thatsAllBlogsBtn');

      if (filtered.length === 0) {
        if (blogMoreBtn)   blogMoreBtn.style.display   = 'none';
        if (thatsAllBlogs) thatsAllBlogs.style.display = 'none';
        if (noBlogsBtn)    noBlogsBtn.style.display    = 'block';
      } else if (!showAllBlogs && filtered.length > BLOG_LIMIT) {
        if (blogMoreBtn) {
          blogMoreBtn.style.display = 'inline-block';
          blogMoreBtn.textContent =
            `${BLOG_LIMIT} of ${filtered.length} Blogs Displayed — Click to Show All`;
        }
        if (thatsAllBlogs) thatsAllBlogs.style.display = 'none';
        if (noBlogsBtn)    noBlogsBtn.style.display    = 'none';
      } else {
        if (blogMoreBtn)   blogMoreBtn.style.display   = 'none';
        if (thatsAllBlogs) {
          thatsAllBlogs.style.display = 'block';
          thatsAllBlogs.textContent = `All ${filtered.length} blog posts shown.`;
        }
        if (noBlogsBtn) noBlogsBtn.style.display = 'none';
      }
    }

    const showMoreBlogsBtn = document.getElementById('showMoreBlogsBtn');
    if (showMoreBlogsBtn) {
      showMoreBlogsBtn.addEventListener('click', function () {
        showAllBlogs = true;
        blogFilterAndSort();
      });
    }
    if (blogYearFilterDropdown) {
      blogYearFilterDropdown.addEventListener('change', function () {
        showAllBlogs = false;
        blogFilterAndSort();
      });
    }

    // ── Initial render ────────────────────────────────────────
    filterAndSort();
    teamfilterAndSort();
    newsfilterAndSort();
    blogFilterAndSort();
  });
