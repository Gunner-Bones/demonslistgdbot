import socket, sys, os, ast, urllib.request, urllib.parse, json, requests

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
def getmods():
    ccl = "http://tmi.twitch.tv/group/user/" + CHANNEL + "/chatters"
    ccl = urllib.request.Request(ccl, headers={'User-Agent': 'Mozilla/5.0'})
    ccl = str(urllib.request.urlopen(ccl).read())
    ccmi = ccl.index("\"moderators\": ")
    ccbi = ccl.index("]")
    ccl = ccl[ccmi + 15:ccbi]
    ccl = ccl.replace("\\n", "")
    ccl = ccl.replace(" ", "")
    ccl = ccl.replace("\"", "")
    ccl = ccl.split(",")
    global MODS
    MODS = ccl
getmods()

#DEMONS LIST MODERATORS
DLMODS = []

def userindlmods(username):
    found = False
    for d in DLMODS:
        if d['name'] == username:
            found = True
    return found

# GLOBAL BOOLEANS
MODSONLY = False

# CONSTANTS
DEMONSLISTSIZE = 0
dls = requests.get("https://pointercrate.com/api/v1/demons?position__gt=100")
dls = dls.json(); dls = len(dls); dls += 100
DEMONSLISTSIZE = dls

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
    if headers is None: rq = requests.get(baseurl,params=({'User-Agent': 'Mozilla/5.0'}))
    else: rq = requests.get(baseurl,params=({'User-Agent': 'Mozilla/5.0'},headers))
    try:
        rq = rq.json()
    except Exception as e:
        print(e)
        return None
    if len(rq) == 1: return rq[0]
    return rq

def POST(url,data,headers=None):
    baseurl = "https://pointercrate.com/api/v1/" + url
    if headers is None: rq = requests.post(baseurl,data=data,headers=({'User-Agent': 'Mozilla/5.0'}))
    else: rq = requests.post(baseurl,data=data,headers=({'User-Agent': 'Mozilla/5.0'},headers))
    try:
        rq = rq.json()
    except Exception as e:
        print(e)
        return None
    return rq

def PATCH(url,data,headers=None):
    baseurl = "https://pointercrate.com/api/v1/" + url
    if headers is None: rq = requests.patch(baseurl,data=data,headers=({'User-Agent': 'Mozilla/5.0'}))
    else: rq = requests.patch(baseurl,data=data,headers=({'User-Agent': 'Mozilla/5.0'},headers))
    try:
        rq = rq.json()
    except Exception as e:
        print(e)
        return None
    return rq

def formatREQUESTforTM(rqm):
    rqm = str(rqm)
    if len(rqm) > 50:
        rqm = rqm[:200]
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
                        getmods()
                        if username not in MODS and not userindlmods(username):
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
                    if message == ">>modsonly":
                        getmods()
                        if username != CHANNEL:
                            if username not in MODS and not userindlmods(username):
                                Send_message(username + ", you do not have permissions to do this!", username,messagewhisper)
                        else:
                            if MODSONLY:
                                Send_message("Commands are now Mods Only!",username,messagewhisper)
                                MODSONLY = True
                            else:
                                Send_message("Commands are now for everyone!",username,messagewhisper)
                                MODSONLY = False
                    if message.startswith(">>demon"):
                        cmdpass = False
                        if MODSONLY:
                            if username not in MODS:
                                if username not in MODS and not userindlmods(username):
                                    Send_message(username + ", you do not have permissions to do this!", username,messagewhisper)
                            else: cmdpass = True
                        else: cmdpass = True
                        if cmdpass:
                            tm = message.replace(">>demon ","")
                            tmint = False
                            try:
                                tm = int(tm)
                                tmint = True
                            except:
                                dr = GET(url="demons?name=" + tm)
                                if dr is None or dr == []:
                                    Send_message(username + ", no Demon found with that name on the List!",username,messagewhisper)
                                else:
                                    Send_message("#" + str(dr['position']) + ": " + dr['name'],username,messagewhisper)
                            if tmint:
                                if tm > DEMONSLISTSIZE or tm < 1:
                                    Send_message(username + ", that number is out of range!",username,messagewhisper)
                                else:
                                    dr = GET(url="demons?position=" + str(tm))
                                    if dr is None or dr == []:
                                        Send_message(username + ", no Demon found with that position on the List!",username,messagewhisper)
                                    else:
                                        Send_message("#" + str(dr['position']) + ": " + dr['name'],username,messagewhisper)
                    if message.startswith(">>newdemon"):
                        if not userindlmods(username):
                            Send_message(username + ", you do not have permissions to do this!", username,
                                         messagewhisper)
                        else:
                            if message == ">>newdemon":
                                Send_message("Usage: >>newdemon name;pos;requirement;verifier;publisher;"
                                             "[creator1,creator2];video",username,messagewhisper)
                            else:
                                tm = message.replace(">>newdemon ","")
                                tm = tm.split(";")
                                if len(tm) != 7:
                                    Send_message(username + ", Invalid Syntax! Usage: >>newdemon name;pos;requirement;"
                                                            "verifier;publisher;[creator1,creator2];video", username,
                                                            messagewhisper)
                                else:
                                    DLTOKEN = ""
                                    for d in DLMODS:
                                        if d['name'] == username:
                                            DLTOKEN = d['access token']
                                    ndvalid = True
                                    NDNAME = tm[0]
                                    NDPOS = 0
                                    try:
                                        NDPOS = int(tm[1])
                                    except:
                                        ndvalid = False
                                        Send_message(
                                            username + ", Invalid Position! Usage: >>newdemon name;pos;requirement;"
                                                       "verifier;publisher;[creator1,creator2];video", username,
                                            messagewhisper)
                                    NDREQUIREMENT = 0
                                    try:
                                        NDREQUIREMENT = int(tm[2])
                                    except:
                                        ndvalid = False
                                        Send_message(
                                            username + ", Invalid Requirement! Usage: >>newdemon name;pos;requirement;"
                                                       "verifier;publisher;[creator1,creator2];video", username,
                                            messagewhisper)
                                    if NDREQUIREMENT < 1 or NDREQUIREMENT > 99:
                                        ndvalid = False
                                        Send_message(
                                            username + ", Invalid Requirement! Usage: >>newdemon name;pos;requirement;"
                                                       "verifier;publisher;[creator1,creator2];video", username,
                                            messagewhisper)
                                    NDVERIFIER = tm[3]
                                    NDPUBLISHER = tm[4]
                                    NDCREATORS = tm[5]
                                    if NDCREATORS[0] != "[" or NDCREATORS[len(NDCREATORS) - 1] != "]":
                                        ndvalid = False
                                        Send_message(
                                            username + ", Invalid Creators! Usage: >>newdemon name;pos;requirement;"
                                                       "verifier;publisher;[creator1,creator2];video", username,
                                            messagewhisper)
                                    NDCREATORS = NDCREATORS.replace("[",""); NDCREATORS = NDCREATORS.replace("]","")
                                    NDCREATORS = NDCREATORS.split(",")
                                    NDVIDEO = tm[6]
                                    if not NDVIDEO.startswith("https://www.youtube.com/"):
                                        ndvalid = False
                                        Send_message(
                                            username + ", Invalid Video! Usage: >>newdemon name;pos;requirement;"
                                                       "verifier;publisher;[creator1,creator2];video", username,
                                            messagewhisper)
                                    if ndvalid:
                                        ndr = POST("demons/",data={'name':NDNAME,'position':NDPOS,
                                        'requirement':NDREQUIREMENT,'verifier':NDVERIFIER,'publisher':NDPUBLISHER,
                                        'creators':NDCREATORS,'video':NDVIDEO},headers={'Authorization':'Bearer ' +
                                                                                                        DLTOKEN})
                                        if ndr is None or ndr == []:
                                            Send_message(username + ", Invalid Request!",username,messagewhisper)
                                        else:
                                            Send_message(username + ", added demon " + NDNAME + "!",username,
                                                         messagewhisper)
                    if message.startswith(">>modifydemon"):
                        if not userindlmods(username):
                            Send_message(username + ", you do not have permissions to do this!", username,
                                         messagewhisper)
                        else:
                            if message == ">>modifydemon":
                                Send_message("Usage: >>modifydemon position_to_modify field [new value]",username,
                                             messagewhisper)
                            else:
                                tm = message.replace(">>modifydemon","")
                                tm = tm.split(" ")
                                if len(tm) < 3:
                                    Send_message("Invalid Syntax! Usage: >>modifydemon position_to_modify field "
                                                 "[new value]", username,messagewhisper)
                                else:
                                    mdvalid = True
                                    MDPOS = tm[0]
                                    try:
                                        MDPOS = int(MDPOS)
                                    except:
                                        mdvalid = False
                                        Send_message("Invalid Position! Usage: >>modifydemon position_to_modify field "
                                                     "new_value", username, messagewhisper)
                                    MDFIELD = tm[1].lower()
                                    mdacceptable = ['name','position','video','requirement',
                                                    'verifier','publisher','notes']
                                    if MDFIELD not in mdacceptable:
                                        mdvalid = False
                                        Send_message("Invalid Field! Usage: >>modifydemon position_to_modify field "
                                                     "new_value", username, messagewhisper)
                                    tm.remove(tm[0]); tm.remove(tm[1])
                                    MDVALUE = ""
                                    for m in tm:
                                        MDVALUE += m + " "
                                    MDVALUE = MDVALUE[:len(MDVALUE) - 1]
                                    if MDFIELD == "position" or MDFIELD == "requirement":
                                        try:
                                            MDVALUE = int(MDVALUE)
                                        except:
                                            mdvalid = False
                                            Send_message(
                                                "Invalid Value! Usage: >>modifydemon position_to_modify field "
                                                "new_value", username, messagewhisper)
                                    DLTOKEN = ""
                                    for d in DLMODS:
                                        if d['name'] == username:
                                            DLTOKEN = d['access token']
                                    mdr = PATCH("records/" + str(MDPOS),data={MDFIELD:MDVALUE},
                                        headers={'Authorization':'Bearer ' + DLTOKEN})
                                    if mdr is None or mdr == []:
                                        Send_message(username + ", Invalid Request!", username, messagewhisper)
                                    else:
                                        Send_message(username + ", Demon Modified! " + MDFIELD + ": " + str(MDVALUE),
                                                     username,messagewhisper)
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