<h2>Portfolio Optimization and Scraper</h2>
<p>The main idea of this project was to create a portfolio optimizer that maximizes sharpe ratio.</p>
<p>Model can receive hundreds of portfolio volatilities and returns and will calculate the best combination.</p>
<p>As a reference a optimization with 500 stocks with information of around 200 days (10 months of 2019) runs in less than 2 minutes in my computer.</p>
<p>&nbsp;</p>
<h3>Main file to look for:</h3>
<li>portfolio_optimization.py: this file has all you need to run it for yourself. It works with the symbols/quotes you want to download from Yahoo Finance. If you want to run it with assets not contained in yahoo finance (such as cash, funds, etc.) you will need to create a CSV file that information and process it along with the stocks you want to consider.</li>
<li>portfolio.py: is the file I used for scraping yahoo finance to get some additional detail about some stocks I was tracking. In order to use it I suggest you load the whole file as a library and then call functions as required. You might need to create some local sql file to download the information.</li>
<li>master.py: is an example of how I was calling different functions as required when I did my monitoring stocks presentation. It might not be particularly useful to you but you can see a little bit how to call some functions.</li>

<p>&nbsp;</p>
<h3>Takeaways</h3>
<p>The main takeaways of the study can be found in the following blog.</p>
<p><a href="https://nycdatascience.com/blog/alumni/portfolio-selection-and-optimization/">https://nycdatascience.com/blog/alumni/portfolio-selection-and-optimization/</a></p>
<p>&nbsp;</p>
