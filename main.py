import asyncio

alphabet = set('ACGTRYMKSWHBVDN')

async def handle_client(reader: asyncio.StreamReader,
                        writer: asyncio.StreamWriter):
    try:
        while data := await reader.readline():
            seq = data.decode().strip().upper()

            if len(seq) > 20:
                result = 'Maximum seq length exceeded\r\n'
            elif set(seq).issubset(alphabet):
                result = 'This is a DNA\r\n'
            else:
                result = 'This is not a DNA\r\n'

            writer.write(result.encode())
            await writer.drain()

    except asyncio.CancelledError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()


async def main():
    server = await asyncio.start_server(
        handle_client,
        '127.0.0.1',
        34561
    )

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())