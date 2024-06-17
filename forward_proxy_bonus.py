import socket
import threading

# Konstanta untuk ukuran buffer dan port
BUFFER_SIZE = 4096
LOCAL_PORT = 9919


# Fungsi untuk menangani koneksi klien
def handle_client(client_socket):
    try:
        request = client_socket.recv(BUFFER_SIZE)
        request_line = request.split(b"\n")[0]
        method, url, version = request_line.split(b" ")

        if method == b"CONNECT":
            target_host, target_port = url.split(b":")
            target_port = int(target_port)
            response = b"HTTP/1.1 200 Connection Established\r\n\r\n"
            client_socket.send(response)

            proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxy_socket.connect((target_host.decode(), target_port))

            client_to_server = threading.Thread(
                target=forward, args=(client_socket, proxy_socket), daemon=True
            )
            server_to_client = threading.Thread(
                target=forward, args=(proxy_socket, client_socket), daemon=True
            )
            client_to_server.start()
            server_to_client.start()
            client_to_server.join()
            server_to_client.join()
        else:
            http_pos = url.find(b"://")
            if http_pos == -1:
                temp = url
            else:
                temp = url[(http_pos + 3) :]
            port_pos = temp.find(b":")
            webserver_pos = temp.find(b"/")
            if webserver_pos == -1:
                webserver_pos = len(temp)
            if port_pos == -1 or webserver_pos < port_pos:
                port = 80
                webserver = temp[:webserver_pos]
            else:
                port = int((temp[(port_pos + 1) :])[: webserver_pos - port_pos - 1])
                webserver = temp[:port_pos]

            proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            proxy_socket.connect((webserver.decode(), port))
            proxy_socket.send(request)

            response = b""
            while True:
                data = proxy_socket.recv(BUFFER_SIZE)
                if len(data) > 0:
                    response += data
                else:
                    break

            # Memproses respons HTTP
            header_end = response.find(b"\r\n\r\n") + 4
            header = response[:header_end]
            body = response[header_end:]

            # Mengganti kata 'software' dengan 'kontol' dan menghitung jumlahnya
            body_lower = body.lower()
            body_replaced = body_lower.replace(b"software", b"kontol")
            count = (len(body_lower) - len(body_replaced)) // len(b"software")

            # Menyisipkan informasi jumlah kata yang dihapus
            info = f"<p>Number of 'software' words removed: {count}</p>\r\n".encode()
            if b"</body>" in body:
                body = body.replace(b"</body>", info + b"</body>")
            elif b"</html>" in body:
                body = body.replace(b"</html>", info + b"</html>")

            # Mengirim respons ke klien
            client_socket.send(header + body)

            proxy_socket.close()
            client_socket.close()
    except Exception as e:
        print(f"Error handling client: {e}")
        client_socket.close()


# Fungsi untuk meneruskan data antara dua soket
def forward(source, destination):
    try:
        while True:
            data = source.recv(BUFFER_SIZE)
            if len(data) > 0:
                destination.send(data)
            else:
                break
    except Exception as e:
        print(f"Forwarding error: {e}")
    finally:
        try:
            source.shutdown(socket.SHUT_RDWR)
            destination.shutdown(socket.SHUT_RDWR)
        except:
            pass
        source.close()
        destination.close()


# Fungsi utama untuk memulai server proxy
def start_proxy():
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("localhost", LOCAL_PORT))
        server_socket.listen(5)
        print(f"Proxy server berjalan di port {LOCAL_PORT}...")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")

            # Handle client in a new thread
            client_thread = threading.Thread(
                target=handle_client, args=(client_socket,), daemon=True
            )
            client_thread.start()
    except socket.error as se:
        print(f"Socket error: {se}")
    except Exception as e:
        print(f"Proxy server error: {e}")
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_proxy()
