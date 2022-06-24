# Reboot Investing
https://rebootinvesting.com/

Simple repo that generates candlestick charts using a free public API

## Instructions
### Docker
There is a docker-compose.yml file associated with this project, and after building the image and running the container you can simply go to http://localhost:3000 to visit the app  
Alternatively, if you want to build and run the server and client separately please follow the instructions below.

### Server
This is a simple endpoint written in FastAPI that uses yfinance to get stock data.  The URL format is http://localhost:8000/quote/{ticker}/{interval}?start={start}&end={end}
The following are the parameter requirements:
#### URL Parameters - Required
ticker - Must be a stock symbol.  Invalid symbols don't error out, they just don't return any data  
interval - Must be one of the following

- 1d -> daily
- 1wk -> weekly
- 1mo -> monthly

#### URL Parameters - Optional
start - Must be in the format of yyyy-mm-dd  
end - Must be in the format of yyyy-mm-dd  
The start date must be less than the end date, otherwise a 400 exception will be returned.

#### Versions and Installation instructions
Python 3.8.0 is required.  To install and run the code, simply navigate to the server location, create a virtual environment, install the requirements file, and run the uvicorn run script

```
cd server
python -m venv env
pip install -r requirements.txt
uvicorn main:app --reload
```

### Client
This is a Vue 3 (JavaScript) app that utilizes the Apex Charts open source library for charting and Tailwind CSS/UI for UI elements.

#### Versions and Installation Instructions
The following versions were used

- node: 14.17.6
- npm: 6.14.15

In order to run the code simply run npm install then npm run serve and navigate to http://localhost:3000

```
cd client
npm i
npm run serve
```
