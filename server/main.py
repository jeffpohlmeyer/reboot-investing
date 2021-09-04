from datetime import datetime as dt
from typing import Optional
from fastapi import FastAPI, HTTPException
import pandas as pd
import yfinance as yf

app = FastAPI()

@app.get("/quote/{ticker}/{interval}")
def get_prices(ticker: str, interval: str, start: Optional[str] = None, end: Optional[str] = None):
    # Make sure that the interval is in the allowable group
    if interval not in ['1d', '1wk', '1mo']:
        raise HTTPException(status_code=400, detail="Only daily, weekly, monthly intervals are allowed.")
    
    # If end is passed in and start is not then just set the start to be 1 year back
    if end is not None and start is None:
        end_date = end.split('-')
        year = int(end_date[0]) - 1
        start = '-'.join([str(year), end_date[1], end_date[2]])
    
    # Grab the stock, get history, convert to json
    stock = yf.Ticker(ticker)
    history = stock.history(interval=interval, start=start, end=end)
    # The default date_format is epoch unless using table format
    return dict(data=history.to_json(date_format='iso', orient='split'))
