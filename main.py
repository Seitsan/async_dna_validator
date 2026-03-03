import asyncio
import socket
from asyncio import AbstractEventLoop

alphabet = 'ACGTRYMKSWHBVDN'

async def validate_dna(connection: socket,
                loop: AbstractEventLoop) -> None:
    buffer = ''
    try:
        while data := await loop.sock_recv(connection, 1024):
            buffer += data.decode('utf-8').upper()
            if '\n' in buffer or '\r\n' in buffer:
                seq = buffer.replace('\r\n', '\n')[:-1]
                if len(seq) > 20:
                    result = 'Maximum seq length exceeded\r\n'
                else:
                    is_valid = set(seq).issubset(set(alphabet))
                    if is_valid:
                        result = 'This is a DNA\r\n'
                    else:
                        result = 'This is not a DNA\r\n'
                await loop.sock_sendall(connection, result.encode('utf-8'))
                buffer = ''
    except (ConnectionResetError, asyncio.CancelledError):
        pass
    finally:
        connection.close()
        print("Connection closed")


async def listen_for_connection(server_socket: socket,
                                loop: AbstractEventLoop):
    tasks = set()
    try:
        while True:
            connection, address = await loop.sock_accept(server_socket)
            connection.setblocking(False)
            print(f"Connection from {address}")
            task = asyncio.create_task(validate_dna(connection, loop))
            tasks.add(task)
            task.add_done_callback(tasks.discard)

    except asyncio.CancelledError:
        print("Stopping the connections")
        for task in tasks: task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

async def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    server_address = ('127.0.0.1', 34561)
    server_socket.setblocking(False)
    server_socket.bind(server_address)
    server_socket.listen()

    print('Server started at 127.0.0.1:34561')

    loop = asyncio.get_running_loop()

    listener_task = asyncio.create_task(listen_for_connection(server_socket, loop))

    try:
        await listener_task
    except KeyboardInterrupt:
        print("\nGot a stop signal")
        listener_task.cancel()
        await listener_task
    finally:
        server_socket.close()
        print('Server stopped successfully')

if __name__ == "__main__":
    asyncio.run(main())
