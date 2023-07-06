# 7versts Telegram Bot

This is a Telegram bot developed using the aiogram framework and SQLAlchemy for database operations.

## Features

- Feature 1: Bot needed to calculate seamstresses' wages
- Feature 2: The bot provides all the information for the clothing production director
- Feature 3: The Bot helps to control and monitor accounting


## Prerequisites

Before running the bot, ensure you have the following prerequisites installed:

1. Python 3.7 or higher
2. Docker
3. Docker Compose

## Installation

Follow these steps to set up and run the bot:

1. ***Clone the repository:***

```bash
git clone https://github.com/Aleksey512/SewTgBot
cd SewTgBot
```

2.  ***Set up the configuration file:***

open ***.env*** file and update the necessary values such as the Telegram API token, database connection details, etc.

3.  ***Build and run the Docker containers:***

```bash
docker-compose up --build -d
```
This will create and start the bot container along with the required database container.

4. ***Verify the bot is running:***

Open your Telegram app and search for the bot by its username. You should be able to find and interact with it.

## Usage

Here are some instructions on how to use the bot:

Start the bot by sending the ***/start*** command.

Follow the prompts or use the available commands to interact with the bot's features.

Enjoy the functionality provided by the bot!

## Troubleshooting

If you encounter any issues while running the bot, consider the following steps:

Check that you have provided the correct API token in the config.py file.

Verify your database connection details and ensure the database is running.

Check the logs of the Docker containers for any error messages.

If the issue persists, feel free to contact the developers at [7versts](https://7versts.ru/) for further assistance.

## License

This project is licensed under the MIT License. Feel free to modify and distribute the code as needed.

## Acknowledgments

We would like to express our gratitude to the aiogram and SQLAlchemy communities for providing excellent frameworks for building Telegram bots and working with databases. Thank you for your contributions.

For more information about our company, 7versts, please visit our website at [7versts.ru](https://7versts.ru/).