#menggunakan GUI library Tkinter untuk user interfacenya 
import tkinter as tk

#import socket karena menggunakan IPC socket
import socket 

# import thread agar server dapat menerima request koneksi client baru
# ketika sedang memproses pesan dari client yang sudah connect
import threading

window = tk.Tk()
window.title("Sever")

# frameAtas terdiri dari dua button yaitu btnStart dan btnStop
frameAtas = tk.Frame(window)

# button connect
# dan fungsi start_server akan dipanggil ketika button diclick
btnStart = tk.Button(frameAtas, text="Connect", command=lambda : start_server())
btnStart.pack(side=tk.LEFT)

# button stop
# dan fungsi start_server akan dipanggil ketika button diclick
btnStop = tk.Button(frameAtas, text="Stop", command=lambda : stop_server(), state=tk.DISABLED)
btnStop.pack(side=tk.LEFT)
frameAtas.pack(side=tk.TOP, pady=(5, 0))

# middle frame terdiri dari dua labels untuk display host dan port info
middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text = "Host: X.X.X.X")
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text = "Port:XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))

# client farme yang menampilkan client area
clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text=" Client List ").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=15, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))


# network server
server = None
HOST_ADDR = "192.168.1.4"
HOST_PORT = 5000
client_name = " "
clients = []
clients_names = []


# Start server function
def start_server():
    global server, HOST_ADDR, HOST_PORT
    btnStart.config(state=tk.DISABLED)
    btnStop.config(state=tk.NORMAL)

    # buat server socket IPv4 (socket.AF_INET) dan TCP protocol (socket.SOCK_STREAM)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(socket.AF_INET)
    print(socket.SOCK_STREAM)
    
    # server binding address dan port
    server.bind((HOST_ADDR, HOST_PORT))
    
    # server is listening untuk client connection
    server.listen(5)  

    #thread baru menerima new clients connection
    threading._start_new_thread(accept_clients, (server, " "))

    lblHost["text"] = "Host: " + HOST_ADDR
    lblPort["text"] = "Port: " + str(HOST_PORT)


# Stop server function
def stop_server():
    global server
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)

#server menerima request koneksi client-client baru, 
#dan informasi client akan di store di dalam list yaitu clients 
def accept_clients(the_server, y):
    while True:
        client, addr = the_server.accept()
        clients.append(client)
        
        #start new thread untuk handle sending/recieve pesan dari client-client
        threading._start_new_thread(send_receive_client_message, (client, addr))


# untuk menerima message dari current client 
# dan mengirim pesan tersebut ke client-client lainnya
def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, clients_addr
    client_msg = " "

    # send welcome message to client
    # jika ada client baru connect, maka client akan mengirim nama ke server
    # server menerimanya dengan socket.recv method
    client_name  = client_connection.recv(4096).decode()
    welcome_msg = "Welcome " + client_name + ". Use 'exit' to quit"
    
    # mengirim isi welcome_msg
    client_connection.send(welcome_msg.encode())
    clients_names.append(client_name)

    # update display nama client
    update_client_names_display(clients_names)  


    while True:
        data = client_connection.recv(4096).decode()
        if not data: break
        if data == "exit": break

        client_msg = data
        
        # me-return current client index yang ada pada client list
        # jadi ini bertujuan untuk mengetahui client index
        # dan aplikasi ini dapat mengirim pesan ke semua client yang connect
        idx = get_client_index(clients, client_connection)
        sending_client_name = clients_names[idx]

        for c in clients:
            if c != client_connection:
                server_msg = str(sending_client_name + "->" + client_msg)
                c.send(server_msg.encode())

    # find the client index then remove from both lists(client name list and connection list)
    idx = get_client_index(clients, client_connection)
    del clients_names[idx] # hapus client ketika pesan exit
    del clients[idx] # hapus client ketika pesan exit
    server_msg = "BYE!"
    client_connection.send(server_msg.encode())
    client_connection.close()

    #update nama client di display
    update_client_names_display(clients_names) 


# return index dari current client pada list clients
def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1
    return idx

# mengupdate display nama client ketika ada client baru yang connect atau
# ketika client yang connect telah disconnect
def update_client_names_display(name_list):
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in name_list:
        tkDisplay.insert(tk.END, c+"\n")
    tkDisplay.config(state=tk.DISABLED)

window.mainloop()