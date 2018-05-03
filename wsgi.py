from dummyauth import create_app
import os

def main():
    app = create_app()
    app.run()

if __name__ == "__main__":
    main()
