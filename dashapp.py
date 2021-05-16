from app import create_app

server = create_app()
# print(server.debug)

if __name__ == '__main__':
    server.run()