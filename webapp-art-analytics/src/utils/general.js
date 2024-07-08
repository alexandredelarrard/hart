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

export  const validateEmail = (email) => {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  };

export const validatePassword = (password) => {
    const regex = /^(?=.*[A-Z])(?=.*[^\w\s])(?=.{8,})/;
    return regex.test(password);
  };

export const generateDatesRange = (startDate, endDate) => {
  const dates = [];
  let currentDate = new Date(startDate);
  while (currentDate <= endDate) {
    dates.push(new Date(currentDate));
    currentDate.setDate(currentDate.getDate() + 1);
  }
  return dates;
};

export const timeout = (delay) => {
  return new Promise( res => setTimeout(res, delay) );
}
