#menggunakan GUI library Tkinter untuk user interfacenya 
import tkinter as tk

#import socket karena menggunakan IPC socket
import socket 

# import thread agar server dapat menerima request koneksi client baru
# ketika sedang memproses pesan dari client yang sudah connect
import threading

window = tk.Tk()
window.title("Sever")

# frameAtas terdiri dari dua button yaitu tombolStart dan tombolStop
frameAtas = tk.Frame(window)

# button connect
# dan fungsi serverStart akan dipanggil ketika button diclick
tombolStart = tk.Button(frameAtas, text="Connect", command=lambda : serverStart())
tombolStart.pack(side=tk.LEFT)

# button stop
# dan fungsi serverStart akan dipanggil ketika button diclick
tombolStop = tk.Button(frameAtas, text="Stop", command=lambda : serverStop(), state=tk.DISABLED)
tombolStop.pack(side=tk.LEFT)
frameAtas.pack(side=tk.TOP, pady=(5, 0))

# ini frame isinya memasukkan terdiri dari dua labels yaitu untuk display host dan port info
hostNport = tk.Frame(window)
lebelHost = tk.Label(hostNport, text = "Host: X.X.X.X")
lebelHost.pack(side=tk.LEFT)
lebelPort = tk.Label(hostNport, text = "Port:XXXX")
lebelPort.pack(side=tk.LEFT)
hostNport.pack(side=tk.TOP, pady=(5, 0))

# client farme yang menampilkan client area
clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text=" Client List ").pack()
scrollBar = tk.Scrollbar(clientFrame) #untuk slide controller
scrollBar.pack(side=tk.RIGHT, fill=tk.Y) #untuk slide controller
tkDisplay = tk.Text(clientFrame, height=15, width=35) # ukuran framenya
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))

# network server
server = None
alamatHost = "192.168.1.4"
alamatPort = 5000
namaClient = " "
clients = []
namaClientClient = []

# Fungsi start server
def serverStart():
    tombolStart.config(state=tk.DISABLED)
    tombolStop.config(state=tk.NORMAL)

    # buat server socket IPv4 (socket.AF_INET) dan TCP protocol (socket.SOCK_STREAM)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(socket.AF_INET)
    print(socket.SOCK_STREAM)
    
    # server binding address dan port
    server.bind((alamatHost, alamatPort))
    
    # server is listening untuk client connection
    server.listen(5)  

    #thread baru menerima new clients connection
    threading._start_new_thread(terimaClient, (server, " "))

    #untuk menampilkan host dan port yang terhubung di server
    lebelHost["text"] = "Host: " + alamatHost
    lebelPort["text"] = "Port: " + str(alamatPort)


# fungsi stop server
def serverStop():
    global server
    #agar tombol stop berfungsi 
    tombolStart.config(state=tk.NORMAL)
    tombolStop.config(state=tk.DISABLED)

#server menerima request koneksi client-client baru, 
#dan informasi client akan di store di dalam list yaitu clients 
def terimaClient(the_server, y):
    while True:
        client, addr = the_server.accept()
        clients.append(client)
        
        #start new thread untuk handle sending/recieve pesan dari client-client
        threading._start_new_thread(sendPesanClientYangDiterima, (client, addr))


# untuk menerima message dari current client 
# dan mengirim pesan tersebut ke client-client lainnya
def sendPesanClientYangDiterima(koneksiClient, clientIpAddr):
    global server, namaClient, clients, clientsAddr
    pesanClient = " "

    # send welcome message to client
    # jika ada client baru connect, maka client akan mengirim nama ke server
    # lalu server menerimanya dengan socket.recv method
    namaClient  = koneksiClient.recv(4096).decode() #ukuran buffer
    pesanAwal = "Welcome " + namaClient + ". Use 'exit' to quit"
    
    # mengirim isi pesanAwal
    koneksiClient.send(pesanAwal.encode())
    namaClientClient.append(namaClient)

    # update display nama client
    updateDisplayNamaClient(namaClientClient)  

    while True:
        data = koneksiClient.recv(4096).decode()
        if not data: break
        if data == "exit": break

        pesanClient = data
        
        # me-return current client index yang ada pada client list
        # jadi ini bertujuan untuk mengetahui client index
        # dan aplikasi ini dapat mengirim pesan ke semua client yang connect
        idx = getIndexClient(clients, koneksiClient)
        kirimNamaClient = namaClientClient[idx]

        for c in clients:
            if c != koneksiClient:
                pesanServer = str(kirimNamaClient + "->" + pesanClient)
                c.send(pesanServer.encode())

    # mencari client index, lalu hapus dari list (list nama client dan list connection)
    idx = getIndexClient(clients, koneksiClient)
    del namaClientClient[idx] # hapus client ketika pesan exit
    del clients[idx] # hapus client ketika pesan exit

    pesanServer = "Sampai Jumpa!"
    koneksiClient.send(pesanServer.encode())
    koneksiClient.close()

    #update nama client di display
    updateDisplayNamaClient(namaClientClient) 


# return index dari current client pada list clients
def getIndexClient(listClient, currentClient):
    idx = 0
    for cc in listClient:
        if cc == currentClient:
            break
        idx = idx + 1
    return idx

# mengupdate display nama client ketika ada client baru yang connect atau
# ketika client ada yang disconnect
def updateDisplayNamaClient(listNama):
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in listNama:
        tkDisplay.insert(tk.END, c+"\n") #agar ada spasi
    tkDisplay.config(state=tk.DISABLED)

window.mainloop()