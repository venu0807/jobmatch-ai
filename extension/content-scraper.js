/**
 * JobMatch AI — Active Tab Job Description Scraper
 * Extracts job description, title, and company from LinkedIn, Naukri, Indeed, and generic portals.
 */
(() => {
  // 1. Check if the user has manually highlighted/selected text
  const selectedText = window.getSelection() ? window.getSelection().toString().trim() : "";
  if (selectedText.length > 50) {
    return {
      success: true,
      source: "selection",
      title: document.title,
      company: "",
      text: selectedText,
      url: window.location.href
    };
  }

  // 2. Portal-Specific Selector Dictionaries
  const siteSelectors = [
    // LinkedIn
    {
      domain: "linkedin.com",
      desc: [
        ".jobs-description__content",
        ".jobs-box__html-content",
        ".jobs-description",
        "#job-details",
        "article.jobs-description__container"
      ],
      title: [
        ".job-details-jobs-unified-top-card__job-title",
        ".jobs-unified-top-card__job-title",
        "h1.t-24"
      ],
      company: [
        ".job-details-jobs-unified-top-card__company-name",
        ".jobs-unified-top-card__company-name",
        ".jobs-unified-top-card__subtitle-primary-grouping a"
      ]
    },
    // Naukri
    {
      domain: "naukri.com",
      desc: [
        ".styles_job-desc-container__txpYf",
        ".dang-inner-html",
        ".job-desc",
        "section.job-desc-container"
      ],
      title: [
        ".styles_header-title__job-title",
        ".styles_jdn-header-title__R8j1w",
        "h1.styles_header-title__job-title"
      ],
      company: [
        ".styles_header-title__company-name",
        ".styles_jdn-header-title__company-name"
      ]
    },
    // Indeed
    {
      domain: "indeed.com",
      desc: [
        "#jobDescriptionText",
        ".jobsearch-JobComponent-description"
      ],
      title: [
        "h1.jobsearch-JobInfoHeader-title",
        "[data-testid='jobsearch-JobInfoHeader-title']"
      ],
      company: [
        "[data-testid='inlineHeader-companyName']",
        ".jobsearch-InlineCompanyRating a"
      ]
    },
    // Greenhouse
    {
      domain: "greenhouse.io",
      desc: ["#content", "#app-body", ".body"],
      title: [".app-title", "h1"],
      company: [".company-name"]
    },
    // Lever
    {
      domain: "lever.co",
      desc: [".section.page-centered", ".posting-page"],
      title: [".posting-headline h2", "h2"],
      company: [".main-header-logo"]
    },
    // Ashby
    {
      domain: "ashbyhq.com",
      desc: [".ashby-job-posting-description", "[class*='description']"],
      title: ["h1"],
      company: ["[class*='company']"]
    }
  ];

  const currentHost = window.location.hostname.toLowerCase();
  let foundSite = siteSelectors.find(s => currentHost.includes(s.domain));

  let extractedText = "";
  let extractedTitle = "";
  let extractedCompany = "";

  // Helper to query first matching selector
  function queryFirst(selectors) {
    if (!selectors) return "";
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el && el.innerText && el.innerText.trim().length > 0) {
        return el.innerText.trim();
      }
    }
    return "";
  }

  if (foundSite) {
    extractedText = queryFirst(foundSite.desc);
    extractedTitle = queryFirst(foundSite.title);
    extractedCompany = queryFirst(foundSite.company);
  }

  // Generic Fallbacks if portal-specific selectors didn't match or for company career pages
  if (!extractedText || extractedText.length < 50) {
    const genericDescSelectors = [
      "[data-job-description]",
      "[class*='job-description']",
      "[class*='jobDescription']",
      "[class*='JobDescription']",
      "[id*='job-description']",
      "[id*='jobDescription']",
      "article",
      "main",
      "[role='main']"
    ];
    extractedText = queryFirst(genericDescSelectors);
  }

  // Clean the extracted text
  if (extractedText) {
    extractedText = extractedText
      .replace(/\r\n/g, "\n")
      .replace(/[ \t]+/g, " ")
      .replace(/\n\s*\n+/g, "\n\n")
      .trim();
  }

  return {
    success: !!(extractedText && extractedText.length > 50),
    source: foundSite ? foundSite.domain : "generic",
    title: extractedTitle || document.title,
    company: extractedCompany,
    text: extractedText,
    url: window.location.href
  };
})();
