export const sortData = (data, sortOrder) => {
    return data.sort((a, b) => {
      let comparison = 0;
      switch (sortOrder) {
        case 'relevance_desc':
          comparison = a.distance - b.distance;
          break;
        case 'price_desc':
          comparison = b.final_result - a.final_result;
          break;
        case 'price_asc':
          comparison = a.final_result - b.final_result;
          break;
        case 'date_desc':
          comparison = new Date(b.date) - new Date(a.date);
          break;
        case 'date_asc':
          comparison = new Date(a.date) - new Date(b.date);
          break;
        default:
          break;
      }
      return comparison;
    });
  };
