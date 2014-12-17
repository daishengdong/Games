import pygame
import math
from PodSixNet.Connection import ConnectionListener, connection
from time import sleep

class BoxesGame(ConnectionListener):
    def initSound(self):
        pygame.mixer.music.load("resources/audios/music.wav")
        self.winSound = pygame.mixer.Sound('resources/audios/win.wav')
        self.loseSound = pygame.mixer.Sound('resources/audios/lose.wav')
        self.placeSound = pygame.mixer.Sound('resources/audios/place.wav')
        pygame.mixer.music.play()

    def Network_close(self, data):
        exit()

    def Network_yourturn(self, data):
        #torf = short for true or false
        self.turn = data["torf"]

    def Network_startgame(self, data):
        self.running = True
        self.num = data["player"]
        self.gameid = data["gameid"]

    def Network_place(self, data):
        self.placeSound.play()
        #get attributes
        x = data["x"]
        y = data["y"]
        hv = data["is_horizontal"]
        #horizontal or vertical
        if hv:
            self.boardh[y][x] = True
        else:
            self.boardv[y][x] = True

    def Network_yourturn(self, data):
        #torf = short for true or false
        self.turn = data["torf"]

    def __init__(self):
    	self.justplaced = 10
        self.boardh = [[False for x in range(6)] for y in range(7)]
        self.boardv = [[False for x in range(7)] for y in range(6)]
        #1
        pygame.init()
        pygame.font.init()
        width, height = 389, 489
        #2
        #initialize the screen
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Boxes")
        #3
        #initialize pygame clock
        self.clock = pygame.time.Clock()
        #initialize the graphics
        self.initGraphics()
        self.initSound()
        self.turn = True
        self.owner = [[0 for x in range(6)] for y in range(6)]
        self.me = 0
        self.otherplayer = 0
        self.didiwin = False
        self.running = False
        address = raw_input("Address of Server: ")
        try:
            if not address:
                host, port = "localhost", 8000
            else:
                host, port = address.split(": ")
            self.Connect((host, int(port)))
        except:
            print "Error Connecting to Server"
            print "Usage: ", "host: port"
            print "e.g.", "localhost: 31425"
            exit()
        print "Boxes client started"
        self.running = False
        self.owner = [[0 for x in range(6)] for y in range(6)]
        while not self.running:
            self.Pump()
            connection.Pump()
            sleep(0.01)
        #determine attributes from player #
        if self.num == 0:
            self.turn = True
            self.marker = self.greenplayer
            self.othermarker = self.blueplayer
        else:
            self.turn = False
            self.marker = self.blueplayer
            self.othermarker = self.greenplayer
            
    def drawBoard(self):
        # This draws all of the lines other than the edges.
        for x in range(6):
            for y in range(6):
                if not self.boardh[y][x]:
                    self.screen.blit(self.normallineh, [(x) * 64 + 5, (y) * 64])
                else:
                    self.screen.blit(self.bar_doneh, [(x) * 64 + 5, (y) * 64])
                if not self.boardv[y][x]:
                    self.screen.blit(self.normallinev, [(x) * 64, (y) * 64 + 5])
                else:
                    self.screen.blit(self.bar_donev, [(x) * 64, (y) * 64 + 5])
        for edge in range(6):
            if not self.boardh[6][edge]:
                self.screen.blit(self.normallineh, [edge * 64 + 5, 6 * 64])
            else:
                self.screen.blit(self.bar_doneh, [edge * 64 + 5, 6 * 64])
            if not self.boardv[edge][6]:
                self.screen.blit(self.normallinev, [6 * 64, edge * 64 + 5])
            else:
                self.screen.blit(self.bar_donev, [6 * 64, edge * 64 + 5])
        #draw separators
        for x in range(7):
            for y in range(7):
                self.screen.blit(self.separators, [x * 64, y * 64])

    def drawHUD(self):
        #draw the background for the bottom:
        self.screen.blit(self.score_panel, [0, 389])
        #create font
        myfont = pygame.font.SysFont(None, 32)
         
        #create text surface
        label = myfont.render("Your Turn: ", 1, (255, 255, 255))
         
        #draw surface
        self.screen.blit(label, (10, 400))
        self.screen.blit(self.greenindicator if self.turn else self.redindicator, (130, 395))
        #same thing here
        myfont64 = pygame.font.SysFont(None, 64)
        myfont20 = pygame.font.SysFont(None, 20)

        scoreme = myfont64.render(str(self.me), 1, (255, 255, 255))
        scoreother = myfont64.render(str(self.otherplayer), 1, (255, 255, 255))
        scoretextme = myfont20.render("You", 1, (255, 255, 255))
        scoretextother = myfont20.render("Other Player", 1, (255, 255, 255))

        self.screen.blit(scoretextme, (10, 425))
        self.screen.blit(scoreme, (10, 435))
        self.screen.blit(scoretextother, (280, 425))
        self.screen.blit(scoreother, (340, 435))

    def update(self):
        if self.me + self.otherplayer == 36:
            self.didiwin = True if self.me>self.otherplayer else False
            return 1
        #sleep to make the game 60 fps
        self.justplaced -= 1
        self.clock.tick(60)
        connection.Pump()
        self.Pump()
        #clear the screen
        self.screen.fill(0)
        self.drawBoard()
        self.drawHUD()
        self.drawOwnermap()

        for event in pygame.event.get():
            #quit if the quit button was pressed
            if event.type == pygame.QUIT:
                exit()
     
        #update the screen
        #1
        mouse = pygame.mouse.get_pos()
         
        #2
        xpos = int(math.ceil((mouse[0] - 32) / 64.0))
        ypos = int(math.ceil((mouse[1] - 32) / 64.0))
         
        #3
        is_horizontal = abs(mouse[1] - ypos * 64) < abs(mouse[0] - xpos * 64)
         
        #4
        ypos = ypos - 1 if mouse[1] - ypos * 64 < 0 and not is_horizontal else ypos
        xpos = xpos - 1 if mouse[0] - xpos * 64 < 0 and is_horizontal else xpos
         
        #5
        board = self.boardh if is_horizontal else self.boardv 
        isoutofbounds = False
         
        #6
        try: 
            if not board[ypos][xpos]: self.screen.blit(self.hoverlineh if is_horizontal else self.hoverlinev, [xpos * 64 + 5 if is_horizontal else xpos * 64, ypos * 64 if is_horizontal else ypos * 64 + 5])
        except:
            isoutofbounds = True
            pass
        if not isoutofbounds:
            alreadyplaced = board[ypos][xpos]
        else:
            alreadyplaced = False
        if pygame.mouse.get_pressed()[0] and not alreadyplaced and not isoutofbounds and self.turn and self.justplaced <= 0:
            self.justplaced = 10
            if is_horizontal:
                self.boardh[ypos][xpos] = True
                self.Send({"action": "place", "x": xpos, "y": ypos, "is_horizontal": is_horizontal, "num": self.num, "gameid": self.gameid})
            else:
                self.boardv[ypos][xpos] = True
                self.Send({"action": "place", "x": xpos, "y": ypos, "is_horizontal": is_horizontal, "num": self.num, "gameid": self.gameid})
        pygame.display.flip()
        
    def Network_win(self, data):
        self.owner[data["x"]][data["y"]] = "win"
        self.boardh[data["y"]][data["x"]] = True
        self.boardv[data["y"]][data["x"]] = True
        self.boardh[data["y"] + 1][data["x"]] = True
        self.boardv[data["y"]][data["x"] + 1] = True
        #add one point to my score
        self.winSound.play()
        self.me += 1

    def Network_lose(self, data):
        self.owner[data["x"]][data["y"]] = "lose"
        self.boardh[data["y"]][data["x"]] = True
        self.boardv[data["y"]][data["x"]] = True
        self.boardh[data["y"] + 1][data["x"]] = True
        self.boardv[data["y"]][data["x"] + 1] = True
        #add one to other players score
        self.loseSound.play()
        self.otherplayer += 1

    def initGraphics(self):
        self.normallinev = pygame.image.load("resources/images/normalline.png")
        self.normallineh = pygame.transform.rotate(pygame.image.load("resources/images/normalline.png"), -90)
        self.bar_donev = pygame.image.load("resources/images/bar_done.png")
        self.bar_doneh = pygame.transform.rotate(pygame.image.load("resources/images/bar_done.png"), -90)
        self.hoverlinev = pygame.image.load("resources/images/hoverline.png")
        self.hoverlineh = pygame.transform.rotate(pygame.image.load("resources/images/hoverline.png"), -90)
        self.separators = pygame.image.load("resources/images/separators.png")
        self.redindicator = pygame.image.load("resources/images/redindicator.png")
        self.greenindicator = pygame.image.load("resources/images/greenindicator.png")
        self.greenplayer = pygame.image.load("resources/images/greenplayer.png")
        self.blueplayer = pygame.image.load("resources/images/blueplayer.png")
        self.winningscreen = pygame.image.load("resources/images/youwin.png")
        self.gameover = pygame.image.load("resources/images/gameover.png")
        self.score_panel = pygame.image.load("resources/images/score_panel.png")

    def drawOwnermap(self):
        for x in range(6):
            for y in range(6):
                if self.owner[x][y] != 0:
                    if self.owner[x][y] == "win":
                        self.screen.blit(self.marker, (x * 64 + 5, y * 64 + 5))
                    if self.owner[x][y] == "lose":
                        self.screen.blit(self.othermarker, (x * 64 + 5, y * 64 + 5))

    def finished(self):
        self.screen.blit(self.gameover if not self.didiwin else self.winningscreen, (0, 0))
        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
            pygame.display.flip()

bg = BoxesGame() #__init__ is called right here
while 1:
    if bg.update() == 1:
        break
bg.finished()
