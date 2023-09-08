from dotenv import dotenv_values

from src.FireflyClient import Client

if __name__ == "__main__":
    config = dotenv_values(".env")
    client = Client(config)
    print(client)
