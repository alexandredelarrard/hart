export const formatPrice = (price, langue, currency_suffix) => {
  if (price === null || price === undefined) {
    return ''; 
  }

  if (price >= 1e6) {
    if(currency_suffix){
      return ' ' + (price / 1e6).toFixed(1) + ' M€';
    } else {
      return (price / 1e6).toFixed(1) + ' ';
    }
  } else if (price >= 1e4) {
    if(currency_suffix){
      return ' ' + (price / 1e3).toFixed(1) + ' k€';
    } else {
      return (price / 1e3).toFixed(1) + ' ';
    }
  } else {
    if(currency_suffix){
      return ' ' + price.toLocaleString(langue) + ' €';
    } else {
      return price.toLocaleString(langue) + ' ';
    }
  }
  };