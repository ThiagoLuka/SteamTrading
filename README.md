## Steam Level Up Service

An app designed to level up steam accounts based on crafting new badges. Usable only through the Python console.

## Project Status

This project is under development. Users can save up their current badges and inventory now. Booster packs can be opened giving the name of a game.

Future improvements and functionalities:

- [ ] Analysis of the current steam user level and what badges can be created to improve it
- [ ] Badges can be crafted through the app
- [ ] Redirection to browser pages in order to buy more cards
- [ ] Better UI and easy support for other languages
- [ ] Steam login made easy (currently users have to manually set login cookies in order to make it work)
- [ ] Performance improvements

## Setup instructions

### Python 3.9

Further python packages used are visible in requirements.txt

PostgreSQL is also used to store information. To set it up, look for the table's creation file in the folder called "db".

## Reflection

This is a side project developed to improve some of my data manipulation skills. It was build from scratch as an ETL pipeline.

The core of the app is a web crawler that was designed to "interact" with steam web pages, as a regular browser client would do, and extract the information that is useful to perform the leveling up on steam. This data is then processed to make the leveling up actions available. The actions initially thought of are two: the crafting of badges which cards are already in inventory, and the redirection to a web page where more cards can be bought.

I used Object-Oriented Programming to build the crawler in a way that the SOLID principles are respected. In order to do that, the crawler is based on the factory design pattern, while their interactions are the elements "built" through the interactions. This has proved to be a nice way to split responsibilities between classes, making it easy to create new interactions without having to deal with login authentication again.

The ETL pipeline can be found in two different sets of classes. The extraction and transformation of the data are located in each steam web page class, while the loading proccesses are at the data_models classes. The former set of classes are also used as a primary access point to the database. This brakes the single resposibility principle, but it has also allowed to make a single layer between the database and the rest of the app.
