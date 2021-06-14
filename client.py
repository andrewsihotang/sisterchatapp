#menggunakan GUI library Tkinter 
import tkinter as tk
from tkinter import messagebox

#untuk socket
import socket

#untuk thread
import threading

window = tk.Tk()
window.title("Client")
username = " "

frameAtas = tk.Frame(window)
isiUsername = tk.Label(frameAtas, text = "Name:").pack(side=tk.LEFT) #isi name dari client
isiUsername2 = tk.Entry(frameAtas) #menampilkan box untuk isi nama
isiUsername2.pack(side=tk.LEFT) #menampilkan box untuk isi nama
tombolConnect = tk.Button(frameAtas, text="Connect", command=lambda : connect()) #button connect client
tombolConnect.pack(side=tk.LEFT)
frameAtas.pack(side=tk.TOP) #menampilkan nama dan button connect diatas

displayFrame = tk.Frame(window)
lblLine = tk.Label(displayFrame, text=" ").pack()
scrollBar = tk.Scrollbar(displayFrame) #untuk slide controller 
scrollBar.pack(side=tk.RIGHT, fill=tk.Y) #tampilkan slide controller 
tkDisplay = tk.Text(displayFrame, height=20, width=55) #framenya
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="blue") #untuk membuat message sendiri menjadi biru
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
displayFrame.pack(side=tk.TOP) #untuk menampilkan pesan displaynya


frameBawah = tk.Frame(window)
kirimPesan = tk.Text(frameBawah, height=2, width=55) #size
kirimPesan.pack(side=tk.LEFT, padx=(5, 13), pady=(5, 10))
kirimPesan.config(highlightbackground="grey", state="disabled")
kirimPesan.bind("<Return>", (lambda event: getPesanChat(kirimPesan.get("1.0", tk.END))))
frameBawah.pack(side=tk.BOTTOM) #menampilkan dibawah

# ketika button click ditrigger akan memanggil fungsi connect ini
# fungsi ini mengecek username apakah sudah di masukkan sebelum mencoba untuk connect ke server
# setelah itu akan memanggil fungsi connectKeServer
def connect():
    global username, client
    if len(isiUsername2.get()) < 1:
        #memunculkan error kalau belum tulis nama sebelum connect
        tk.messagebox.showerror(title="ERROR!!!", message="You must enter a name!")
    else:
        username = isiUsername2.get()
        connectKeServer(username)


# network client
client = None
alamatHost = "192.168.1.4"
alamatPort = 5000


# fungsi untuk connect ke server 
def connectKeServer(name):
    global client, alamatPort, alamatHost
    try:
        # buat client socket IPv4 (socket.AF_INET) dan TCP protocol (socket.SOCK_STREAM)
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((alamatHost, alamatPort)) 
        client.send(name.encode()) # mengirim nama ke server setelah connecting

        isiUsername2.config(state=tk.DISABLED)
        tombolConnect.config(state=tk.DISABLED)
        kirimPesan.config(state=tk.NORMAL)

        # memulai thread untuk terus menerima message dari server
        threading._start_new_thread(menerimaPesanDariServer, (client, "m"))
    except Exception as e:
        # menampilkan pesan error ketika tidak bisa connect ke ip ataupun port yang dituju
        tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + alamatHost + " on port: " + str(alamatPort) + ". Try again later")


# fungsi ini yaitu, loop yang dibuat untuk terus menerima message dari server (via client socket)
# pesan yang diterima akan di tambahkan di client chat display area  
def menerimaPesanDariServer(sck, m):
    while True:
        from_server = sck.recv(4096).decode() #buffer size

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


def getPesanChat(pesan):
    pesan = pesan.replace('\n', '')
    texts = tkDisplay.get("1.0", tk.END).strip()

    # enable area displaynya lalu insert pesan dan disable kembali
    tkDisplay.config(state=tk.NORMAL) #enable
    if len(texts) < 1:
        # untuk konfigurasi message yang masuk, merubah menjadi text biru
        tkDisplay.insert(tk.END, "You->" + pesan, "tag_your_message")
    else:
        tkDisplay.insert(tk.END, "\n\n" + "You->" + pesan, "tag_your_message")

    tkDisplay.config(state=tk.DISABLED) #disable

    # memanggil fungsi kirimPesanKeServer agar client-client yang connect dapat melihat semua pesan 
    kirimPesanKeServer(pesan)

    tkDisplay.see(tk.END)
    kirimPesan.delete('1.0', tk.END)

# mengirim pesan ke server dengan menggunakan send function dari socket object
# lalu close client socket dan menutup chat window jika user mengetik pesan exit 
def kirimPesanKeServer(pesan):
    pesanClient = str(pesan)
    client.send(pesanClient.encode())
    if pesan == "exit":
        client.close() # tutup koneksi
        window.destroy() # tutup window
    print("Sending message") #di terminal

window.mainloop()