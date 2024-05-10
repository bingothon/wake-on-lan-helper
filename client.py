import socket
import subprocess
import sys

def sleep_computer():
    ps_command = "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Application]::SetSuspendState([System.Windows.Forms.PowerState]::Suspend, $false, $false)"
    subprocess.run(["powershell", "-Command", ps_command], check=True)

def start_listener(ip, port, secret_key):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((ip, port))
    serversocket.listen(5)
    serversocket.setblocking(False)

    print(f"Client listener started on {ip}:{port}")

    try:
        while True:
            try:
                clientsocket, addr = serversocket.accept()
                print(f"Received a connection from {addr}")

                # Non-blocking receive, handle exceptions
                try:
                    data = clientsocket.recv(1024).decode('utf-8').strip()
                    if data:
                        print(f"Received data: {data}")
                        if data.startswith('GET') or data.startswith('POST'):
                            # Basic handling of HTTP request
                            clientsocket.sendall(b"HTTP/1.1 200 OK\n\nHello from TCP server.")
                        elif 'sleep:' in data and data.split('sleep:')[1] == secret_key:
                            print("Valid key received, putting the PC to sleep...")
                            sleep_computer()
                        else:
                            print("Unknown command or invalid key received.")
                except BlockingIOError:
                    continue  # Non-blocking mode error handling
                except Exception as e:
                    print(f"Error receiving data: {str(e)}")

                clientsocket.close()
            except BlockingIOError:
                continue  # No incoming connections

    except KeyboardInterrupt:
        print("Shutting down server.")
    finally:
        serversocket.close()

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: client.exe <IP> <Port> <SecretKey>")
    else:
        start_listener(sys.argv[1], int(sys.argv[2]), sys.argv[3])
