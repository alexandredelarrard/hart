export const organizeResults = (results, t) => {

  const organizedResults = {
    [t("plateforme.sidebar.today")]: [],
    [t('plateforme.sidebar.yesterday')]: [],
    [t('plateforme.sidebar.lastweek')]: [],
    [t('plateforme.sidebar.lastmonth')]: [],
    [t('plateforme.sidebar.older')]: []
  };

  const now = new Date();

  // Sort results by date in descending order (most recent first)
  results.sort((a, b) => new Date(b.creation_date) - new Date(a.creation_date));

  results.forEach(result => {
    const resultDate = new Date(result.creation_date);
    const differenceInDays = Math.floor((now - resultDate) / (1000 * 60 * 60 * 24));
    result.llm_result = JSON.parse(JSON.stringify(result.llm_result));

    if (differenceInDays <= 1) {
      organizedResults[t('plateforme.sidebar.today')].push(result);
    } else if (differenceInDays <= 2) {
      organizedResults[t('plateforme.sidebar.yesterday')].push(result);
    } else if (differenceInDays <= 7) {
      organizedResults[t('plateforme.sidebar.lastweek')].push(result);
    } else if (differenceInDays <= 30) {
      organizedResults[t('plateforme.sidebar.lastmonth')].push(result);
    } else {
      organizedResults[t('plateforme.sidebar.older')].push(result);
    }
  });

  // Remove keys with empty lists
  Object.keys(organizedResults).forEach(key => {
    if (organizedResults[key].length === 0) {
      delete organizedResults[key];
    }
  });

  return organizedResults;
};
