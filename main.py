from dotenv import dotenv_values

from src.FireflyLearning import Client


def main():
    config = dotenv_values(".env")
    client = Client(config)
    print(client)


if __name__ == "__main__":
    main()
