export const organizeResults = (results) => {
    const organizedResults = {
      "Today": [],
      "Yesterday": [],
      "Last Week": [],
      "Last Month": [],
      "Older": []
    };

    const now = new Date();
    results.forEach(result => {
      const resultDate = new Date(result.result_date);
      const differenceInDays = Math.floor((now - resultDate) / (1000 * 60 * 60 * 24));

      if (differenceInDays <= 1) {
        organizedResults["Today"].push(result);
      } else if (differenceInDays < 2) {
        organizedResults["Yesterday"].push(result);
      } else if (differenceInDays <= 7) {
        organizedResults["Last Week"].push(result);
      } else if (differenceInDays <= 30) {
        organizedResults["Last Month"].push(result);
      } else {
        organizedResults["Older"].push(result);
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