# For each of my (Nick's) additions to the code I wrote "NH" as a comment to make it easier to locate
import math # NH
import pygame
import sheets_handler 
from oauth2client.service_account import ServiceAccountCredentials 
from sheets_handler import append_data_to_sheet, retrieve_data_from_sheet
pygame.init()

# pygame screen
width = 1600
height = 900

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("idp")
clock = pygame.time.Clock()

leaderBoard1st = f"1st: {retrieve_data_from_sheet('A2')}: {retrieve_data_from_sheet('B2')}"
leaderBoard2nd = f"2nd: {retrieve_data_from_sheet('A3')}: {retrieve_data_from_sheet('B3')}"
leaderBoard3rd = f"3rd: {retrieve_data_from_sheet('A4')}: {retrieve_data_from_sheet('B4')}"
leaderBoard4th = f"4th: {retrieve_data_from_sheet('A5')}: {retrieve_data_from_sheet('B5')}"
leaderBoard5th = f"5th: {retrieve_data_from_sheet('A6')}: {retrieve_data_from_sheet('B6')}"

# Music and Sounds
click = pygame.mixer.Sound("dialogueSFX.mp3")
click.set_volume(0.1)
deepClick = pygame.mixer.Sound("dialogueSFXLower.mp3")
deepClick.set_volume(0.3)
highClick = pygame.mixer.Sound("dialogueSFXHigher.mp3")
highClick.set_volume(0.5)


# -------------------------------------------- CLASSES -------------------------------------------------------- #

class Player(pygame.sprite.Sprite): # player class :)
    def __init__(self):
        super().__init__()
        self.xpos = 1800
        self.ypos = 1100
        self.speed = 5
        self.image = pygame.transform.scale(pygame.image.load("player/cedric.png").convert_alpha(), (135, 394))
        self.rect = self.image.get_rect(center = (self.xpos, self.ypos))
        self.facing = "left"
        self.direction = ""
        
    def inventory(self):
        if inventoryActive:
            screen.blit(inventoryEnv.image, inventoryEnv.rect)
            screen.blit(inventorySlot1.image, inventorySlot1.rect)
            screen.blit(inventorySlot2.image, inventorySlot2.rect)
            screen.blit(inventorySlot3.image, inventorySlot3.rect)
            screen.blit(inventorySlot4.image, inventorySlot4.rect)
            screen.blit(controlsInstructions.image, controlsInstructions.rect)
            pressE.rect.centerx = 1150
            screen.blit(pressE.image, pressE.rect)
            for i in inventoryList:
                try:
                    screen.blit(pygame.transform.scale(pygame.image.load(i).convert_alpha(), (125, 125)), inventoryPositionDict[inventoryList.index(i)].rect)
                except :
                    pass
        elif inventoryActive == False and interactable:
            pressE.rect.centerx = 1500
            screen.blit(pressE.image, pressE.rect)

    def itemCheck(self, item):
        if item in inventoryList:
            return True

    def player_input(self):
        global movement
        keys = pygame.key.get_pressed()
        if movement:
            if keys[pygame.K_a] and self.rect.left >= width - width: 
                self.xpos -= 1*self.speed
                if "left" not in self.facing:
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.facing = "left"
            if keys[pygame.K_d] and self.rect.right <= width:
                self.xpos += 1*self.speed
                if "right" not in self.facing:
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.facing = "right"
            if keys[pygame.K_w] and self.rect.top >= 288:
                self.ypos -= 1*self.speed
            if keys[pygame.K_s] and self.rect.bottom <= height:
                self.ypos += 1*self.speed


    def apply_movement(self):
        self.rect.centery = self.ypos
        self.rect.centerx = self.xpos

    def collision(self):
        solidObjects = pygame.sprite.spritecollide(self, environment_group, False) + pygame.sprite.spritecollide(self, dialogueTrigger_group, False) + pygame.sprite.spritecollide(self, newRoomTrigger_group, False)

        for solid in solidObjects:
            if solid.collidable == True:
                dr = abs(self.rect.right - solid.rect.left)
                dl = abs(self.rect.left - solid.rect.right)
                db = abs(self.rect.bottom - solid.rect.top)
                dt = abs(self.rect.top - solid.rect.bottom)

                if min(dl, dr) < min(dt, db):
                    self.direction = "left" if dl < dr else "right"
                else:
                    self.direction = "bottom" if db < dt else "top"

                if self.direction == "left":
                    self.rect.left = solid.rect.right - 1

                elif self.direction == "right":
                    self.rect.right = solid.rect.left + 1

                elif self.direction == "top":
                    self.rect.top = solid.rect.bottom - 1

                elif self.direction == "bottom":
                    self.rect.bottom = solid.rect.top + 1
                self.xpos = self.rect.centerx
                self.ypos = self.rect.centery

    def update(self):
        self.player_input()
        self.apply_movement()
        self.collision()
        self.inventory()

class Environment(pygame.sprite.Sprite): # class for handling images that are displayed on the game
    def __init__(self, xpos, ypos, width, height, collidable:bool, collectable:bool, image = "what.png", angle = 0): #NH added the "angle" attribute 
        super().__init__()
        self.xpos = xpos
        self.ypos = ypos
        self.name = image
        self.image = pygame.transform.scale(pygame.image.load(image).convert_alpha(), (width, height))
        self.rect = self.image.get_rect(center = (self.xpos, self.ypos))
        self.collidable = collidable
        self.collectable = collectable
        self.angle = angle

    def apply_change(self):
        self.rect.centerx = self.xpos
        self.rect.centery = self.ypos

    def update(self, *argv):
        global currentSurveyQuestion
        self.apply_change()
        try:
            for event in argv[0]:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.rect.collidepoint(event.pos) and self.collectable and interactable:
                        self.kill()
                        inventoryList.append(self.name)
                        highClick.play()
                        if roomID == 2763:
                            puzzleTrigger_group.empty()
                            currentSurveyQuestion += 1
                            surveyQuestionDict[currentSurveyQuestion]()
        except IndexError:
            pass
    
     # NH A function used to return images rotated around their center, to whatever the angle attribute states.
    def rotImage(self):
        while self.angle >= 360:
            self.angle += -360
        while self.angle < 0:
            self.angle += 360
        orig_rect = self.image.get_rect()
        rot_image = pygame.transform.rotate(self.image, self.angle)
        rot_rect = orig_rect.copy()
        rot_rect.center = rot_image.get_rect().center
        rot_image = rot_image.subsurface(rot_rect).copy()
        return rot_image
        

class DialogueTrigger(Environment): # class for handling images that will play dialogue when F key is pressed
    def __init__(self, xpos, ypos, width, height, collidable:bool, collectable:bool, speed, text, expression, image = "what.png"):
        super().__init__(xpos, ypos, width, height, collidable, collectable, image)
        self.text = text
        self.expression = expression
        self.speed = speed

class NewRoomTrigger(Environment): # class for handling images that will transport the player to a new room when the F key is pressed
    def __init__(self, xpos, ypos, width, height, collidable:bool, collectable:bool, rID, newX, newY, speed, waitMS, image = "what.png"):
        super().__init__(xpos, ypos, width, height, collidable, collectable, image)
        self.rID = rID
        self.newX = newX
        self.newY = newY
        self.speed = speed
        self.waitMS = waitMS

class PuzzleTrigger(Environment):
    def __init__(self, xpos, ypos, width, height, collidable:bool, collectable:bool, pID, image = "what.png"):
        super().__init__(xpos, ypos, width, height, collidable, collectable, image)
        self.pID = pID

# --------------------------------------------- FUNCTIONS -------------------------------------------------------- #

textDone = False
counter = 0
activeMessage = 0
dialogueDone = False
voiceDict = {
    "Amalgamation.png" : deepClick
}

def conversation(text, expression, speed): # BTW FOR SPEED, THE HIGHER IT IS, THE SLOWER IT WILL BE YES THIS IS NOT INTUITIVE OH WELL
    global movement, counter, textDone, activeMessage, message, wholeMessage, dialogueInitiated, dialogueDone
    wholeMessage = text
    message = wholeMessage[activeMessage]
    dialogueSprite = pygame.transform.scale(pygame.image.load(expression[activeMessage]).convert_alpha(), (200, 200))
    old = message[0:counter//speed]
    if activeMessage >= len(wholeMessage) - 1:
        dialogueInitiated = False
        activeMessage = 0
        movement = True
        dialogueDone = True
    if counter < len(message)*speed:
        counter += 1
    elif counter >= len(message) * speed:
        pygame.time.wait(100)
        textDone = True
    snip = largerFont.render(message[0:counter//speed], True, "White")
    if len(old.replace(" ", "")) < len(message[0:counter//speed].replace(" ", "")):
        try:
            voiceDict[expression[activeMessage]].play()
        except KeyError:
            click.play()
    screen.blit(dialogueBox.image, dialogueBox.rect)
    screen.blit(snip, (300, 625))
    screen.blit(dialogueSprite, (75, 625))
    if textDone:
        screen.blit(pressEnter_Text, pressEnter_Rect)


def changingRooms(newRoomID, newX, newY, speed:10, waitMS:0): # DON'T WORRY THE SPEED FOR THIS FUNCTION IS ACTUALLY INTUITIVE YES HOORAY LETS GOOOOOO
    global roomID, screenTransitionAlpha, interactable
    screenTransitionAlpha += speed

    if screenTransitionAlpha > 255:
        pygame.time.wait(waitMS)
        environment_group.empty()
        dialogueTrigger_group.empty()
        newRoomTrigger_group.empty()
        puzzleTrigger_group.empty()
        dummy_group.empty()
        interactable = False
        roomID = newRoomID
        roomDict[roomID]()
        player.xpos = newX
        player.ypos = newY
        player.update()

def forceDialogue(dialogue):
    global dialogueInitiated, interactable, movement
    movement = False
    dialogue.xpos, dialogue.ypos = player.xpos, player.ypos
    dialogue.update()
    dialogueTrigger_group.add(dialogue)
    dialogueInitiated, interactable = True, False

def forceCustomDialogue(speed, dialogueText, dialogueExpressions):
    global dialogueInitiated, interactable, movement
    movement = False
    customDialogue.text = dialogueText
    customDialogue.speed = speed
    customDialogue.expression = dialogueExpressions
    customDialogue.xpos, customDialogue.ypos = player.xpos, player.ypos
    customDialogue.update()
    dialogueTrigger_group.add(customDialogue)
    dialogueInitiated, interactable = True, False

def forceNewRoom(roomTrigger):
    global changingRoomsCond, interactable
    roomTrigger.xpos, roomTrigger.ypos = player.xpos, player.ypos
    roomTrigger.update()
    newRoomTrigger_group.add(roomTrigger)
    changingRoomsCond, interactable = True, False

# NH Here is a little function I made to quickly get the distance between two points
def getDist(loc1, loc2, ret=3):
  (loc1x, loc1y) = loc1
  (loc2x, loc2y) = loc2
  if ret == 3: 
    retDist = math.sqrt((loc1x-loc2x)**2)+((loc1y-loc2y)**2)
  elif ret == 2:
    retDist = (loc1y-loc2y)
  elif ret == 1:
    retDist = (loc1x-loc2x)
  return retDist

# NH This function tracks your mouse movement around a center point so the change in angle from the image can be added to something (often the angle attribute of an object) 
def manualTurn(obCenter, mousePos):
    global manRot
    prevRot = manRot
    try:
        manRot = (180/3.1415)*math.atan(getDist(mousePos,obCenter, 2)/-(getDist(mousePos, obCenter, 1)))
    except:
        manRot = 0
    if getDist(mousePos, obCenter,1) < 0:
        manRot += 180
    elif getDist(mousePos, obCenter) > 0:
        manRot += 360
    while manRot >= 360:
        manRot += -360
    if manRot != prevRot:
        if abs(manRot - prevRot < 180) and abs(prevRot - manRot  < 180):
            return (manRot - prevRot)
        else:
            return 0
    else:
        return 0

# ------------------------------------------- SURFACES (such as text, sprites) -------------------------------------------------------- #

# text related stuff
font = pygame.font.Font(None, 50)
largerFont = pygame.font.Font(None, 65)

pressEnter_Text = font.render("Press Enter to continue.", True, "White")
pressEnter_Rect = pressEnter_Text.get_rect(bottomright = (1525, 825))

# sprites/surfaces
environment_group = pygame.sprite.Group()
dialogueTrigger_group = pygame.sprite.Group()
newRoomTrigger_group = pygame.sprite.Group()
puzzleTrigger_group = pygame.sprite.Group()
dummy_group = pygame.sprite.Group()

playerGroup = pygame.sprite.Group()
player = Player()
playerGroup.add(player)

# Starting Screen
startMenu = Environment(width/2, height/2, width, height, False, False, "miscAssets/CoverImageforapp.png")
leaderBoardButton = Environment(100, 100, 150, 150, False, False, "miscAssets/placeholderTrophy.png")

leaderBoardTitle = Environment(width/2, 225, 1100, 225, False, False, "miscAssets/placeholderLeaderboardTitle.png")

leaderBoardBackground = Environment(width/2, height/2, 1200, 700, False, False, "miscAssets/solidBlack.png")
leaderBoardBackground.image.set_alpha(128)

# Room 1
studyFloor = Environment(width/2, height/2, width, height, False, False, "studyRoom\studyRoomBGI.png")
amalgamation = Environment(883, 600, 400, 600, True, False, "Amalgamation.png")

# Misc Environments
dummy = Environment(1700, 1000, player.image.get_width(), player.image.get_height(), False, False, "player/cedric.png")
dialogueBox = Environment(width/2, 725, 1500, 250, False, False, "placeholderDialogueBox.png")
interactSign = Environment(1700, 1000, 100, 100, False, False, "miscAssets/F_key.png")
exitButton = Environment(1700, 1000, 100, 100, False, False, "miscAssets/exitButton.png")
screenTransition = Environment(width/2, height/2, width, height, False, False, "miscAssets/solidBlack.png")
keyO = Environment(1388, 748, 100, 100, False, True, "studyRoom/Key_O.png")
keyY = Environment(910, 380, 100, 100, False, True, "studyRoom/Key_Y.png")
#match = Environment(200, 800, 100, 100, False, True, "studyRoom/match.png")
#unlitCandle = Environment(width/2, 650, 100, 100, False, True, "studyRoom/Unlit_Candle.png")

pressE = Environment(1525, 75, 100, 100, False, False, "press e.png")

inventoryEnv = Environment(1400, height/2, 350, 850, False, False, "miscAssets/solidBlack.png")
inventoryEnv.image.set_alpha(200)
inventorySlot1 = Environment(1325, 125, 125, 125, False, False, "lightGray.png")
inventorySlot1.image.set_alpha(175)
inventorySlot2 = Environment(1475, 125, 125, 125, False, False,"lightGray.png")
inventorySlot2.image.set_alpha(175)
inventorySlot3 = Environment(1325, 275, 125, 125, False,False, "lightGray.png")
inventorySlot3.image.set_alpha(175)
inventorySlot4 = Environment(1475, 275, 125, 125, False,False, "lightGray.png")
inventorySlot4.image.set_alpha(175)
controlsInstructions = Environment(1400, 605, 275, 440, False, False, "miscAssets/placeholderControlPanel.png")

# Dialogue Triggers (FOR THE DIALOGUE TRIGGER, ALWAYS ADD ONE EXTRA BLANK DIALOGUE TO THE LIST ALONG WITH A RANDOM IMAGE BECAUSE REASONS)
customDialogue = DialogueTrigger(1700, 1000, 100, 100, False, False, 3, ["placeholder"], ["player/cedricHeadshot"])
customDialogue.image.set_alpha(0)

studyGrandfatherClockDialogue = DialogueTrigger(100, 500, 100, 700, False,False, 3, ["(It's a very nice looking grandfather clock.)", "(Nevermind that, you need to hurry!)", "(After all, the CLOCK is TICKING...)", " "], ["studyRoom/grandFatherClockHeadshot.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png", "studyRoom/grandFatherClockHeadshot.png"])
studyGrandfatherClockDialogue.image.set_alpha(0)

hintDialogue = DialogueTrigger(1700, 1000, 100, 100, False,False, 3, ["placeholder"], ["what.png"])
hintDialogue.image.set_alpha(0)

deathDialogue = DialogueTrigger(1700, 1000, 100, 100, False,False, 5, ["Uh oh...", "I don't feel so good...", " "], ["player/cedricHeadshot.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png"])

# New Room Triggers
backToStartMenu = NewRoomTrigger(1500, 800, 100, 100, False,False, 0, 1800, 1100, 2, 3000, "placeholderNewRoomTrigger.png")
backToStartMenu.image.set_alpha(0)
studyRoomTrigger = NewRoomTrigger(0, 1100, 100, 100, False,False, 1, 978, 842, 2, 3000)
#studyToGroundRoomTrigger = NewRoomTrigger(1575, height/2, 50, 600, False, False, 2, None, None, None, None)
#studyToGroundRoomTrigger.image.set_alpha(0)

# Puzzle 1
journal = PuzzleTrigger(1270, 378, 73, 100, False,True, 0, "studyRoom\journalAsset.png")
journalContents = Environment(width/2, height/2, 1200, 750, False, False, "studyRoom/journalOpened.png")
journalDialogue = DialogueTrigger(1270, 378, 73, 100, False,False, 3, ["What's this?", " "], ["player/cedricHeadshot.png", "player/cedricHeadshot.png"], "studyRoom\journalAsset.png")
journalDialogueAftermath = DialogueTrigger(1278, 378, 73, 100, False, False, 3, ["(Somehow, the journal is completely empty...)", " "], ["player/cedricHeadshot.png", "player/cedricHeadshot.png"], "studyRoom/journalAsset.png")
journalInputBox = pygame.Rect(875, 600, 400, 55)
journalInputText = ""
journalInputTextSurf = font.render(journalInputText, False, (255, 255, 255))
journalCodeSurf = font.render("5 6 5 4 2 5 10 5 3 1 11 7", False, (255, 0, 0))
journalCodeRect = journalCodeSurf.get_rect(center = (1075, 300))

# Puzzle 2
scroll = PuzzleTrigger(1700, 1000, 100, 100, False,False, 1, "studyRoom\scrollAsset.png") #NH 
scrollContents = Environment(width/2, height/2, 575, 800, False, False, "studyRoom/scrollOpened.png")
clockHour = 5
clockMinute = 50
timeMin = 0
turningCog = 0
manRot = 0
grandFatherClockTrigger = PuzzleTrigger(100,500,100,700,False,False,2)
grandFatherClockTrigger.image.set_alpha(0)
grandFatherClockContents = Environment(100,100,1400,700,False,False,"placeholderClockBackround.png")
grandFatherClockClock = Environment(950,200,500,500,False,False,"placeholderClock.png")
grandFatherClockCog1 = Environment(150,325,250,250,False,False,"placeholderCog.png")
grandFatherClockCog2 = Environment(650,325,250,250,False,False,"placeholderCog.png")
# for the dialogue that plays after your complete the clock puzzle and pick up the candle forceCustomDialogue(3, ["A candle!", "I just need something to light this!"], ["player/cedricHeadshot.png", "player/cedricHeadshot.png"])

# Puzzle 3
studyGrandFatherClockCompletedDialogue = DialogueTrigger(100, 500, 100, 700, False, False, 3, ["(It's a very nice looking gr-)", "Hey, wait a second...", "There's something inside of this grandfather clock!", " "], ["studyRoom/grandFatherClockHeadshot.png","player/cedricHeadshot.png","studyRoom/Unlit_Candle.png","studyRoom/Unlit_Candle.png",])
studyGrandFatherClockCompletedDialogue.image.set_alpha(0)
keyYellowDialogueCheck = DialogueTrigger(662, 702, 15, 40, False, False, 3, ["(Do you have the key for this yellow lock?)", " "], ["studyRoom/keyLock_Y.png", "studyRoom/keyLock_Y.png"], "what.png")
keyYellowDialogueCheck.image.set_alpha(0)
keyOrangeDialogueCheck = DialogueTrigger(438, 702, 15, 40, False, False, 3, ["(Do you have the key for this orange lock?)", " "], ["studyRoom/keyLock_O.png", "studyRoom/keyLock_O.png"], "what.png")
keyOrangeDialogueCheck.image.set_alpha(0)

studyExitDoorDialogue = DialogueTrigger(1575, height/2, 50, 600, False, False, 3, ["(You think about leaving...)", " "], ["player/cedricHeadshot.png", "player/cedricHeadshot.png"])
studyExitDoorDialogue.image.set_alpha(0)
surveyRoomTrigger = NewRoomTrigger(1575, height/2, 50, 600, False, False, 2763, 1900, 1200, 2, 3000)
surveyRoomTrigger.image.set_alpha(0)

# survey
surveySpace = Environment(width/2, height/2, width, height, False, False, "miscAssets/solidWhite.png")
surveyJournal = Environment(400, 450, 146, 200, False, True, "studyRoom/journalAsset.png")
surveyGrandFatherClock = Environment(800, 450, 200, 200, False, True, "studyRoom/grandFatherClockHeadshot.png")
surveyKeys = Environment(1200, 450, 200, 200, False, True, "studyRoom/BothKeys.png")
surveyEasy = Environment(400, 450, 300, 100, False, True, "miscAssets/easy.png")
surveyPerfect = Environment(800, 450, 300, 100, False, True, "miscAssets/perfect.png")
surveyHard = Environment(1200, 450, 300, 100, False, True, "miscAssets/hard.png")

# Functions for adding the different things in a room to the correct group, every room is assigned a specific roomID based on the room dictionary. (also some specific things that only need to ran once)

def startScreen():
    global currentPuzzleID, hintID, typing, inventoryList, currentTimerLengthSecs, currentSurveyQuestion
    environment_group.add(startMenu, leaderBoardButton)
    currentTimerLengthSecs = timerLengthSecs
    currentPuzzleID, hintID, currentSurveyQuestion = 1, 0, 1
    inventoryList = []

def study():
    environment_group.add(studyFloor)
    dialogueTrigger_group.add(journalDialogue, studyGrandfatherClockDialogue, studyExitDoorDialogue, keyOrangeDialogueCheck, keyYellowDialogueCheck)
    player.image = pygame.transform.rotate(player.image, 90)
    player.rect = player.image.get_rect(center = (player.xpos, player.ypos))

def survey():
    global inventoryList, puzzle3Time, hintsUsedPuzzle3, hintID
    puzzle3Time = timerLengthSecs - puzzle2Time - puzzle1Time - currentTimerLengthSecs
    hintsUsedPuzzle3 = hintID
    hintID = 0
    environment_group.add(surveySpace)
    inventoryList = []

roomDict = {
    0 : startScreen,
    1 : study, 
    2763 : survey
}

# Functions for additional things that have to constantly happen when entering a new room, such as the player updating or drawing additional text

def startScreenExtra():
    if leaderBoardActive:
        screen.blit(leaderBoardBackground.image, leaderBoardBackground.rect)
        leaderBoard1st_Surf = largerFont.render(leaderBoard1st, False, "White")
        leaderBoard2nd_Surf = largerFont.render(leaderBoard2nd, False, "White")
        leaderBoard3rd_Surf = largerFont.render(leaderBoard3rd, False, "White")
        leaderBoard4th_Surf = largerFont.render(leaderBoard4th, False, "White")
        leaderBoard5th_Surf = largerFont.render(leaderBoard5th, False, "White")
        screen.blit(leaderBoardTitle.image, leaderBoardTitle.rect)
        screen.blit(leaderBoard1st_Surf, leaderBoard1st_Surf.get_rect(center = (width/2, 375)))
        screen.blit(leaderBoard2nd_Surf, leaderBoard2nd_Surf.get_rect(center = (width/2, 460)))
        screen.blit(leaderBoard3rd_Surf, leaderBoard3rd_Surf.get_rect(center = (width/2, 545)))
        screen.blit(leaderBoard4th_Surf, leaderBoard4th_Surf.get_rect(center = (width/2, 630)))
        screen.blit(leaderBoard5th_Surf, leaderBoard5th_Surf.get_rect(center = (width/2, 715)))
        exitButton.rect.centerx, exitButton.rect.centery = leaderBoardBackground.rect.right, leaderBoardBackground.rect.top
        screen.blit(exitButton.image, exitButton.rect)


def studyExtra():
    player.update()
    environment_group.update(event_list)

def surveyExtra():
    global surveyUsernameText, surveyUsernameSurf, currentSurveyQuestion, typing
    puzzleTrigger_group.update(event_list)
    if typing:
        for event in event_list:
            if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        surveyUsernameText = surveyUsernameText[:-1]
                    elif event.key == pygame.K_RETURN and len(surveyUsernameText) > 1:
                        typing = False
                        currentSurveyQuestion += 1
                        surveyQuestionDict[currentSurveyQuestion]()
                    elif surveyUsernameSurf.get_width() >= 380:
                        pass
                    else:
                        surveyUsernameText += event.unicode
        pygame.draw.rect(screen, (0, 0, 0), surveyUsernameInputBox, 2)
        surveyUsernameSurf = font.render(surveyUsernameText, False, (0, 0, 0))
        surveyTypeHereLabel = font.render("type here in this box by the way...", False, (0,0,0))
        screen.blit(surveyUsernameSurf, (surveyUsernameInputBox.x + 5, surveyUsernameInputBox.y + 8))
        screen.blit(surveyTypeHereLabel, (surveyUsernameInputBox.x, surveyUsernameInputBox.y - surveyTypeHereLabel.get_height() - 60))

roomExtraDict = {
    0 : startScreenExtra,
    1 : studyExtra,
    2763 : surveyExtra
}

# Functions for dialogue events that happen after a specific dialogue plays

def dialogueKill():
    global interactable
    pygame.sprite.spritecollide(player, dialogueTrigger_group, False)[0].kill()
    interactable = True

def hintKill():
    global timerEnabled
    dialogueKill()
    player.xpos, player.ypos = dummy.xpos, dummy.ypos
    player.update()
    dummy.kill()
    timerEnabled = True

def replaceDialogue():
    journalDialogue.kill()
    puzzleTrigger_group.add(journal)

def studyPuzzleInit():
    global timerEnabled, interactable
    customDialogue.kill()
    player.image = pygame.transform.rotate(player.image, -90)
    player.rect = player.image.get_rect(center = (player.xpos, player.ypos))
    player.rect.bottom = studyFloor.rect.bottom
    player.xpos, player.ypos = player.rect.centerx, player.rect.centery
    timerEnabled, interactable = True, True
    pygame.time.set_timer(timerEvent, 1000)

def fadeOut():
    global fadingOut, timerEnabled, movement, interactable
    dummy.image = pygame.transform.rotate(player.image, 90)
    dummy.rect = dummy.image.get_rect(center = (dummy.xpos, dummy.ypos))
    movement, interactable = False, False
    fadingOut = True

def amalgamationDialogueKill():
    global timerEnabled, currentPuzzleID, hintID
    dialogueKill()
    scroll.rect.centerx, scroll.rect.centery = amalgamation.rect.centerx, amalgamation.rect.bottom - 70
    scroll.xpos, scroll.ypos = scroll.rect.centerx, scroll.rect.centery
    dialogueTrigger_group.add(journalDialogueAftermath)
    puzzleTrigger_group.add(scroll, grandFatherClockTrigger)
    studyGrandfatherClockDialogue.kill()
    amalgamation.kill()
    journal.kill()
    currentPuzzleID = 2
    hintID = 0
    timerEnabled = True

def clockCompleted():
    global puzzleTextActive, timerEnabled, currentPuzzleID, hintID, clockHour, clockMinute, timeMin, turningCog, manRot
    clockHour = 5
    clockMinute = 50
    timeMin = 0
    turningCog = 0
    manRot = 0
    customDialogue.kill()
    currentPuzzleID = 3
    hintID = 0
    grandFatherClockTrigger.kill()
    scroll.kill()
    environment_group.add(keyO, keyY)
    dialogueTrigger_group.add(studyGrandFatherClockCompletedDialogue)
    puzzleTextActive = False
    timerEnabled = True

def insideGrandFatherClock():
    highClick.play()
    inventoryList.append("studyRoom/Unlit_Candle.png")
    studyGrandFatherClockCompletedDialogue.kill()
    dialogueTrigger_group.add(studyGrandfatherClockDialogue)

def checkYellowKey():
    if player.itemCheck("studyRoom/Key_Y.png"):
        keyYellowDialogueCheck.kill()
        inventoryList.pop(inventoryList.index("studyRoom/Key_Y.png"))
        inventoryList.append("studyRoom/boxOfMatches.png")
        highClick.play()
        forceCustomDialogue(3, ["(Inside the locked cabinet, you find...)", "(A box of matches...)", "What could I possibly do with this??", " "], ["studyRoom/keyLock_Y.png", "studyRoom/boxOfMatches.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png"])
    else:
        keyYellowDialogueCheck.kill()
        forceCustomDialogue(3, ["(Darn, you don't have the key...)", "(Imagine the legendary loot inside...)", " "], ["player/cedricHeadshot.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png"])

def checkOrangeKey():
    if player.itemCheck("studyRoom/Key_O.png"):
        keyOrangeDialogueCheck.kill()
        inventoryList.pop(inventoryList.index("studyRoom/Key_O.png"))
        inventoryList.append("studyRoom/cigarette.png")
        highClick.play()
        forceCustomDialogue(3, ["(Inside the locked cabinet, you find...)", "(A cigarette...)", "What am I supposed to do with this?!", " "], ["studyRoom/keyLock_O.png", "studyRoom/cigarette.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png"])
    else:
        keyOrangeDialogueCheck.kill()
        forceCustomDialogue(3, ["(Darn, you don't have the key...)", "(Imagine the amazing loot inside...)", " "], ["player/cedricHeadshot.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png"])

def yellowKeyNotReady():
    dialogueTrigger_group.add(keyYellowDialogueCheck)
    customDialogue.kill()

def orangeKeyNotReady():
    dialogueTrigger_group.add(keyOrangeDialogueCheck)
    customDialogue.kill()

def checkCandleAndMatch():
    if player.itemCheck("studyRoom/Unlit_Candle.png") and player.itemCheck("studyRoom/boxOfMatches.png"):
        studyExitDoorDialogue.kill()
        newRoomTrigger_group.add(surveyRoomTrigger)
        inventoryList.pop(inventoryList.index("studyRoom/Unlit_Candle.png"))
        inventoryList.pop(inventoryList.index("studyRoom/boxOfMatches.png"))
        inventoryList.append("studyRoom/Lit_Candle.png")
        highClick.play()
        forceCustomDialogue(3, ["(Oh right! You have that candle and match!)", "(You'll be perfectly fine going outside.)", " "], ["player/cedricHeadshot.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png"])
    else:
        studyExitDoorDialogue.kill()
        forceCustomDialogue(3, ["(Nope! It's as pitch dark as the night sky!)", "(In no world are you going in there!)", " "], ["player/cedricHeadshot.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png"])

def candleMatchNotReady():
    dialogueTrigger_group.add(studyExitDoorDialogue)
    customDialogue.kill()

def candleMatchReady():
    customDialogue.kill()

def askSurveyQuestion1():
    puzzleTrigger_group.add(surveyJournal, surveyGrandFatherClock, surveyKeys)

def askSurveyQuestion2():
    puzzleTrigger_group.add(surveyJournal, surveyGrandFatherClock, surveyKeys)

def askSurveyQuestion3():
    puzzleTrigger_group.add(surveyEasy, surveyPerfect, surveyHard)

def askSurveyNickname():
    global typing
    typing = True

def surveyToMainScreen():
    global surveyUsernameText
    playerSurveyResponses = inventoryList
    playerUsername = surveyUsernameText
    hardestPuzzle = playerSurveyResponses[0]
    if hardestPuzzle == "studyRoom/BothKeys.png":
        hardestPuzzle = "Key Finding Puzzle"
    elif hardestPuzzle == "studyRoom/grandFatherClockHeadshot.png":
        hardestPuzzle = "Grandfather Clock Puzzle"
    elif hardestPuzzle == "studyRoom/journalAsset.png":
        hardestPuzzle = "Journal Puzzle"

    easiestPuzzle = playerSurveyResponses[1]
    if easiestPuzzle == "studyRoom/BothKeys.png":
        easiestPuzzle = "Key Finding Puzzle"
    elif easiestPuzzle == "studyRoom/grandFatherClockHeadshot.png":
        easiestPuzzle = "Grandfather Clock Puzzle"
    elif easiestPuzzle == "studyRoom/journalAsset.png":
        easiestPuzzle = "Journal Puzzle"

    gameRating = playerSurveyResponses[2]
    if gameRating == "miscAssets/hard.png":
        gameRating = "Hard"
    elif gameRating == "miscAssets/perfect.png":
        gameRating = "Perfect"
    elif gameRating == "miscAssets/easy.png":
        gameRating = "Easy"
    surveyUsernameText = ""
    append_data_to_sheet(playerUsername=playerUsername, max_time=900, puzzle1Time=puzzle1Time, puzzle2Time=puzzle2Time, puzzle3Time=puzzle3Time, hints=hints, hintsUsedPuzzle1=hintsUsedPuzzle1, hintsUsedPuzzle2=hintsUsedPuzzle2, hintsUsedPuzzle3=hintsUsedPuzzle3, hardestPuzzle=hardestPuzzle, easiestPuzzle=easiestPuzzle, gameRating=gameRating)
    forceNewRoom(backToStartMenu)

dialogueEventDict = {
    "(Press E for a tutorial...)" : studyPuzzleInit,
    "What's this?" : replaceDialogue,
    "(Perhaps you should try something else?...)" : dialogueKill,
    "Literally, and metaphorically. Try finding a light first." : amalgamationDialogueKill,

    "(But where???)" : clockCompleted,
    "There's something inside of this grandfather clock!" : insideGrandFatherClock,

    "(Do you have the key for this yellow lock?)" : checkYellowKey,
    "(Do you have the key for this orange lock?)" : checkOrangeKey,
    "What could I possibly do with this??" : customDialogue.kill,
    "(Imagine the legendary loot inside...)" : yellowKeyNotReady,
    "What am I supposed to do with this?!" : customDialogue.kill,
    "(Imagine the amazing loot inside...)" : orangeKeyNotReady,


    "(You think about leaving...)" : checkCandleAndMatch,
    "(In no world are you going in there!)" : candleMatchNotReady,
    "(You'll be perfectly fine going outside.)" : candleMatchReady,

    "(Such as the FIRST thing they would do for the day.)" : hintKill,
    "(But in what order should it be arranged in...?)" : hintKill,
    "(are CONNECTED.)" : hintKill,

    "(Do the red letters refer to specific numbers?)" : hintKill,
    "(But what am I supposed to do with that time?)" : hintKill,
    "(How did I not notice that??)" : hintKill,

    "(Where could I find something like that?)" : hintKill,
    "(Just to be sure...)" : hintKill,
    "(I need to look more closely for ITEMS...)" : hintKill,

    "\"What do you think was the hardest puzzle?\"" : askSurveyQuestion1,
    "uhhhh \"Which do you think was the easiest?\"" : askSurveyQuestion2,
    "\"Or too hard?\"" : askSurveyQuestion3,
    "\"Can you please give us a nickname?\"" : askSurveyNickname,
    "uh thank you for \"answering our survey!\"" : surveyToMainScreen,

    "(No hints available.)" : hintKill,

    "I don't feel so good..." : fadeOut
    
}

# Functions for new room events that happen after the new room COMPLETELY loads (not like the other room dict)

def wakeUp():
    pygame.time.wait(5000)
    forceCustomDialogue(3, ["What.. where am I?", "I feel so cold.", "HUH?? WHY AM I ON THE FLOOR?", "(Press E for a tutorial...)", " "], ["player/cedricHeadshot.png", "player/cedricHeadshot.png","player/cedricHeadshot.png", "what.png", "what.png"])

def death():
    global interactable, dummyAlpha, puzzle1Time, puzzle2Time, puzzle3Time, hintsUsedPuzzle1, hintsUsedPuzzle2, hintsUsedPuzzle3, leaderBoard1st, leaderBoard2nd, leaderBoard3rd, leaderBoard4th, leaderBoard5th
    interactable = True
    dummyAlpha = 255
    dummy.image.set_alpha(dummyAlpha)
    print(f"puzzle 1: {puzzle1Time}, puzzle 2: {puzzle2Time}, puzzle 3: {puzzle3Time}")
    print(f"hints 1: {hintsUsedPuzzle1}, hints 2: {hintsUsedPuzzle2}, hints 3: {hintsUsedPuzzle3}")
    puzzle1Time, puzzle2Time, puzzle3Time = "N/A", "N/A", "N/A"
    hintsUsedPuzzle1, hintsUsedPuzzle2, hintsUsedPuzzle3 = "N/A", "N/A", "N/A"

    leaderBoard1st = f"1st: {retrieve_data_from_sheet('A2')}: {retrieve_data_from_sheet('B2')}"
    leaderBoard2nd = f"2nd: {retrieve_data_from_sheet('A3')}: {retrieve_data_from_sheet('B3')}"
    leaderBoard3rd = f"3rd: {retrieve_data_from_sheet('A4')}: {retrieve_data_from_sheet('B4')}"
    leaderBoard4th = f"4th: {retrieve_data_from_sheet('A5')}: {retrieve_data_from_sheet('B5')}"
    leaderBoard5th = f"5th: {retrieve_data_from_sheet('A6')}: {retrieve_data_from_sheet('B6')}"

def surveyIntroDialogue():
    pygame.time.wait(1000)
    forceCustomDialogue(3, ["...", "oh, hey there.", "i didn't expect you to get here so soon...", "*psst what am i supposed to do again?*", "OH RIGHT, uhhh...", "\"What do you think was the hardest puzzle?\"", " "], ["what.png","what.png","what.png","what.png","what.png","what.png","what.png",])

newRoomEventDict = {
    0 : death,
    1 : wakeUp,
    2763 : surveyIntroDialogue
}

# -------------------------------------------- HINTS -------------------------------------------------------- #

hintDict = {
    10 : ["(Oh, it's an old journal.)",  "(The type someone would use to write reminders.)", "(Such as the FIRST thing they would do for the day.)", " "],
    11 : ["(But, you realize the entries are out of ORDER.)", "(This mildly irritates you...)", "(Maybe you should rearrange them properly.)",  "(But in what order should it be arranged in...?)", " "],
    12 : ["(Maybe that CODE at the bottom,)", "(and the ORDER of the poem,)", "(along with the FIRST letter,)", "(are CONNECTED.)", " "],

    20 : ["(That's weird... Why are some letters red?)", "(And what does it mean by \"numbered\"?)", "(Do the red letters refer to specific numbers?)", " "],
    21 : ["(And that part about \"time\"...)", "(If the red letters refer to specific numbers,)", "(Then those numbers HAVE to compose a certain time.)", "(But what am I supposed to do with that time?)", " "],
    22 : ["(Oh, right...)", "(There's literally a huge grandfather clock over there)", "(How did I not notice that??)", " "],

    30 : ["(What did the Amalgamation say again?)", "(That I needed a light to leave?)", "(Where could I find something like that?)", " " ],
    31 : ["(If changing the grandfather clock did something,)", "(I should probably check it again...)", "(Just to be sure...)", " " ],
    32 : ["(Has anything in this room changed at all?)", "(I need to look more closely for ITEMS...)", " "],

    40 : ["(I think there's something wrong with this record player's SETTINGS...)", "(But how can it be adjusted?)", " "],
    41 : ["(Maybe a button or part on the record player can help fix it)", "(One of them should do the trick.)", " "],
    42 : ["(What is this record player saying?)", "(It's speed is too FAST to understand)", " "],

    50 : ["(I can't understand what this paper says!)", "(I should think hard and REFLECT upon what it could mean)", " "], 
    51 : ["(Most of this house decor seems pretty old...)", "(But that \"mirror\" over there is still in good shape.)", "(Maybe I should take a moment to fix my hair)", " "],
    52 : ["(This paper seems to contain some sort of \"passcode\".)", "(There should be an item in here that needs this...)", "(But what could it be?)", " "],

    60 : ["(There's only dust and soot in this fireplace!)", "(Oh, wait...)", "(I think I see something hiding in here!)", " "],
    61 : ["(These little pieces are made out of the same material...)", "(Maybe they CONNECT together.)", " "],
    62 : ["(It looks like the pieces form a key.)", "(I wonder what it's been used for?)", " "],

    70 : ["(What could the NUMBER for the suitcase be?)", "(This person usually hides their passwords in an item,)", "(so something in this room probably has the code)", " "],
    71 : ["(There’s a paper placed under the suitcase!)", "(It sure has a lot of WORDS on it.)", "(But how could it relate to a passcode NUMBER?)", " "], 
    72 : ["(Maybe I should count how many words are on each line?)", " "],

    80 : ["(What are these symbols?)”, “(They must be roman numerals.)", " "],
    81 : ["(If I remember correctly,)", "(I=1, II=2, III=3, IV=4, V=5, VI=6, VII=7, VIII=8, IX=9, X=10)", " "],
    82 : ["(This box is locked…)", "(I think it needs a passCODE to be opened.)", " "],

    90 : ["(The newspaper said there had been 5 victims…)", "(I don’t think their names were very long.)", " "],
    91 : ["(I think she had a niCkname, whAt waS it again?)", " "],
    92 : ["(I’m pretty sure I was married before I died…)", " "]
}


# -------------------------------------------- PUZZLES -------------------------------------------------------- #

def journalZoom():
    global journalInputText, journalInputTextSurf, typing, event_list
    for event in event_list:
        if event.type == pygame.KEYDOWN:
            if typing:
                if event.key == pygame.K_BACKSPACE:
                    journalInputText = journalInputText[:-1]
                elif event.key == pygame.K_RETURN and currentPuzzleID == 1:
                    try:
                        textCheckDict[f"{currentPuzzleID}{journalInputText.lower()}"]()
                    except KeyError:
                        typing = False
                        forceCustomDialogue(3, ["(You feel a weird sense of unfulfillment...)", "(Perhaps you should try something else?...)", " "], ["player/cedricHeadshot.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png"])
                elif journalInputTextSurf.get_width() >= 380:
                    pass
                else:
                    journalInputText += event.unicode
    screen.blit(journalContents.image, journalContents.rect)
    exitButton.rect.centerx, exitButton.rect.centery = journalContents.rect.right, journalContents.rect.top
    screen.blit(exitButton.image, exitButton.rect)
    if typing:
        pygame.draw.rect(screen, (0, 0, 0), journalInputBox, 2)
    else:
        pygame.draw.rect(screen, (128, 128, 128), journalInputBox, 2)
        journalInputText = "_"
    journalInputTextSurf = font.render(journalInputText, False, (255, 255, 255))
    screen.blit(journalInputTextSurf, (journalInputBox.x + 5, journalInputBox.y + 8))
    screen.blit(journalCodeSurf, journalCodeRect)

def scrollZoom():
    screen.blit(scrollContents.image, scrollContents.rect)
    exitButton.rect.centerx, exitButton.rect.centery = scrollContents.rect.right, scrollContents.rect.top
    screen.blit(exitButton.image, exitButton.rect)

# NH loop for the clock puzzle
def grandFatherClockDisplay():
    global clockHour, clockMinute, manRot, timeMin, turningCog, timerEnabled, puzzle2Time, hintsUsedPuzzle2
    mousePos = pygame.mouse.get_pos()
    (mousex, mousey) = mousePos
    # NH I couldn't get the centers using rect.center or get_rect().center :(
    clockCenter = (1200,450)
    (clockCenterx, clockCentery) = (clockCenter)
    cog1Center = (275,450)
    (cog1Centerx,cog1Centery) = cog1Center
    cog2Center = (775,450)
    (cog2Centerx,cog2Centery) = cog2Center
    screen.blit((grandFatherClockContents.image), (grandFatherClockContents.xpos, grandFatherClockContents.ypos))
    screen.blit((grandFatherClockClock.image), (grandFatherClockClock.xpos, grandFatherClockClock.ypos))
    screen.blit((grandFatherClockCog1.rotImage()), (grandFatherClockCog1.xpos, grandFatherClockCog1.ypos))
    screen.blit((grandFatherClockCog2.rotImage()), (grandFatherClockCog2.xpos, grandFatherClockCog2.ypos))
    exitButton.rect.centerx, exitButton.rect.centery = 1500, 100
    screen.blit(exitButton.image, exitButton.rect)
    if clockMinute >= 60:
        clockHour += 1
        clockMinute = 0
    elif clockMinute < 0:
        clockHour += -1
        clockMinute = 59
    timeMin = clockHour*60 + clockMinute
    (clockHourx,clockHoury) = (100*math.cos(3.14/6*(clockHour-3+((3.14/30)*clockMinute/6)))+clockCenterx,100*math.sin(3.14/6*(clockHour-3+((3.14/30)*clockMinute/6)))+clockCentery)
    (clockMinutex,clockMinutey) = (150*math.cos(3.14/30*(clockMinute-15))+clockCenterx,150*math.sin(3.14/30*(clockMinute-15))+clockCentery)
    pygame.draw.line(screen, (0,0,0), clockCenter, (clockHourx,clockHoury),16)
    pygame.draw.line(screen, (0,0,0), clockCenter, (clockMinutex,clockMinutey),10)
    pygame.draw.circle(screen, (0,0,0), (clockHourx,clockHoury),8)
    pygame.draw.circle(screen, (0,0,0), (clockMinutex,clockMinutey),5)
    if pygame.mouse.get_pressed()[0] and not dialogueInitiated:
        if getDist(cog1Center, mousePos) < 300 and turningCog == 0 :
            turningCog = 1
        elif 300 > getDist(mousePos, cog2Center) and turningCog == 0:
            turningCog = 2
        if turningCog == 1:
            turnAmt = manualTurn(cog1Center, mousePos)
            clockMinute += -(turnAmt/60)
            grandFatherClockCog1.angle += (turnAmt)/5
        elif turningCog == 2:
            turnAmt = manualTurn(cog2Center, mousePos)
            clockHour += -(turnAmt/450)
            grandFatherClockCog2.angle += (turnAmt/5)
    else:
        if clockHour > 12:
            clockHour = 1
        elif clockHour < 1:
            clockHour = 12
        clockMinute = round(clockMinute)
        clockHour = round(clockHour)
        manRot = 0
        turningCog = 0
        if timeMin >= 704 and timeMin <= 706:
            # NH this is where it detects you've completed it, but I don't know how to stop this puzzle loop.
            timerEnabled = False
            puzzle2Time = timerLengthSecs - puzzle1Time - currentTimerLengthSecs
            hintsUsedPuzzle2 = hintID
            forceCustomDialogue(3, ["(You hear something opening...)", "(But where???)", " "], ["studyRoom/grandFatherClockHeadshot.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png",])

puzzleDict = {
    0 : journalZoom,
    1 : scrollZoom,
    2 : grandFatherClockDisplay,
}

def journalTextSuccess():
    global journalInputText, typing, puzzleTextActive, timerEnabled, movement, dialogueInitiated, puzzle1Time, hintsUsedPuzzle1
    hintsUsedPuzzle1 = hintID
    puzzle1Time = timerLengthSecs - currentTimerLengthSecs
    journalInputText = ""
    typing = False
    puzzleTextActive = False
    timerEnabled = False
    environment_group.add(amalgamation)
    pygame.time.delay(500)
    forceCustomDialogue(3, ["Leave me in my misery.", "You'll have all eternity to see us later.", "Who are you? Let me out of here!", "Who am I? You don't even know who you are.", "Hogwash. Of course I know who I am.", "I'm...", "I am, uhh...", "It's no use. Your fate is eternity here.", "Better if you spend it alone while you can.", "The less you know, the better.", "Ignorance is bliss, my friend...", "But I must know! What is this?", "Well if you insist...you are gone.", "Dead.", "Deceased.", "Dead?!", "What do you mean \"dead\"!!", "You exist in a state of wandering.", "After your death, you ended up here.", "Eventually, your spiritual energy will combine with us,", "the Amalgamation", "Permanently trapped in this cursed house.", "Most move onto the stars, most are brought peace.", "But not us...", "We are not granted the same privileges, taken so easily.", "Why so verbose, \"move onto the stars\"?", "When one's soul, and mind, are at complete tranquility.", "Only then, does one's world go black,", "awakening amongst stars, glowing with radiance.", "It is, only after what appears to be reality bending,", "periods of time, do these concepts become self-evident.", "For that reason, I will put it in layman's terms;", "Find out the motives behind your appearance here,", "and you'll become one with the stars.", "You're incomplete.", "Why- you! I'll show you!", "I'll find my way out of this blasted place!", "Throughout this house, we've left keys,", "keys to your escape and unknown identity.", "This is a test, a game if you will,", "to see if you truly deserve seeing stars.", "Outside of this room, though, you're blind.", "Literally, and metaphorically. Try finding a light first.", " "], ["Amalgamation.png", "Amalgamation.png", "player/cedricHeadshot.png", "Amalgamation.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png", "Amalgamation.png", "Amalgamation.png", "Amalgamation.png", "Amalgamation.png", "player/cedricHeadshot.png", "Amalgamation.png", "Amalgamation.png", "Amalgamation.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png", "Amalgamation.png","Amalgamation.png","Amalgamation.png","Amalgamation.png","Amalgamation.png","Amalgamation.png","Amalgamation.png","Amalgamation.png", "player/cedricHeadshot.png", "Amalgamation.png","Amalgamation.png","Amalgamation.png","Amalgamation.png","Amalgamation.png","Amalgamation.png","Amalgamation.png","Amalgamation.png","Amalgamation.png", "player/cedricHeadshot.png","player/cedricHeadshot.png", "Amalgamation.png", "Amalgamation.png","Amalgamation.png","Amalgamation.png","Amalgamation.png","Amalgamation.png","Amalgamation.png", "Amalgamation.png"])

textCheckDict = {
    "1amalgamation" : journalTextSuccess
}

# -------------------------------------------- INVENTORY -------------------------------------------------------- #

inventoryList = []

inventoryPositionDict = {
    0 : inventorySlot1,
    1 : inventorySlot2,
    2 : inventorySlot3,
    3 : inventorySlot4
}

# -------------------------------------------- PUZZLE TIMER -------------------------------------------------------- #

timerEvent = pygame.USEREVENT + 1
fadingOutEvent = pygame.USEREVENT + 2
pygame.time.set_timer(fadingOutEvent, 10)
timerLengthSecs = 900
currentTimerLengthSecs = timerLengthSecs
timer_surf = largerFont.render("05:00", False, "white")
timer_rect = timer_surf.get_rect(center = (width/2, 100))

# -------------------------------------------- SURVEY  -------------------------------------------------------- #

def hardestPuzzleQuestion():
    forceCustomDialogue(3, ["oh okay...", "uhhhh \"Which do you think was the easiest?\"", " "], ["what.png", "what.png", "what.png"])

def difficultyQuestion():
    forceCustomDialogue(3, ["mhm uh huh", "\"Was the game as a whole too easy?\"", "\"Or too hard?\"", " "], ["what.png", "what.png", "what.png", "what.png"])

def usernameQuestion():
    forceCustomDialogue(3, ["alright alright awesome", "there's also like one more thing we need,", "\"Can you please give us a nickname?\"", " "], ["what.png", "what.png", "what.png", "what.png"])

def surveyConclusion():
    forceCustomDialogue(3, ["cool cool cool", "uh thank you for \"answering our survey!\"", " "], ["what.png", "what.png", "what.png"])

currentSurveyQuestion = 1

surveyQuestionDict = {
    2 : hardestPuzzleQuestion,
    3 : difficultyQuestion,
    4 : usernameQuestion,
    5 : surveyConclusion
}

surveyUsernameInputBox = pygame.Rect(600, height/2, 400, 55)
surveyUsernameText = ""

# -------------------------------------------- GAME VARIABLES -------------------------------------------------------- #

# Game State Variables
run = True
dialogueInitiated = False
changingRoomsCond = False
puzzleTextActive = False
inventoryActive = False
leaderBoardActive = False

timerEnabled = False
typing = False
fadingOut = False

movement = False
interactable = True

roomID = 0
hintID = 0
currentPuzzleID = 1

puzzle1Time = 0
puzzle2Time = 0
puzzle3Time = 0

hintsUsedPuzzle1 = 0
hintsUsedPuzzle2 = 0
hintsUsedPuzzle3 = 0
hints = hintsUsedPuzzle1 + hintsUsedPuzzle2 + hintsUsedPuzzle3

#leaderBoard1st = f"1st: {retrieve_data_from_sheet('A2')}: {retrieve_data_from_sheet('B2')}"
#leaderBoard2nd = f"2nd: {retrieve_data_from_sheet('A3')}: {retrieve_data_from_sheet('B3')}"
#leaderBoard3rd = f"3rd: {retrieve_data_from_sheet('A4')}: {retrieve_data_from_sheet('B4')}"
#leaderBoard4th = f"4th: {retrieve_data_from_sheet('A5')}: {retrieve_data_from_sheet('B5')}"
#leaderBoard5th = f"5th: {retrieve_data_from_sheet('A6')}: {retrieve_data_from_sheet('B6')}"

screenTransitionAlpha = 0
dummyAlpha = 255

roomDict[roomID]()

# -------------------------------------------- GAME LOOP -------------------------------------------------------- #


while run:
    event_list = pygame.event.get()
    for event in event_list:
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_e and interactable and not typing: # inventory handler
                inventoryActive = True if inventoryActive == False else False
            if event.key == pygame.K_h and not changingRoomsCond and not dialogueInitiated and not typing and currentTimerLengthSecs > 60 and roomID != 2763: # hint handler
                try:
                    dummy = Environment(player.xpos, player.ypos, player.image.get_width(), player.image.get_height(), False, False, "player/cedric.png")
                    player.xpos, player.ypos = 0, 1100
                    player.update()
                    dummy_group.add(dummy)
                    hintDialogue.text = hintDict[int(f'{currentPuzzleID}{hintID}')]
                    hintDialogue.expression = []
                    for i in range(len(hintDialogue.text)):
                        hintDialogue.expression.append("player/cedricHeadshot.png")
                    timerEnabled = False
                    interactable = False
                    forceDialogue(hintDialogue)
                    hintID += 1
                    currentTimerLengthSecs -= 30 if hintID == 1 or hintID == 2 else 45
                except KeyError:
                    hintDialogue.text = ["(No hints available.)", " "]
                    hintDialogue.expression = ["what.png", "what.png"]
                    forceDialogue(hintDialogue)
                    interactable = False
            if event.key == pygame.K_f and any(pygame.sprite.spritecollide(player, dialogueTrigger_group, False)) and interactable and not typing: # dialogue handler
                movement = False
                dialogueInitiated = True
                interactable = False
                counter = 0
            elif event.key == pygame.K_f and any(pygame.sprite.spritecollide(player, newRoomTrigger_group, False)) and interactable and not typing: # new room handler
                changingRoomsCond = True
                interactable = False
                timerEnabled = False
                movement = False
            elif event.key == pygame.K_f and any(pygame.sprite.spritecollide(player, puzzleTrigger_group, False)) and interactable and not typing: # puzzle trigger handler
                if puzzleTextActive:
                    puzzleTextActive = False
                    typing = False
                    movement = True
                else:
                    puzzleTextActive = True
                    movement = False
            elif event.key == pygame.K_f and roomID == 0:
                forceNewRoom(studyRoomTrigger)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and textDone and activeMessage < len(wholeMessage) - 1:
                textDone = False
                activeMessage += 1
                counter = 0
            elif event.key == pygame.K_RETURN and not textDone and counter > 1 and roomID != 2763:
                counter += 9999
        if event.type == pygame.MOUSEBUTTONDOWN:
            if leaderBoardButton.rect.collidepoint(event.pos) and not changingRoomsCond and roomID == 0:
                leaderBoardActive = False if leaderBoardActive else True
            if exitButton.rect.collidepoint(event.pos):
                pygame.time.wait
                puzzleTextActive = False
                leaderBoardActive = False
                movement = True
            elif startMenu.rect.collidepoint(event.pos) and not leaderBoardActive and not changingRoomsCond and roomID == 0:
                forceNewRoom(studyRoomTrigger)
            if journalInputBox.collidepoint(event.pos) and puzzleTextActive and puzzleList[0].pID == 0:
                typing = True if not typing else False
                journalInputText = ""
            elif roomID == 2763:
                pass
            else:
                typing = False
        if timerEnabled: 
            if event.type == timerEvent:
                currentTimerLengthSecs -= 1 if currentTimerLengthSecs > -1 else 0
        if fadingOut:
            if event.type == fadingOutEvent:
                dummyAlpha -= 1
                dummy.image.set_alpha(dummyAlpha)
                if dummyAlpha < 0:
                    pygame.time.wait(1000)
                    fadingOut = False
                    forceNewRoom(backToStartMenu)

    environment_group.draw(screen)
    dialogueTrigger_group.draw(screen)
    newRoomTrigger_group.draw(screen)
    puzzleTrigger_group.draw(screen)
    playerGroup.draw(screen)
    dummy_group.draw(screen)
    try:
        roomExtraDict[roomID]()
    except KeyError:
        print("couldn't find an extra function to run (MAY OR MAY NOT BE A PROBLEM)")

    screenTransition.image.set_alpha(screenTransitionAlpha)

    if interactable:
        if any(pygame.sprite.spritecollide(player, dialogueTrigger_group, False)) or any(pygame.sprite.spritecollide(player, newRoomTrigger_group, False)) or any(pygame.sprite.spritecollide(player, puzzleTrigger_group, False)):
            screen.blit(interactSign.image, (player.rect.centerx, player.rect.top - interactSign.rect.h))

    screen.blit(screenTransition.image, screenTransition.rect)

    if changingRoomsCond:
        inventoryActive = False
        movement = False
        newRoomTriggerList = pygame.sprite.spritecollide(player, newRoomTrigger_group, False)
        try:
            changingRooms(newRoomTriggerList[0].rID, newRoomTriggerList[0].newX, newRoomTriggerList[0].newY, newRoomTriggerList[0].speed, newRoomTriggerList[0].waitMS)
        except IndexError:
            pass
        if bool(newRoomTriggerList) == False:
            screenTransitionAlpha -= 10
        if screenTransitionAlpha <= 0:
            changingRoomsCond = False
            movement = True
            screenTransitionAlpha = 0
            try:
                newRoomEventDict[roomID]()
            except KeyError:
                print("could not find an event to run after room change finished (MAY OR MAY NOT BE A PROBLEM)")

    if puzzleTextActive:
        movement = False
        puzzleList = pygame.sprite.spritecollide(player, puzzleTrigger_group, False)

        puzzleDict[puzzleList[0].pID]()

    if dialogueInitiated:
        inventoryActive = False
        #movement = False
        dialogueList = pygame.sprite.spritecollide(player, dialogueTrigger_group, False)
        try:
            conversation(dialogueList[0].text, dialogueList[0].expression, dialogueList[0].speed)
        except IndexError:
            pass
        if dialogueDone:
            interactable = True
            dialogueDone = False
            try: 
                dialogueEventDict[dialogueList[0].text[len(dialogueList[0].text) - 2]]()
            except KeyError:
                print("could not find an event to run after dialogue finished (MAY OR MAY NOT BE A PROBLEM)")

    if timerEnabled:
        if currentTimerLengthSecs > -1:
            timerDisplaySecs = currentTimerLengthSecs % 60
            timerDisplayMins = int(currentTimerLengthSecs/60) % 60
        else:
            dialogueInitiated, puzzleTextActive, changingRoomsCond, typing, textDone, dialogueDone, timerEnabled = False, False, False, False, False, False, False
            counter = 0
            activeMessage = 0
            if dummy not in dummy_group:
                dummy = Environment(player.xpos, player.ypos, player.image.get_width(), player.image.get_height(), False, False, "player/cedric.png")
                dummy_group.add(dummy)
            player.xpos, player.ypos = 1800, 0
            player.update()
            forceDialogue(deathDialogue)
        timer_surf = largerFont.render(f"{timerDisplayMins:02}:{timerDisplaySecs:02}", False, "White")
        screen.blit(timer_surf, timer_rect)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()