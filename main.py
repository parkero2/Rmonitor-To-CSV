import tkinter as tk
import socket
import time
import socketserver
import flask
import threading
import asyncio
from aiohttp import web
from pythonosc import udp_client

positions = [] # Array of competitor objects
racers = 0
header = "Laps, Race Name, Race Category,"
outfile = open("output.csv", "w")
competitors = []
regos = []
highest_lap = 0
race_name = ""

#OSC STUFF
OSCIP, OSCPORT = "127.0.0.1", 50000
OSCMSG = {
    "red": "/red",
    "yellow": "/yellow",
    "green": "/green",
    "purple": "/purple",
    "checkered": "/checkered"
}

flag = OSCMSG["green"]

OSCUDP_CLIENT = udp_client.SimpleUDPClient(OSCIP, OSCPORT)

ADDRESS = "127.0.0.1"
PORT = 50000

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        # IP address input field
        self.ip_label = tk.Label(self, text="IP Address:")
        self.ip_label.pack(side="left")
        self.ip_entry = tk.Entry(self)
        self.ip_entry.pack(side="left")

        # Port number input field
        self.port_label = tk.Label(self, text="Port Number:")
        self.port_label.pack(side="left")
        self.port_entry = tk.Entry(self)
        self.port_entry.pack(side="left")

        # Connect button
        self.connect_button = tk.Button(self, text="Connect", command=self.connect)
        self.connect_button.pack(side="left")

        # Disconnect button
        self.disconnect_button = tk.Button(self, text="Disconnect", command=self.disconnect, state="disabled")
        self.disconnect_button.pack(side="left")

        # Quit button
        self.quit_button = tk.Button(self, text="Quit", fg="red", command=self.master.destroy)
        self.quit_button.pack(side="left")

        # Output section
        self.output_label = tk.Label(self, text="Output:")
        self.output_label.pack()
        self.output_text = tk.Text(self, height=10, width=50)
        self.output_text.pack()

        # RMonitor log section
        self.log_label = tk.Label(self, text="RMonitor Log:")
        self.log_label.pack()
        self.log_text = tk.Text(self, height=10, width=50)
        self.log_text.pack()

    def connect(self):
        global ADDRESS, PORT
        ADDRESS = self.ip_entry.get()
        PORT = int(self.port_entry.get())
        # TODO: Implement connection logic here
        self.connect_button.config(state="disabled")
        self.disconnect_button.config(state="normal")

    def disconnect(self):
        # TODO: Implement disconnection logic here
        self.connect_button.config(state="normal")
        self.disconnect_button.config(state="disabled")

root = tk.Tk()
app = Application(master=root)
app.mainloop()
class competitor:
    def __init__(self, reg_num, num, trans_num, first_name, last_name, nationality, class_num) -> None:
        self.reg_num = reg_num
        self.num = num
        self.trans_num = trans_num
        if (first_name == ""):
            self.first_name = last_name.split(" ")[0]
            last_name = " ".join(last_name.split(" ")[1:])
        self.first_name = first_name
        self.last_name = last_name
        self.nationality = nationality
        self.class_num = class_num

def position_update():
    # Updates the CSV
    # Laps	Race Name	Race Category	Name1	        Short1	Reg1
    # 51/54	Formula 1	Bikes	        Lewis Hamilton	L.HAM	4
    global positions, outfile, header, racers, highest_lap, race_name
    if (race_name == ""):
        rn = "NotSet"
    else:
        rn = race_name
    linesToWrite = [f"{highest_lap}, {rn}, Bikes "]
    outfile.seek(0)
    outfile.write(header)
    outfile.write("\n")
    for i in range(racers):
        linesToWrite.append(f"{str(positions[i].first_name + ' ' + positions[i].last_name)}, {positions[i].first_name[1]}.{positions[i].last_name}, {positions[i].reg_num[1:-1]}, ?")
    outfile.write(",".join(linesToWrite))
    outfile.flush()
    print("Updated positions")

def parse_stream(line : str):
    global competitors, racers, header, positions, regos, highest_lap, flag, OSCMSG
    line = line.split(',')
    if (line[0] == "$A"):
        # Competitor
        reg_num = line[1]
        print(line)
        if any(comp.reg_num == reg_num for comp in competitors):
            return
        
        competitors.append(competitor(reg_num, line[2], line[3][1:-1], line[4][1:-1], line[5][1:-1], line[6], line[7]))
        positions.append(competitors[-1])
        racers = len(competitors)
        header += f"Name{racers}, Short Name{racers}, Car{racers}, Laps{racers},"
        print(f"Added competitor {line[4]} {line[5]} rego {reg_num}")

    if (line[0] == "$C"):
        global race_name
        print(line)
        if race_name == "":
            race_name = line[2].split('"')[1]

    if (line[0] == "$G"):
        # position change
        racer = None
        for i in range(len(positions)):
            if (positions[i].reg_num == line[2]):
                racer = i 
                break
        new_pos = int(line[1]) - 1
        if racer is not None:
            #highest_lap = max(highest_lap, int(line[3]) if line[3] != "" else -1)
            if new_pos < racer:
                positions.insert(new_pos, positions[racer])
                positions.pop(racer + 1)
            elif new_pos > racer:
                positions.insert(new_pos, positions[racer])
                positions.pop(racer)
            position_update() 
    if (line[0] == "$F"):
        highest_lap = int(line[1])
        flag = OSCMSG[line[5].lower()]
        bcast_OSC()

def bcast_OSC():
    # OSC
    global flag, OSCUDP_CLIENT
    OSCUDP_CLIENT.send_message(flag, 1)


if False:
    with open('sample.txt', 'r') as f:
        for line in f:
            parse_stream(line)
            time.sleep(0.0001)

# SERVER STUFF DON'T TOUCH IT'S PROBABLY WORKING

WSHOST, WSPORT, SOCKHOST, SOCKPORT = "127.0.0.1", 8080, "127.0.0.1", 9999

async def main():
    global ADDRESS, PORT
    # Run runServer() asynchronusly

    # Connect to the socket server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ADDRESS, PORT))

    # Process incoming data from the socket server
    while True:
        data = s.recv(1024)
        if not data:
            break
        d = data.decode("utf-8")
        for line in d.split("\n"):
            parse_stream(line)

if __name__ == "__main__":
    asyncio.run(main())