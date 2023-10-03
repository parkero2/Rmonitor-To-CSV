import socket

ADDRESS = '127.0.0.1'
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

registered_competitors = [] #list of competitor objects ordered by their position in the race
header = ""
output = open("output.csv", "w")
linelog = open("log.txt", "w")

def update_positions():
    output.seek(0)
    output.write(header)
    output.write("\n")
    for i in range(len(registered_competitors)):
        output.write(f"{(registered_competitors[i].first_name + registered_competitors[i].last_name)}, {registered_competitors[i].first_name[0]}.{registered_competitors[i].last_name}, {registered_competitors[i].num}, ")

def parse_comp_stream(line : list):
    # $A,”1234BE”,”12X”,52474,”John”,”Johnson”,”USA”
    # competitor, reg_number, car_num, class, first name, last name, country
    global registered_competitors, header
    for i in range(len(registered_competitors)):
        if (registered_competitors[i].reg_num == line[1]):
            return
    # New competitor
    print(line)
    registered_competitors.append(competitor(line[1], line[2], line[3], line[4], line[5], line[6], line[7]))
    print(f"New competitor {registered_competitors[-1].first_name} {registered_competitors[-1].last_name} registered with car number {registered_competitors[-1].num}. There are now {len(registered_competitors)} competitors.")
    header += f"Name{len(registered_competitors)}, Short Name{len(registered_competitors)}, Car{len(registered_competitors)},"
    update_positions()
    
def parse_pos_stream(line : list):
    # $G,3,”1234BE”,14,”01:12:47.872”
    # Race update, position, reg_number, lap, time
    
    # Position change, update positions list according to the position change
    global registered_competitors
    affectedRacer = None
    for i in range(len(registered_competitors)):
        if (registered_competitors[i].reg_num == line[2]):
            affectedRacer = registered_competitors[i]
            if i > int(line[1]):
                registered_competitors.insert(int(line[1]), affectedRacer)
                registered_competitors.pop(i+1)
            elif i < int(line[1]):
                registered_competitors.insert(int(line[1]), affectedRacer)
                registered_competitors.pop(i)
    update_positions()

def logKeep(line : str):
    linelog.write(",".join(line) + "\n")

def main():
    # Clear the log
    linelog.seek(0)
    linelog.write("")
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ADDRESS, PORT))
    while True:
        data = s.recv(1024).decode("utf-8")
        if (not data):
            break
        # Parse the data beginning with $A or $G. There may be more than one occourance of $A or $G in the data
        
        data = data.split(',')
        if (data[0] == '$A'):
            parse_comp_stream(data)
            logKeep(data)
        elif (data[0] == '$G'):
            parse_pos_stream(data)
            logKeep(data)
        
    s.close()

if __name__ == "__main__":
    main()