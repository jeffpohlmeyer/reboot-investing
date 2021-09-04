# Candlestick Charts.

***Important***:
This project involves writing a simple back-end and front-end for an application that displays prices of stocks in a graph.

The back-end involves getting price data from a free source (yahoo) and provide it as JSON to a Javascript front-end. The front-end involves displaying the data as a candlestick chart. 

We do NOT expect you to write everything from scratch. There are high quality, free libraries that get stock price data from yahoo and make it available in multiple formats. There are free libraries that work with multiple front-end frameworks that display candlestick charts.

We expect you to make good choices regarding which library to use and explain why you chose what you chose. We expect you to write code like you would write in production. This means code should be written for other programmers to understand and documented when necessary. You should try to write your code in a manner that the how is self-explanatory and document the why.

If you need clarification or if you get stuck, call me and I will help.

### The Problem
Create a web page on which there are 4 inputs. One allows a user to type in the ticker symbol for a stock. The second input is a start date. The third input is an end date. The 4th input allows a user to choose between daily, weekly or monthly data.

If the user types in a ticker symbol that does not exist, or a start date that is the same or later than the end date, the page should let the user know that there is an error. If the user types in a start date earlier than the earliest date for which we have data or later than the latest date for which we have data, then the date entered should be replaced with the appropriate date when the graph is drawn.

If the user requests daily data, display daily data i.e. daily open price, high price, low price, close price and volume (number of shares traded). If the user requests weekly data, display weekly data i.e. weekly open price, high price, low price, close price and volume. Note the weekly open price is the open price of the first day in the week. The weekly high (low) price is the highest high (lowest low) price of all the high (low) prices during the week. The weekly close price is the close price of the last day in the week. The same applies for monthly data. Similarly, the volume (number of shares traded) for the week (month) is the sum of the number of shares traded each day during the week (month). Note that you may not have to do any calculation. You can request daily, weekly or monthly data from the libraries that get stock price data from Yahoo.

The area of the page devoted to showing stock data should be divided into 2 seconds, Approximately 80% of the height taken up by the first section and the remainder by the second section.

The first section (approximately top 80% of the area devoted to graphing stock data) should display a candlestick chart of the stock price data. For a description of what a candlestick chart is see [Wikipedia](https://en.wikipedia.org/wiki/Candlestick_chart) and/or  [Investopedia](https://www.investopedia.com/trading/candlestick-charting-what-is-it/).

In the second section (bottom 20% of the area devoted to graphing data) should display a bar chart of the volume (number of shares) traded on the specific day/week/month. The bar representing a period's week should line up vertically with the candlestick representing the prices during that period.

We expect that you will use React or Svelte for the front-end and Python for the back-end. You may use any open source library or component. You may not use closed source libraries. If you do not make extensive use of open source libraries, this project may take an inordinate amount of time. In fact, while this project may overwhelm at first, it is in fact a straightforward stitching together of a few open source libraries. 

You may not generate an image to display in the back-end and display this image in the front-end. The back-end should be get data from yahoo and provide it to the front end as JSON. You should get the data using any one of the open-source libraries that download stock price data from yahoo. The front-end should then display this data. There are multiple libraries that can do this. All you need to do is display the appropriate graphing component on the page ensure the data is in a format the libraries can use and provide it to the component.

We are deliberately not suggesting specific components or open-source libraries. Part of what we are expecting is that you will choose one appropriately and describe why you chose what you chose and why you did not choose the alternatives. However, if your google-fu is failing you, and you would like some suggestions, get in touch and I will help. 