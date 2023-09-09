from dotenv import dotenv_values

from src.FireflyClient import Client


def main():
    config = dotenv_values(".env")
    client = Client(config)


if __name__ == "__main__":
    main()
