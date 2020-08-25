from telethon import TelegramClient
from telethon.events import NewMessage,newmessage
from telethon.client import TelegramBaseClient
from telethon.tl.patched import Message
from telethon.errors.rpcerrorlist import ChatAdminRequiredError,UsernameNotModifiedError
from telethon import functions, types
import logging
from socks import SOCKS5
import shutil
from threading import Thread
import os
import asyncio
import datetime
import pytz
import random
os.environ['TZ'] = 'Asia/Tehran'

# Vars
API_ID = 1544711 # Edit Here
API_HASH = 'd04ebd2eea6942d8ff4a991d682eb6a7' # Edit Here
SUDOS = [1364455559,932528835] # Edit Here 
DEFAULT_LIMIT = 300 # Edit Here
DEFAULT_LIST = ''' # Edit Here
usernameufsjifjsdij1
usernameufsjifjsdij2
usernameufsjifjsdij3
usernameufsjifjsdij4
usernameufsjifjsdij5
usernameufsjifjsdij6
usernameufsjifjsdij7
usernameufsjifjsdij8
usernameufsjifjsdij9
usernameufsjifjsdij10
'''

client = TelegramClient('session',API_ID,API_HASH,
#proxy=(SOCKS5,'127.0.0.1',7372)
)

def convert_datetime_timezone(dt, tz1, tz2):
    tz1 = pytz.timezone(tz1)
    tz2 = pytz.timezone(tz2)

    dt = datetime.datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
    dt = tz1.localize(dt)
    dt = dt.astimezone(tz2)
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt

async def check_channels():
    while 1:
        print("while")
        chnls =  [i for i in open("channels/ids").read().strip().split("\n") if i not in ('',' ',None)]
        if len(chnls)<1:
            open("running","w").write("no")
            break
        for id in open("channels/ids").read().strip().split("\n"):
            dt = datetime.datetime.now()
            mint = str(dt.minute)
            dic = {}
            limit = int(open(f"channels/{id}/limit").read())
            async for h in client.iter_admin_log(await client.get_entity(int(id)),join=True,limit=int(limit)+10,invite=True):
                print(h.date)
                converted = convert_datetime_timezone(str(h.date).split("+")[0],'UTC','Asia/Tehran')
                date = datetime.datetime.strptime(converted, '%Y-%m-%d %H:%M:%S')
                if((int(date.minute) in list(range(int(mint)-1,int(mint)+2))) and (int(date.day)== int(dt.day)) and (int(date.hour) == int(dt.hour))):
                    print(f"int({date.minute}) in {list(range(int(mint)-1,int(mint)+2))}")
                    dic[f"{id}{date.day}{date.hour}{date.minute}"] = (dic.get(f"{id}{date.day}{date.hour}{date.minute}") or 0)+1
                    num = dic[f"{id}{date.day}{date.hour}{date.minute}"]
                    print(f"{num}>={limit}")
                    if(num>=limit):
                        res = await revoke_channel_link(id)
                        if res and res[0] == True:
                            try:
                                dic[f"{id}{date.day}{date.hour}{date.minute}"] = -int(limit)
                                del dic[f"{id}{date.day}{date.hour}{date.minute-1}"]
                            except Exception as ex: print(ex)
                            await client.send_message(SUDOS[0],f"Username {id} changed to {res[1]}")
                            
                    open("logs","a+").write(f"[{date.year}:{date.month}:{date.day} {date.time()}] | {id} => {num} member\n\n\n\n")
        await asyncio.sleep(20)

async def revoke_channel_link(id):
    lis = open(f"channels/{id}/list").read().strip().split("\n")
    last = open(f"channels/{id}/last").read()
    dt = datetime.datetime.now()
    while 1:
        idd = random.choice(lis)
        idd = idd.strip()
        if(idd.strip() == last.strip()): continue
        try:
            print(f"change to {idd} (TRY)")
            result = await client(functions.channels.UpdateUsernameRequest(
                channel=await client.get_input_entity(int(id)),
                username=idd
            ))
            open("logs","a+").write(f"{dt} | username {id} Changes to  {idd}\n\n")
            open(f"channels/{id}/last","w").write(idd)
            return True,idd
        except UsernameNotModifiedError:
            pass
        except Exception as ex:
            open("logs","a+").write(f"ERROR : {dt} | {id} => {ex}\n\n")
            break


folders = ['times','channels','tmp']

for folder in folders:
    if(not os.path.exists(folder)):
        os.mkdir(folder)
if(not os.path.exists('channels/ids')):
    open('channels/ids','w').write('')
if(not os.path.exists('logs')):
    open('logs','w').write('Nothing\n')
    
open('running','w').write('no')
    
logging.basicConfig(format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
                    level=logging.WARNING)

@client.on(NewMessage())
async def get_id(event:newmessage.NewMessage.Event):
    text = str(event.message.message)
    cid = event.chat_id
    if(text == "id"):
        await event.reply(f"`{cid}`")

@client.on(NewMessage(from_users=SUDOS))
async def admins(event:newmessage.NewMessage.Event):
    text = str(event.message.message)
    print(text)
    if(text.startswith("##")):
        command = text.replace("##","").strip()
        x = os.popen(command).read()
        await event.reply(f"**{command}**\n\n`{x}`")
    elif(text=="logs"):
        await client.send_file(event.chat_id,'./logs')
    elif(text.startswith("!add ")):
        channel = text.replace("!add ","")
        try:
            if(not channel.replace("-","").strip().isnumeric()):    
                await event.reply(f"{channel} is not numeric!")
                return
            msg = await client.send_message(int(channel),"This Is Test For Permission")
            await msg.delete()
            if str(channel) in open("channels/ids").read().strip().split("\n"):
                await event.reply("چنل موجود است")
                return
            open("channels/ids","a+").write(f"{channel}\n")
            os.makedirs(f"channels/{channel}")
            open(f"channels/{channel}/limit","w").write(f"{DEFAULT_LIMIT}")
            open(f"channels/{channel}/list","w").write(f"{DEFAULT_LIST}")
            open(f"channels/{channel}/last","w").write(f"")
            await event.reply(f"Channel `{channel}` Configed successfuly!\n\tlimit : {DEFAULT_LIMIT}")

        except ChatAdminRequiredError:
            await event.reply(f"ربات در چنل {channel} ادمین نیست")
        except Exception as ex:
            print(ex)
            print(type(ex))
            await event.reply(f"**Unknown Error**\n`{str(ex)[:600]}`\n\n**Report Bug to @The_Bloody**")
    elif(text.startswith("!setlimit ")):
        spli = text.split()
        if(not spli[2].isnumeric()):
            await event.reply("limit must be a number")
            return 
        if(not os.path.exists(f"channels/{spli[1]}")):
            await event.reply(f"channel `{spli[1]}` not found")
            return
        open(f"channels/{spli[1]}/limit","w").write(f"{spli[2]}")
        await event.reply(f"limit {spli[2]} seted for `{spli[1]}`")
    elif(text.startswith("!setlist ")):
        spli = text.split()
        print(event.message.is_reply)
        if(event.message.is_reply):
            if(not os.path.exists(f"channels/{spli[1]}")):
                await event.reply(f"channel {spli[1]} not found")
                return 
            replyed =await event.message.get_reply_message()
            fname = replyed.media.document.attributes[0].file_name+".txt".replace(" ","")
            await client.download_media(replyed,f"tmp/{fname}")        
            data = open(f"tmp/{fname}").read()
            open(f"channels/{spli[1]}/list","w").write(data)
            dn = len(data.strip().split('\n'))
            await event.reply(f"{dn} username loaded for channel `{spli[1]}`")
            os.remove(f"tmp/{fname}")
        else: await event.reply("you must reply this command on a file")
    elif(text.startswith("!remove ")):
        channel = text.replace("!remove ","")
        if(os.path.exists(f"channels/{channel}")):
            shutil.rmtree(f'channels/{channel}')
            open("channels/ids","w").write(open("channels/ids").read().replace(f"{channel}\n",""))
            await event.reply(f"`{channel}` removed")
        else: await event.reply(f"`{channel}` not found!")
    elif (text == "!channels"):
        char = ''
        for channel in open('channels/ids').read().strip().split("\n"):
            limit = open(f"channels/{channel}/limit").read()
            char += f"{channel=}\n{limit=}\n\n"
        await event.reply(char)
    elif (text == "run"):
        if(open("running").read() == 'no'):
            await event.reply("runned")
            open("running","w").write("yes")
            await check_channels()
        else: await event.reply("loop already is running ")
client.start()
print("R    U   N")
client.run_until_disconnected()


