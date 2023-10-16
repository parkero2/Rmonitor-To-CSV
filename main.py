import socket
import time

positions = [] # Array of competitor objects
racers = 0
header = "Laps, Race Name, Race Category,"
outfile = open("output.csv", "w")
competitors = []
regos = []
highest_lap = 0
race_name = ""

ADDRESS = "115.188.181.165"
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
        self.lap = 0
        self.best_lap = 0
        self.last_lap_time = ""

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
        linesToWrite.append(f"{str(positions[i].first_name + ' ' + positions[i].last_name)}, {positions[i].first_name[0]}.{positions[i].last_name}, {positions[i].reg_num[1:-1]}, {positions[i].lap}, {positions[i].best_lap}, {positions[i].last_lap_time}")
    outfile.write(",".join(linesToWrite))
    outfile.flush()
    print("Updated positions")

def parse_stream(line : str):
    global competitors, racers, header, positions, regos, highest_lap, race_name
    line = line.split(',')
    if (line[0] == "$B"):
        race_name = line[2].strip("\r").strip('"')
    if (line[0] == "$A"):
        # Competitor
        reg_num = line[1]
        print(line)
        if any(comp.reg_num == reg_num for comp in competitors):
            return
        
        competitors.append(competitor(reg_num, line[2], line[3][1:-1], line[4][1:-1], line[5][1:-1], line[6], line[7]))
        positions.append(competitors[-1])
        racers = len(competitors)
        header += f"Name{racers}, Short Name{racers}, Car{racers}, Lap{racers}, Best Lap{racers}, Best Lap Time{racers},"
        print(f"Added competitor {line[4]} {line[5]} rego {reg_num}")
        position_update()

    if (line[0] == "$G"):
        # position change
        racer = None
        for i in range(len(positions)):
            if (positions[i].reg_num == line[2]):
                racer = i 
                break
        new_pos = int(line[1]) - 1
        if racer is not None:
            print(line[3])
            highest_lap = max(highest_lap, int(line[3]) if line[3] != "" else 0)
            positions[racer].lap = int(line[3]) if line[3] != "" else 0
            if new_pos < racer:
                positions.insert(new_pos, positions[racer])
                positions.pop(racer + 1)
            elif new_pos > racer:
                positions.insert(new_pos, positions[racer])
                positions.pop(racer)
            position_update()

    if (line[0] == "$H"):
        #$H,2,”1234BE”,3,”00:02:17.872”
        # lap time
        racer = None
        for i in range(len(positions)):
            if (positions[i].reg_num == line[2]):
                racer = i 
                break
        if racer is not None:
            print(line)
            positions[racer].last_lap_time = line[4].strip("\r").strip('"')
            position_update()



if False:
    with open('sample.txt', 'r') as f:
        for line in f:
            parse_stream(line)
            time.sleep(0.0001)

if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ADDRESS, PORT))
    while True:
        data = s.recv(1024)
        if not data:
            break
        d = data.decode("utf-8")
        for line in d.split("\n"):
            parse_stream(line)