import pygame 

pygame.init()

# pygame screen
width = 1600
height = 900

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("idp")
clock = pygame.time.Clock()

# Music and Sounds
click = pygame.mixer.Sound("dialogueSFX.mp3")
click.set_volume(0.1)
deepClick = pygame.mixer.Sound("dialogueSFXLower.mp3")
deepClick.set_volume(0.1)

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
        if inventoryActive == True:
            screen.blit(inventoryEnv.image, inventoryEnv.rect)

    def player_input(self):
        global movement
        keys = pygame.key.get_pressed()
        if movement:
            if keys[pygame.K_LEFT] or keys[pygame.K_a] and self.rect.left >= width - width: 
                self.xpos -= 1*self.speed
                if "left" not in self.facing:
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.facing = "left"
            if keys[pygame.K_RIGHT] or keys[pygame.K_d] and self.rect.right <= width:
                self.xpos += 1*self.speed
                if "right" not in self.facing:
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.facing = "right"
            if keys[pygame.K_UP] or keys[pygame.K_w] and self.rect.top >= 450:
                self.ypos -= 1*self.speed
            if keys[pygame.K_DOWN] or keys[pygame.K_s] and self.rect.bottom <= height:
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
        #pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

class Environment(pygame.sprite.Sprite): # class for handling images that are displayed on the game
    def __init__(self, xpos, ypos, width, height, collidable:bool, image = "what.png"):
        super().__init__()
        self.xpos = xpos
        self.ypos = ypos
        self.image = pygame.transform.scale(pygame.image.load(image).convert_alpha(), (width, height))
        self.rect = self.image.get_rect(center = (self.xpos, self.ypos))
        self.collidable = collidable

    def apply_change(self):
        self.rect.centerx = self.xpos
        self.rect.centery = self.ypos

    def update(self):
        self.apply_change()

class DialogueTrigger(Environment): # class for handling images that will play dialogue when F key is pressed
    def __init__(self, xpos, ypos, width, height, collidable:bool, speed, text, expression, image = "what.png"):
        super().__init__(xpos, ypos, width, height, collidable, image)
        self.text = text
        self.expression = expression
        self.speed = speed

class NewRoomTrigger(Environment): # class for handling images that will transport the player to a new room when the F key is pressed
    def __init__(self, xpos, ypos, width, height, collidable:bool, rID, newX, newY, speed, waitMS, image = "what.png"):
        super().__init__(xpos, ypos, width, height, collidable, image)
        self.rID = rID
        self.newX = newX
        self.newY = newY
        self.speed = speed
        self.waitMS = waitMS

class PuzzleTrigger(Environment):
    def __init__(self, xpos, ypos, width, height, collidable:bool, pID, image = "what.png"):
        super().__init__(xpos, ypos, width, height, collidable, image)
        self.pID = pID
# --------------------------------------------- FUNCTIONS -------------------------------------------------------- #

textDone = False
counter = 0
activeMessage = 0
dialogueDone = False
voiceDict = {
    "the yippee stares back.png" : deepClick
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
        except:
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
    global dialogueInitiated
    dialogue.xpos, dialogue.ypos = player.xpos, player.ypos
    dialogue.update()
    dialogueTrigger_group.add(dialogue)
    dialogueInitiated = True

def forceNewRoom(roomTrigger):
    global changingRoomsCond
    roomTrigger.xpos, roomTrigger.ypos = player.xpos, player.ypos
    roomTrigger.update()
    newRoomTrigger_group.add(roomTrigger)
    changingRoomsCond = True

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
startMenu = Environment(width/2, height/2, width, height, False, "CoverImageforapp.png")

# Room 1
studyFloor = Environment(width/2, height/2, width, height, False, "studyRoom\studyRoomBGI.png")
amalgamation = Environment(1300, 600, 400, 600, True, "the yippee stares back.png")

# Misc Environments
dummy = Environment(1700, 1000, player.image.get_width(), player.image.get_height(), False, "player/cedric.png")
dialogueBox = Environment(width/2, 725, 1500, 250, False, "placeholderDialogueBox.png")
interactSign = Environment(1700, 1000, 100, 100, False, "miscAssets/F_key.png")
exitButton = Environment(1700, 1000, 100, 100, False, "exitButton.png")
screenTransition = Environment(width/2, height/2, width, height, False, "solidBlack.png")
inventoryEnv = Environment(1400, height/2, 350, 850, False, "solidBlack.png")
inventoryEnv.image.set_alpha(200)

# Dialogue Triggers (FOR THE DIALOGUE TRIGGER, ALWAYS ADD ONE EXTRA BLANK DIALOGUE TO THE LIST ALONG WITH A RANDOM IMAGE BECAUSE REASONS)

studyInitDialogue = DialogueTrigger(1700, 1000, 100, 100, False, 3, ["What.. where am I?", "I feel so cold.", "HUH?? WHY AM I ON THE FLOOR?", " "], ["player/cedricHeadshot.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png"])
studyInitDialogue.image.set_alpha(0)
studyGrandfatherClockDialogue = DialogueTrigger(100, 500, 100, 700, False, 3, ["(It's a very nice looking grandfather clock.)", "(Nevermind that, you need to hurry!)", "(After all, the CLOCK is TICKING...)", " "], ["player/cedricHeadshot.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png"])
studyGrandfatherClockDialogue.image.set_alpha(0)
studyPuzzleDialogue = DialogueTrigger(1700, 1000, 100, 100, False, 3, ["(You feel a weird sense of unfulfillment...)", "(Perhaps you should try something else?...)", " "], ["player/cedricHeadshot.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png"])
studyPuzzleDialogue.image.set_alpha(0)
studyAmalPlayerDialogue = DialogueTrigger(1700, 1000, 100, 100, False, 3, ["Leave me in my misery.", "You'll have all eternity to see us later.", "Who are you? Let me out of here!", "Who am I? You don't even know who you are.", "Hogwash. Of course I know who I am.", "I'm...", "I am, uhh...", "It's no use. Your fate is eternity here.", "Better if you spend it alone while you can.", "The less you know, the better.", "Ignorance is bliss, my friend...", "But I must know! What is this?", "Well if you insist...you are gone.", "Dead.", "Deceased.", "Dead?!", "What do you mean \"dead\"!!", "You exist in a state of wandering.", "After your death, you ended up here.", "Eventually, your spiritual energy will combine with us.", "Permanently trapped in this cursed house.", "Most move onto the stars, most are brought peace.", "But not us...", "We are not granted the same privileges, taken so easily.", "Why so verbose, \"move onto the stars\"?", "When one's soul, and mind, are at complete tranquility.", "Only then, does one's world go black,", "awakening amongst stars, glowing with radiance.", "It is, only after what appears to be reality bending,", "periods of time, do these concepts become self-evident.", "For that reason, I will put it in layman's terms;", "Find out the motives behind your appearance here,", "and you'll become one with the stars.", "You're incomplete.", "Why- you! I'll show you!", "I'll find my way out of this blasted place!", "Outside of this room, you're blind.", "Literally, and metaphorically. Try finding a light.", " "], ["the yippee stares back.png", "the yippee stares back.png", "player/cedricHeadshot.png", "the yippee stares back.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png", "the yippee stares back.png", "the yippee stares back.png", "the yippee stares back.png", "the yippee stares back.png", "player/cedricHeadshot.png", "the yippee stares back.png", "the yippee stares back.png", "the yippee stares back.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png", "the yippee stares back.png","the yippee stares back.png","the yippee stares back.png","the yippee stares back.png","the yippee stares back.png","the yippee stares back.png","the yippee stares back.png", "player/cedricHeadshot.png", "the yippee stares back.png","the yippee stares back.png","the yippee stares back.png","the yippee stares back.png","the yippee stares back.png","the yippee stares back.png","the yippee stares back.png","the yippee stares back.png","the yippee stares back.png", "player/cedricHeadshot.png","player/cedricHeadshot.png", "the yippee stares back.png", "the yippee stares back.png", "the yippee stares back.png"])
studyAmalPlayerDialogue.image.set_alpha(0)

hintDialogue = DialogueTrigger(1700, 1000, 100, 100, False, 3, ["placeholder"], ["what.png"])
hintDialogue.image.set_alpha(0)

deathDialogue = DialogueTrigger(1700, 1000, 100, 100, False, 5, ["Uh oh...", "I don't feel so good...", " "], ["player/cedricHeadshot.png", "player/cedricHeadshot.png", "player/cedricHeadshot.png"])

# New Room Triggers
backToStartMenu = NewRoomTrigger(1500, 800, 100, 100, False, 0, 1800, 1100, 2, 3000, "placeholderNewRoomTrigger.png")
studyRoomTrigger = NewRoomTrigger(0, 1100, 100, 100, False, 1, 978, 842, 2, 3000)

# Puzzle 1
journal = PuzzleTrigger(742, 559, 73, 100, False, 0, "studyRoom\journalAsset.png")
journalContents = Environment(width/2, height/2, 1200, 750, False, "placeholderJournalContents.png")
journalDialogue = DialogueTrigger(742, 559, 73, 100, False, 3, ["What's this?", " "], ["player/cedricHeadshot.png", "player/cedricHeadshot.png"], "studyRoom\journalAsset.png")
journalInputBox = pygame.Rect(900, 700, 400, 55)
journalInputText = ""
journalInputTextSurf = font.render(journalInputText, False, (255, 255, 255))

# Puzzle 2
scroll = PuzzleTrigger(1700, 1000, 100, 100, False, 1, "studyRoom\scrollAsset.png") # CODE FUNCTIONALITY LATER BRUH!!!!!!

# Functions for adding the different things in a room to the correct group, every room is assigned a specific roomID based on the room dictionary. (also some specific things that only need to ran once)

def startScreen():
    global interactable
    environment_group.add(startMenu)
    interactable = True

def study():
    environment_group.add(studyFloor)
    dialogueTrigger_group.add(journalDialogue, studyGrandfatherClockDialogue)
    player.image = pygame.transform.rotate(player.image, 90)
    player.rect = player.image.get_rect(center = (player.xpos, player.ypos))


roomDict = {
    0 : startScreen,
    1 : study, 
}

# Functions for additional things that have to constantly happen when entering a new room, such as the player updating or drawing additional text

def startScreenExtra():
    pass

def studyExtra():
    player.update()

roomExtraDict = {
    0 : startScreenExtra,
    1 : studyExtra
}

# Functions for dialogue events that happen after a specific dialogue plays

def dialogueKill():
    global interactable
    pygame.sprite.spritecollide(player, dialogueTrigger_group, False)[0].kill()
    interactable = True

def hintKill():
    dialogueKill()
    player.xpos, player.ypos = dummy.xpos, dummy.ypos
    player.update()
    dummy.kill()

def replaceDialogue():
    journalDialogue.kill()
    puzzleTrigger_group.add(journal)

def studyPuzzleInit():
    global timerEnabled
    dialogueKill()
    player.image = pygame.transform.rotate(player.image, -90)
    player.rect = player.image.get_rect(center = (player.xpos, player.ypos))
    player.rect.bottom = studyFloor.rect.bottom
    player.xpos, player.ypos = player.rect.centerx, player.rect.centery
    timerEnabled = True
    pygame.time.set_timer(timerEvent, 1000)

def fadeOut():
    global fadingOut, timerEnabled, movement, interactable
    dummy.image = pygame.transform.rotate(player.image, 90)
    dummy.rect = dummy.image.get_rect(center = (dummy.xpos, dummy.ypos))
    movement, interactable = False, False
    fadingOut = True

def amalgamationDialogueKill():
    global timerEnabled, currentPuzzleID
    dialogueKill()
    scroll.rect.centerx, scroll.rect.centery = amalgamation.rect.centerx, amalgamation.rect.bottom - 70
    scroll.xpos, scroll.ypos = scroll.rect.centerx, scroll.rect.centery
    puzzleTrigger_group.add(scroll)
    amalgamation.kill()
    currentPuzzleID = 2
    timerEnabled = True

dialogueEventDict = {
    "HUH?? WHY AM I ON THE FLOOR?" : studyPuzzleInit,
    "What's this?" : replaceDialogue,
    "(Perhaps you should try something else?...)" : dialogueKill,
    "Literally, and metaphorically. Try finding a light." : amalgamationDialogueKill,

    "(Such as the FIRST thing they would do for the day.)" : hintKill,
    "(But in what order should it be arranged in...?)" : hintKill,
    "(are CONNECTED.)" : hintKill,
    "(No hints available.)" : hintKill,

    "I don't feel so good..." : fadeOut
}

# Functions for new room events that happen after the new room COMPLETELY loads (not like the other room dict)

def wakeUp():
    pygame.time.wait(5000)
    forceDialogue(studyInitDialogue)

def death():
    global currentTimerLengthSecs, hintID, interactable, dummyAlpha
    interactable = True
    currentTimerLengthSecs = timerLengthSecs
    dummyAlpha = 255
    dummy.image.set_alpha(dummyAlpha)
    hintID = 1


newRoomEventDict = {
    0 : death,
    1 : wakeUp,
}

# HINT DICTIONARY AND STUFF YEAH

hintDict = {
    11 : ["(Oh, it's an old journal.)",  "(The type someone would use to write reminders.)", "(Such as the FIRST thing they would do for the day.)", " "],
    12 : ["(But, you realize the entries are out of ORDER.)", "(This mildly irritates you...)", "(Maybe you should rearrange them properly.)",  "(But in what order should it be arranged in...?)", " "],
    13 : ["(Maybe that CODE at the bottom,)", "(and the ORDER of the poem,)", "(along with the FIRST letter,)", "(are CONNECTED.)", " "]
}

# PUZZLE STUFF YEAH UHUH YUP

def journalZoom():
    screen.blit(journalContents.image, journalContents.rect)
    exitButton.rect.centerx, exitButton.rect.centery = journalContents.rect.right, journalContents.rect.top
    screen.blit(exitButton.image, exitButton.rect)
    if typing:
        pygame.draw.rect(screen, (0, 0, 0), journalInputBox, 2)
    else:
        pygame.draw.rect(screen, (128, 128, 128), journalInputBox, 2)
    journalInputTextSurf = font.render(journalInputText, False, (255, 255, 255))
    screen.blit(journalInputTextSurf, (journalInputBox.x + 5, journalInputBox.y + 8))

def scrollZoom(): # WIP
    screen.blit()  

puzzleDict = {
    0 : journalZoom,
}

def journalTextSuccess():
    global journalInputText, typing, puzzleActive, timerEnabled
    journalInputText = ""
    typing = False
    puzzleActive = False
    timerEnabled = False
    environment_group.add(amalgamation)
    pygame.time.delay(500)
    forceDialogue(studyAmalPlayerDialogue)

textCheckDict = {
    "1amalgamation" : journalTextSuccess
}

# -------------------------------------------- PUZZLE TIMER -------------------------------------------------------- #

timerEvent = pygame.USEREVENT + 1
fadingOutEvent = pygame.USEREVENT + 2
pygame.time.set_timer(fadingOutEvent, 10)
timerLengthSecs = 300
currentTimerLengthSecs = timerLengthSecs
timer_surf = largerFont.render("05:00", False, "white")
timer_rect = timer_surf.get_rect(center = (width/2, 100))

# -------------------------------------------- GAME VARIABLES -------------------------------------------------------- #

# Game State Variables
run = True
dialogueInitiated = False
changingRoomsCond = False
puzzleActive = False
inventoryActive = False

timerEnabled = False
typing = False
fadingOut = False

movement = False
interactable = True

roomID = 0
hintID = 1
currentPuzzleID = 1 # not used for anything right now

screenTransitionAlpha = 0
dummyAlpha = 255

roomDict[roomID]()

# -------------------------------------------- GAME LOOP -------------------------------------------------------- #


while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_e and interactable and not typing: # inventory handler
                inventoryActive = True if inventoryActive == False else False
            if event.key == pygame.K_h and not changingRoomsCond and not dialogueInitiated and not typing and currentTimerLengthSecs > 60: # hint handler
                try:
                    dummy = Environment(player.xpos, player.ypos, player.image.get_width(), player.image.get_height(), False, "player/cedric.png")
                    hintDialogue.text = hintDict[int(f'{currentPuzzleID}{hintID}')]
                    hintDialogue.expression = []
                    for i in range(len(hintDialogue.text)):
                        hintDialogue.expression.append("player/cedricHeadshot.png")
                    player.xpos, player.ypos = 0, 1100
                    player.update()
                    dummy_group.add(dummy)
                    forceDialogue(hintDialogue)
                    interactable = False
                    currentTimerLengthSecs -= 30 if hintID == 1 or hintID == 2 else 45
                    hintID += 1
                except:
                    hintDialogue.text = ["(No hints available.)", " "]
                    hintDialogue.expression = ["what.png", "what.png"]
                    forceDialogue(hintDialogue)
                    interactable = False
            if event.key == pygame.K_f and any(pygame.sprite.spritecollide(player, dialogueTrigger_group, False)) and interactable and not typing: # dialogue handler
                dialogueInitiated = True
            elif event.key == pygame.K_f and any(pygame.sprite.spritecollide(player, newRoomTrigger_group, False)) and interactable and not typing: # new room handler
                changingRoomsCond = True
            elif event.key == pygame.K_f and any(pygame.sprite.spritecollide(player, puzzleTrigger_group, False)) and interactable and not typing: # puzzle trigger handler
                if puzzleActive:
                    puzzleActive = False
                    typing = False
                    movement = True
                else:
                    puzzleActive = True
            elif event.key == pygame.K_f and roomID == 0:
                forceNewRoom(studyRoomTrigger)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and textDone and activeMessage < len(wholeMessage) - 1:
                textDone = False
                activeMessage += 1
                counter = 0
            if typing:
                if event.key == pygame.K_BACKSPACE:
                    journalInputText = journalInputText[:-1]
                    journalInputTextSurf = font.render(journalInputText, False, (255, 255, 255))
                elif event.key == pygame.K_RETURN and currentPuzzleID == 1:
                    try:
                        textCheckDict[f"{currentPuzzleID}{journalInputText}"]
                        journalInputText = ""
                        typing = False
                        puzzleActive = False
                        timerEnabled = False
                        environment_group.add(amalgamation)
                        pygame.time.delay(500)
                        forceDialogue(studyAmalPlayerDialogue)
                    except KeyError:
                        journalInputText = ""
                        forceDialogue(studyPuzzleDialogue)
                elif journalInputTextSurf.get_width() >= 380:
                    pass
                else:
                    journalInputText += event.unicode
                    journalInputTextSurf = font.render(journalInputText, False, (255, 255, 255))
        if event.type == pygame.MOUSEBUTTONDOWN:
            if exitButton.rect.collidepoint(event.pos):
                puzzleActive = False
                typing = False
                movement = True
            if journalInputBox.collidepoint(event.pos):
                typing = True if not typing else False
            elif startMenu.rect.collidepoint(event.pos) and not changingRoomsCond and roomID == 0:
                forceNewRoom(studyRoomTrigger)
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
        movement = False
        newRoomTriggerList = pygame.sprite.spritecollide(player, newRoomTrigger_group, False)
        try:
            changingRooms(newRoomTriggerList[0].rID, newRoomTriggerList[0].newX, newRoomTriggerList[0].newY, newRoomTriggerList[0].speed, newRoomTriggerList[0].waitMS)
        except:
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

    if puzzleActive:
        movement = False
        puzzleList = pygame.sprite.spritecollide(player, puzzleTrigger_group, False)
        puzzleDict[puzzleList[0].pID]()

    if dialogueInitiated:
        movement = False
        dialogueList = pygame.sprite.spritecollide(player, dialogueTrigger_group, False)
        try:
            conversation(dialogueList[0].text, dialogueList[0].expression, dialogueList[0].speed)
        except:
            print("im going to FUCKING DIE")
        if dialogueDone:
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
            dialogueInitiated, puzzleActive, changingRoomsCond, typing = False, False, False, False
            textDone = False
            counter = 0
            activeMessage = 0
            dialogueDone = False
            if dummy not in dummy_group:
                dummy = Environment(player.xpos, player.ypos, player.image.get_width(), player.image.get_height(), False, "player/cedric.png")
                dummy_group.add(dummy)
            player.xpos, player.ypos = 1800, 0
            player.update()
            forceDialogue(deathDialogue)
            timerEnabled = False
        timer_surf = largerFont.render(f"{timerDisplayMins:02}:{timerDisplaySecs:02}", False, "White")
        screen.blit(timer_surf, timer_rect)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()