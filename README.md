## Loan Automator for yotepresto.com

This project aims to allow other lenders using yotepresto (a Mexican P2P Lending Marketplace) to **automatically** loan money to borrowers applying for loans.

Please read attached license before proceeding.


## License (MIT)

Copyright © 2019-2020 Sam Wong

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


## The Problem being solved

This project aims to resolve some frustrations I got tired of:
1. Refreshing the loan out page to see if there were new loans for me to lend out the minimum amount of 200 pesos (ie. executing a diversification strategy).
2. Missing opportunities when I wasn't able to refresh the loan out page due to not being a robot.
3. Manually exporting my data from the yotepresto Web UI.
4. Overcoming limitations in the 'Autoinvest' feature which was released at the start of March, 2020.


## Features
1. Export your portfolio and transactional data to CSV.
2. Automatically loan out your hard earnt MXN pesos (at MXN200 per loan).
3. Receive email notifications when your funds get depleted (fall into the next MXN1,000 pesos band) to remind you to top up your account.


## Dependencies

- [A yotepresto account](https://www.yotepresto.com/)
- [A bankroll in Mexican Pesos](https://en.wikipedia.org/wiki/Mexican_peso)
- [macOS 10.14.6 (Mojave)](https://en.wikipedia.org/wiki/MacOS)
- [Python 3.7.2](https://www.python.org/)
- [ChromeDriver (Selenium Web Driver)](https://chromedriver.chromium.org/getting-started)
- [BeautifulSoup4 for html parsing](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)


## Usage

1. Install dependencies above if necessary.
2. Create a copy of the .envexample and fill out your username and password (don't forget to encode them with base64)
3. Ensure your yotepresto account is funded with the money you want automatically loaned out.
4. Run `make loop`
5. Sit back and relax as the magic happens, when new loans appear this solution should now automatically fund and checkout new loan applications.
6. ...
7. `$$$`


## Roadmap

1. Improve the CLI (execute different types of tasks based on CLI flags) -- replacing the current commented out code
2. Add configuration/re-configuration of user and lending settings
3. Schedule loan out page refreshes via crontabs
4. Address code quality issues
5. Localize README.md into Spanish


## A note to the team at yotepresto.com

- Your team has built a really great marketplace that I love using!
- Please don't interpret this tool as a means or a statement that your work isn't valued!
- The work your team does is super valuable as it democratises the way people borrow money and loan money to earn interest.
- It also circumvents incumbents in the market who aren't providing competitive interest rates.

If any of your team members ever visit Melbourne, Australia, please reach out to me and I'll shout you a cold one (ie. cerveza)!
