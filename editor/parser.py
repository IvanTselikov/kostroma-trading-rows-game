#from bot import Bot
from bot_message import *

class Scene:
    """Класс сцены Telegram-бота"""

    def __init__(self, name, messages):
        self.sceneMessages = messages
        self.name = name

    def getName(self):
        return self.name

    def getSceneMessages(self):
        return self.sceneMessages

textFile = open("scenery.txt", "r", encoding='utf-8')
elements = []
token = ""
text = ""

# для сцен
currentName = ""
scenes = []
currentScene = None

def getSceneByName(sceneName):
    for sc in scenes:
        if sc.getName()==sceneName:
            return sc

# для группы
groupMessageFlag = False
textFound = False
groupMessage = []

# считываем строку
line = textFile.readline()

while True:
    # прерываем цикл, если строка пустая
    if not line:
        break
    string = ""
    for i in range(len(line)):
        if line[i]!="\t":
            string+=line[i]
            #print(string)
            if string == "бот \"" or string == "бот\"":
                j=i+1
                while (line[j]!='\"'):
                    token += line[j]
                    j+=1;
                print(token)
                line = textFile.readline()
                string = ""
                break
            elif string == "группа:":
                groupMessageFlag = True
                line = textFile.readline()
                string = ""
                break
            elif string == "конецГруппы":
                elements.append(GroupPost(groupMessage))
                textFound = False
                groupMessage = []
                line = textFile.readline()
                string = ""
                break
            elif string == "сцена":
                print("сцена найдена!")
                j = i + 1
                name = ""
                while (line[j] != '\"'):
                    name += line[j]
                    j += 1;
                currentName = name
                line = textFile.readline()
                string = ""
                break
            elif string == "конецСцены":
                scenes.append(Scene(currentName, elements))
                elements = []
                currentName = ""
                line = textFile.readline()
                string = ""
                break
            elif string == "текст\"" or string == "текст \"":
                print("текст найден!")
                j = i + 1
                while (line[j] != '\"'):
                    text += line[j]
                    j+=1;
                    if (j==len(line)):
                        #text += "\n"
                        line = textFile.readline().replace('\t', '')
                        j = 0
                text = text.replace("\\t", "\t")
                print("_____________")
                print (text)
                print("_____________")
                if groupMessageFlag:
                    if not textFound:
                        groupMessage.append(TextPost(text))
                        textFound = True
                else:
                    elements.append(TextPost(text))
                text = ""
                line = textFile.readline()
                string = ""
                break
            elif string == "фото\"" or string == "фото \"":
                j = i + 1
                photo=""
                while (line[j] != '\"'):
                    photo += line[j]
                    j += 1;
                print(photo)
                if groupMessageFlag:
                    groupMessage.append(ImagePost(photo))
                else:
                    elements.append(ImagePost(photo))
                line = textFile.readline()
                string = ""
                break
            elif string == "гс\"" or string == "гс \"":
                j = i + 1
                voice=""
                while (line[j] != '\"'):
                    voice += line[j]
                    j += 1;
                print(voice)
                elements.append(VoicePost(voice))
                line = textFile.readline()
                string = ""
                break
            elif string == "аудио\"" or string == "аудио \"":
                j = i + 1
                audio=""
                while (line[j] != '\"'):
                    photo += line[j]
                    j += 1;
                print(photo)
                if groupMessageFlag:
                    groupMessage.append(AudioPost(audio))
                else:
                    elements.append(AudioPost(audio))
                line = textFile.readline()
                string = ""
                break
            elif string == "видео\"" or string == "видео \"":
                j = i + 1
                video=""
                while (line[j] != '\"'):
                    video += line[j]
                    j += 1;
                print(photo)
                if groupMessageFlag:
                    groupMessage.append(VideoPost(video))
                else:
                    elements.append(VideoPost(video))
                line = textFile.readline()
                string = ""
                break
            elif string == "кругл\"" or string == "кругл \"":
                j = i + 1
                video=""
                while (line[j] != '\"'):
                    video += line[j]
                    j += 1;
                elements.append(RoundPost(video))
                line = textFile.readline()
                string = ""
                break
            elif string == "гиф\"" or string == "гиф \"":
                j = i + 1
                gif=""
                while (line[j] != '\"'):
                    gif += line[j]
                    j += 1;
                print(gif)
                elements.append(GifPost(gif))
                line = textFile.readline()
                string = ""
                break
            elif string == "модель\"" or string == "модель \"":
                j = i + 1
                model=""
                while (line[j] != '\"'):
                    model += line[j]
                    j += 1;
                print(model)
                elements.append(ModelPost(model))
                line = textFile.readline()
                string = ""
                break
            elif string == "документ\"" or string == "документ \"":
                j = i + 1
                doc=""
                while (line[j] != '\"'):
                    doc += line[j]
                    j += 1;
                print(doc)
                if groupMessageFlag:
                    groupMessage.append(DocMessage(doc))
                else:
                    elements.append(DocPost(doc))
                line = textFile.readline()
                string = ""
                break
            elif string == "стикер\"" or string == "стикер \"":
                j = i + 1
                sticker=""
                while (line[j] != '\"'):
                    sticker += line[j]
                    j += 1;
                print(sticker)
                elements.append(StickerPost(sticker))
                line = textFile.readline()
                string = ""
                break
            elif string == "кнопки\"" or string == "кнопки \"":
                buttons = []
                j = i + 1
                while (line[j] != '\"'):
                    text += line[j]
                    j+=1;
                    if (j==len(line)):
                        #text += "\n"
                        line = textFile.readline().replace('\t', '')
                        j = 0
                text = text.replace("\\t", "\t")
                print("_____________")
                print (text)
                print("_____________")
                while True:
                    line = textFile.readline()
                    line = line.replace("\t", "")                    
                    if line.find("хватитКнопок")>-1:                        
                        elements.append(ButtonsPost(text, buttons))
                        line = textFile.readline()
                        string = ""
                        break
                    #print(line)
                    btnText, destination = line.split("--")
                    btnText = btnText[1:len(btnText)-2]
                    destination = destination[1:]
                    if destination.find("\"")==-1:
                        pass #TODO не имя сцены, а команда
                    else:
                        destination = destination[destination.index("\"")+1:destination.rindex("\"")]
                    print(btnText, destination)
                    btn = Button(btnText) #TODO сделать что-то с пунктом назначения 
                    buttons.append(btn)                                        
                string = ""
                break

allMessages = []
for sc in scenes:
    allMessages += sc.getSceneMessages()

bot = Bot(token, allMessages)

# закрываем файл
textFile.close()
