from dummyauth import create_app
import os

def main():
    app = create_app()
    app.run(host=os.environ.get('HOST', '0.0.0.0'))

if __name__ == "__main__":
    main()
