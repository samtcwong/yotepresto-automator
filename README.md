## yotepresto Loan Automator

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
4. Overcoming limitations in the 'Autoinvest' feature which was recently released

*Auto pretty much what this tool does.

However, there are limitations with 'Autoinvest', which you can read on their [site](yotepresto.com).


## Roadmap

1. Improve the CLI (execute different types of tasks based on CLI flags) -- replacing the current commented out code
2. Add configuration/re-configuration of user and lending settings
3. Schedule loan out page refreshes via crontabs
4. Address code quality issues
5. Localize README.md into Spanish


## Dependencies

- [A bankroll in Mexican Pesos](https://en.wikipedia.org/wiki/Mexican_peso)
- [macOS 10.14.6 (Mojave)](https://en.wikipedia.org/wiki/MacOS)
- [Python 3.7.2](https://www.python.org/)
- [ChromeDriver (Selenium Web Driver)](https://chromedriver.chromium.org/getting-started)
- [BeautifulSoup4 for html parsing](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)


## A note to the team at yotepresto.com

- Your team has built a really great marketplace that I love using!
- Please don't interpret this tool as a means or a statement that your work isn't valued!
- The work your team does is super valuable as it democratises the way people borrow money and loan money to earn interest.
- It also circumvents incumbents in the market who aren't providing competitive interest rates.

If any of your team members ever visit Melbourne, Australia, please reach out to me and I'll shout you a cold one (ie. cerveza)!
