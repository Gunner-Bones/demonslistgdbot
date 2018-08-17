import socket, sys, os, ast, urllib.request, urllib.parse, json

try:
    tf = open("dlpass.txt","r")
    tf.close()
except:
    tf.close()
    print("[ERROR] There needs to be a file called 'dlpass.txt' in order for the bot to run! Format:")
    print("CHANNEL=<channel to connect to>")
    print("NICK=<bot username to use>")
    print("PASS=<bot's authorization token>")
    sys.exit()

cp = open("dlpass.txt","r")
cpl = []
for line in cp:
    cpl.append(line.replace("\n",""))
CHANNEL = str(cpl[0]).replace("CHANNEL=","")
NICK = str(cpl[1]).replace("NICK=","")
PASS = str(cpl[2]).replace("PASS=","")

HOST = "irc.twitch.tv"
PORT = 6667
readbuffer = ""
MODT = False

# Connecting to Twitch IRC by passing credentials and joining a certain channel
s = socket.socket()
s.connect((HOST, PORT))
s.send(("PASS " + PASS + "\r\n").encode("UTF-8"))
s.send(("NICK " + NICK + "\r\n").encode("UTF-8"))
s.send(("JOIN #" + CHANNEL + " \r\n").encode("UTF-8"))
s.send(("CAP REQ :twitch.tv/commands \r\n").encode("UTF-8"))

print(NICK + "[Bot Ready]")
print(NICK + "[Info] Channel: " + CHANNEL + ", PORT: " + str(PORT))


# MODERATORS
MODS = []
ccl = "http://tmi.twitch.tv/group/user/" + CHANNEL + "/chatters"
ccl = urllib.request.Request(ccl, headers={'User-Agent': 'Mozilla/5.0'})
ccl = str(urllib.request.urlopen(ccl).read())
ccmi = ccl.index("\"moderators\": ")
ccbi = ccl.index("]")
ccl = ccl[ccmi + 15:ccbi]
ccl = ccl.replace("\\n","")
ccl = ccl.replace(" ","")
ccl = ccl.replace("\"","")
ccl = ccl.split(",")
MODS = ccl

#DEMONS LIST MODERATORS
DLMODS = []

SETTINGSFILE = "dlauth.txt"
HASSETTINGS = True

try:
    st = open("dlauth.txt","r")
    st.close()
except:
    st.close()
    print("[ERROR] A settings file needs to be put with the program called 'dlauth.txt' for Authorizations"
          " to be stored. Authorizations will only persist for this session now.")
    HASSETTINGS = False

def printMods():
    cm = ""
    for m in MODS:
        cm += m + " "
    print(NICK + "[Connected Mods] " + cm)
printMods()

def Send_message(message,username,iswhisper):
    if not iswhisper:
        s.send(("PRIVMSG #" + CHANNEL + " :" + message + "\r\n").encode("UTF-8"))
        print(NICK + "[Send Message] " + message)
    else:
        s.send(("PRIVMSG #" + CHANNEL + " :/w " + username + " [" + CHANNEL + "] " + message + "\r\n").encode("UTF-8"))
        print(NICK + "[Send Whisper](Channel: " + CHANNEL + ") " + message)

def settings(method,name,data="",file=SETTINGSFILE):
    """
    :param file: Filename
    :param method: (get=Return data at name,change=Change data at name)
    :param name: Name location to change/retrieve data
    :param data: New data if changing data
    :return: data if method=get, otherwise None
    """
    if not HASSETTINGS: return None
    global DLMODS
    if method == "get":
        sf = open(file,"r")
        sfl = []
        for line in sf:
            sfl.append(line.replace("\n",""))
        for l in sfl:
            lph = l.split("=")
            if lph[0] == name:
                sf.close()
                if lph[1].startswith("{"): return ast.literal_eval(lph[1])
                else: return lph[1]
    elif method == "change":
        sf = open(file, "r")
        sfl = []
        for line in sf:
            sfl.append(line.replace("\n", ""))
        cl = ""
        for l in sfl:
            lph = l.split("=")
            if lph[0] == name:
                cl = lph[0] + "=" + data
                sfl[sfl.index(l)] = cl
        sfn = ""
        for l in sfl:
            sfn += l + "\n"
        sf.close()
        if cl != "":
            sf = open(file,"w")
            sf.truncate(); sf.write(sfn)
            sf.close()
        return None

def adddlmod(user,at):
    global DLMODS
    DLMODS.append({'name':user,'access token':at})
    if HASSETTINGS:
        settings("change","dlmods",data=DLMODS)

def removedlmod(user):
    global DLMODS
    for m in DLMODS:
        if m['name'] == user:
            DLMODS.remove(m)
    if HASSETTINGS:
        settings("change","dlmods",data=DLMODS)

def getdlmodtoken(user):
    global DLMODS
    for m in DLMODS:
        if m['name'] == user:
            return m['access token']
    return None

def GET(url,headers=None):
    baseurl = "https://pointercrate.com/api/v1/" + url
    rq = None
    if headers != None: rq = urllib.request.Request(baseurl,headers=({'User-Agent': 'Mozilla/5.0'},headers))
    else: rq = urllib.request.Request(baseurl)
    try:
        rq = str(urllib.request.urlopen(rq).read())
    except Exception as e:
        print(e)
        return None
    json.loads(rq)
    return rq

def POST(url,params,headers=None):
    baseurl = "https://pointercrate.com/api/v1/" + url
    rq = urllib.parse.urlencode(params)
    if headers != None: rq = urllib.request.Request(baseurl,rq,headers=({'User-Agent': 'Mozilla/5.0'},headers))
    else: rq = urllib.request.Request(baseurl,rq,headers={'User-Agent': 'Mozilla/5.0'})
    try:
        rq = str(urllib.request.urlopen(rq).read())
    except Exception as e:
        print(e)
        return None
    json.loads(rq)
    return rq

def formatREQUESTforTM(rqm):
    rqm = str(rqm)
    if len(rqm) > 50:
        rqm = rqm[:50]
    return rqm

def dltokenheader(user):
    global DLMODS
    for m in DLMODS:
        if m['name'] == user:
            return {'Authorization':'Bearer ' + m['access token']}
    return None


print()
while True:
    readbuffer = readbuffer + s.recv(1024).decode("UTF-8")
    temp = readbuffer.split("\n")
    readbuffer = temp.pop()

    for line in temp:
        # Checks whether the message is PING because its a method of Twitch to check if you're afk
        if (line[0] == "PING"):
            s.send(("PONG %s\r\n" % line[1]).encode("UTF-8"))
        else:
            # Splits the given string so we can work with it better
            parts = line.split(":")

            if "QUIT" not in parts[1] and "JOIN" not in parts[1] and "PART" not in parts[1]:
                try:
                    # Sets the message variable to the actual message sent
                    message = parts[2][:len(parts[2]) - 1]
                except:
                    message = ""
                # Sets the username variable to the actual username
                usernamesplit = str(parts[1]).split("!")
                username = usernamesplit[0]

                messagewhisper = False
                mt = str(parts[1]).split(" ")
                if mt[1] == "PRIVMSG": messagewhisper = False
                elif mt[1] == "WHISPER": messagewhisper = True

                # Only works after twitch is done announcing stuff (MODT = Message of the day)
                if MODT:

                    # You can add all your plain commands here
                    if message == "Hey":
                        Send_message("Welcome to the stream, " + username,username,messagewhisper)

                    if message.startswith(">>authorize"):
                        if username != CHANNEL:
                            Send_message(username + ", you do not have permissions to do this!",username,messagewhisper)
                        else:
                            am = message.split(" ")
                            if len(am) != 3:
                                Send_message(username + ", invalid syntax! Usage: >>authorize <username> <access token>",username,messagewhisper)
                            else:
                                if getdlmodtoken(am[1]) == None:
                                    adddlmod(am[1],am[2])
                                    dls = ""
                                    if not HASSETTINGS: dls = " for this session"
                                    Send_message(username + ", set an Access Token to " + am[1] + dls,username,messagewhisper)
                                else:
                                    Send_message(username + ", " + am[1] + " is already authorized!",username,messagewhisper)
                    if message.startswith(">>unauthorize"):
                        if username != CHANNEL:
                            Send_message(username + ", you do not have permissions to do this!",username,messagewhisper)
                        else:
                            am = message.split(" ")
                            if len(am) != 2:
                                Send_message(username + ", invalid syntax! Usage: >>unauthorize <username>",username,messagewhisper)
                            else:
                                if getdlmodtoken(am[1]) == None:
                                    Send_message(username + ", " + am[1] + " is not authorized!", username,messagewhisper)
                                else:
                                    removedlmod(am[1])
                                    dls = ""
                                    if not HASSETTINGS: dls = " for this session"
                                    Send_message(username + ", removed Access Token from " + am[1] + dls, username,messagewhisper)
                    if message.startswith(">>directGET"):
                        if username not in MODS and username not in DLMODS:
                            Send_message(username + ", you do not have permissions to do this!",username,messagewhisper)
                        else:
                            dm = message.split(" ")
                            if len(dm) != 2:
                                Send_message(username + ", invalid syntax! Usage: >>directGET <url>",username,messagewhisper)
                            else:
                                dmr = GET(dm[1])
                                if dmr == None:
                                    Send_message(username + ", bad response! Check your url and see console", username,messagewhisper)
                                else:
                                    Send_message(username + ", " + formatREQUESTforTM(dmr), username,messagewhisper)
                for l in parts:
                    if "End of /NAMES list" in l:
                        MODT = True
                        print()
                if parts[0] == "PING ":
                    print(NICK + "[Ping]")
                else:
                    mes = NICK + "[Recieved Message|" + parts[1] + "] "
                    c = 0
                    for l in parts:
                        if c > 1:
                            mes += l
                        c += 1
                    if len(mes) > 8:
                        print(mes)