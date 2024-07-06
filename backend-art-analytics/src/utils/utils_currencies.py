import yfinance as yf
from tqdm import tqdm
import logging

def extract_currencies(liste_paires):

    currency_data = {}

    # extract currency pairs 
    for paire in tqdm(liste_paires):

        try:
            x_usd = yf.Ticker(f"{paire}=X")
            hist = x_usd.history(period="max")
            hist = hist[["Open", "Close"]].reset_index()
            hist["Date"] = hist["Date"].dt.strftime("%Y-%m-%d")
            currency_data[paire[:3]] = hist
        except Exception as e:
            logging.error(f"COULD NOT GET PAIR {paire} from yfinance")

    return currency_data