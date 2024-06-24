import axios from 'axios';
import Cookies from 'js-cookie';
import { URL_API, URL_SEARCH_DB } from '../../utils/constants';

const searchDb = async ({ e, LogActivity, setError, setLoading, setSearchResults, searchText, isError }) => {
    
    e.preventDefault();
    if (isError || !searchText.trim()) return;

    setLoading(true);
    setError(null);

    try {
        const token = Cookies.get('token');
        const response = await axios.get(`${URL_API + URL_SEARCH_DB}?q=${searchText}`, {
            headers: {
              Authorization: `Bearer ${token}`,
              'Content-Type': 'application/json',
            }
          });
        setSearchResults(response.data.result);
        LogActivity('click_history_search', searchText);
    } catch (err) {
        setError(err.message);
    } finally {
        setLoading(false);
    }
};

export default searchDb;