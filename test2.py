import socket
import time

positions = [] # Array of competitor objects
racers = 0
header = ""
outfile = open("output.csv", "w")
log = open("log.txt", "w")
competitors = []
regos = []

ADDRESS = "127.0.0.1"
PORT = 50000

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
    global positions, outfile, header, racers
    with open('output_summary.txt', "+a") as f:
        for i in range(racers):
            f.write(f"{positions[i].first_name} {positions[i].last_name}, {positions[i].first_name[0]}.{positions[i].last_name}, {positions[i].num}\n")
        f.write("\n")
    lines_to_write = []
    for i in range(racers):
        lines_to_write.append(f"{positions[i].first_name} {positions[i].last_name}, {positions[i].first_name[0]}.{positions[i].last_name}, {positions[i].num}")
    outfile.seek(0)
    outfile.write("\n".join([header, ",".join(lines_to_write)]))

def parse_stream(line : str):
    global competitors, racers, header, positions, regos, log
    line = line.split(',')
    if (line[0] == "$A"):
        log.write(f"{line}\n")
        # Competitor
        if (line[1] in regos):
            return
    
        competitors.append(competitor(line[1], line[2], line[3], line[4], line[5], line[6], line[7]))
        positions.append(competitors[-1])
        racers = len(competitors)
        header += f"Name{racers}, Short Name{racers}, Car{racers}, "
        regos.append(line[1])
        print(f"Added competitor {line[4]} {line[5]} rego {line[1]}")

    if (line[0] == "$G"):
        # position change
        log.write(f"{line}\n")
        racer = None
        for i in range(len(positions)):
            if (positions[i].reg_num == line[2]):
                racer = i 
                break
        if (racer == None):
            return print(f"Racer {line[2]} not found")
        print(f"Racer {line[2]} found at position {racer + 1}")
        positions.insert(int(line[1]) - 1, positions.pop(racer))
        position_update()

# TESTING
with open("sample.txt", "r") as f:
    for line in f:
        parse_stream(line)
        time.sleep(0.00001)

# print(len(competitors))

if __name__ == "__main__":
    log.seek(0)
    log.write("")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ADDRESS, PORT))
    while True:
        data = s.recv(1024)
        if not data:
            break
        parse_stream(data.decode('utf-8'))