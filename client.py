import tkinter as tk
from tkinter import messagebox
import socket
import threading

window = tk.Tk()
window.title("Client")
username = " "


frameAtas = tk.Frame(window)
lblName = tk.Label(frameAtas, text = "Name:").pack(side=tk.LEFT) #isi name dari client
entName = tk.Entry(frameAtas)
entName.pack(side=tk.LEFT)
btnConnect = tk.Button(frameAtas, text="Connect", command=lambda : connect()) #button connect client
btnConnect.pack(side=tk.LEFT)
frameAtas.pack(side=tk.TOP)

displayFrame = tk.Frame(window)
lblLine = tk.Label(displayFrame, text=" ").pack()
scrollBar = tk.Scrollbar(displayFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(displayFrame, height=20, width=55)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="blue") #untuk membuat message kita menjadi biru
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
displayFrame.pack(side=tk.TOP)


bottomFrame = tk.Frame(window)
tkMessage = tk.Text(bottomFrame, height=2, width=55)
tkMessage.pack(side=tk.LEFT, padx=(5, 13), pady=(5, 10))
tkMessage.config(highlightbackground="grey", state="disabled")
tkMessage.bind("<Return>", (lambda event: getChatMessage(tkMessage.get("1.0", tk.END))))
bottomFrame.pack(side=tk.BOTTOM)


# ketika button click diklik akan memanggil fungsi connect ini
# fungsi ini mengecek username apakah sudah di masukkan sebelum mencoba untuk connect ke server
# setelah itu akan memanggil fungsi connect_to_server
def connect():
    global username, client
    if len(entName.get()) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="You MUST enter your first name <e.g. John>")
    else:
        username = entName.get()
        connect_to_server(username)


# network client
client = None
HOST_ADDR = "192.168.1.4"
HOST_PORT = 5000


# fungsi untuk connect ke server 
def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR
    try:
        # buat client socket IPv4 (socket.AF_INET) dan TCP protocol (socket.SOCK_STREAM)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT)) 
        client.send(name.encode()) # mengirim nama ke server setelah connecting

        entName.config(state=tk.DISABLED)
        btnConnect.config(state=tk.DISABLED)
        tkMessage.config(state=tk.NORMAL)

        # memulai thread untuk terus menerima message dari server
        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        # menampilkan message ketika tidak bisa connect ke ip ataupun port yang dituju
        tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")


# fungsi ini yaitu, loop yang dibuat untuk terus menerima message dari server (via client socket)
# pesan yang diterima akan di tambahkan di client chat display area  
def receive_message_from_server(sck, m):
    while True:
        from_server = sck.recv(4096).decode()

        if not from_server: break

        # menampilakan message dari server di window chat
        # enable the display area and insert the text and then disable
        texts = tkDisplay.get("1.0", tk.END).strip()
        tkDisplay.config(state=tk.NORMAL)
        if len(texts) < 1:
            tkDisplay.insert(tk.END, from_server)
        else:
            tkDisplay.insert(tk.END, "\n\n"+ from_server)

        tkDisplay.config(state=tk.DISABLED)
        tkDisplay.see(tk.END)
    sck.close()  # tutup koneksi
    window.destroy() # tutup window


def getChatMessage(msg):

    msg = msg.replace('\n', '')
    texts = tkDisplay.get("1.0", tk.END).strip()

    # enable the display area and insert the text and then disable
    tkDisplay.config(state=tk.NORMAL)
    if len(texts) < 1:
        # untuk konfigurasi message yang masuk, merubah menjadi text biru
        tkDisplay.insert(tk.END, "You->" + msg, "tag_your_message") # no line
    else:
        tkDisplay.insert(tk.END, "\n\n" + "You->" + msg, "tag_your_message")

    tkDisplay.config(state=tk.DISABLED)

    # memanggil fungsi send_mssage_to_server agar client-client yang connect dapat melihat semua pesan 
    send_mssage_to_server(msg)

    tkDisplay.see(tk.END)
    tkMessage.delete('1.0', tk.END)

# mengirim pesan ke server dengan menggunakan send function dari socket object
# lalu close client socket dan menutup chat window jika user mengetik pesan exit 
def send_mssage_to_server(msg):
    client_msg = str(msg)
    client.send(client_msg.encode())
    if msg == "exit":
        client.close() # tutup koneksi
        window.destroy() # tutup window
    print("Sending message")

window.mainloop()
