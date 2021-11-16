from room import Room
from items import Equipamiento, Item, Comestible, Mision, Transportador
from player import Player
from npc import NPC
from stack import Stack, inverse
from parser_commands import Parser


class Game:
    def __init__(self):
        self.createRooms()
        self.player = Player('jugador 1', 20)
        self.parser = Parser()
        self.stack = Stack()

    def createRooms(self):
        park = Room("in the city centre")
        hospital = Room("in the hospital reception")
        emergency = Room("in the emegency room")
        gym = Room("in the gym")
        market = Room("in the market")
        drinks = Room("in the drinks area")
        deposit= Room("in the deposit")
        bank = Room("in the bank")
       
        park.setExits(hospital, market, bank, gym, None, None)
        hospital.setExits(None, None, park, emergency, None, None)
        emergency.setExits(None, hospital, None, None, None, None)
        gym.setExits(None, park, None, None, None, None)
        market.setExits(None, None, drinks, park, None, deposit)
        drinks.setExits(market, None, None, bank, None, None)
        deposit.setExits(None, None, None, None, market, None)
        bank.setExits(park, drinks, None, None, None, None)

        #items
        banco = Item ('banco', "Esto es un banco para descansar", 19, picked_up=False)
        botiquin = Item ('botiquin', "Esto es un botiquin de primeros auxilios", 5)
        manzana  = Comestible ('manzana','Esto es una manzana mágica', 0.15, 10, 'strenght')
        botella = Comestible ('botella', "Esto es una botella de agua", 0.5, 20, 'agility')
        galleta = Comestible ('galleta', "Esto es una galleta mágica", 0.1, 5, 'max_weight')
        energizante = Comestible ('energizante','Esto es una barra energizante', 0.25, 10, 'strenght')
        escudo = Equipamiento ('escudo', "Esto es un escudo antiguo", 10, 5, 'defense')
        antiguallave = Mision ('antiguallave', "Esta es la llave mágica para hablar con el Mago",0.5)
        teletransportador = Transportador ('teletransportador', "Tranporta a la sala donde fue activado", 5)
        mago= NPC('Mago', 'Has completado la misión') 
   
        park.setItem(banco)
        emergency.setItem(botiquin)
        park.setItem(manzana)
        drinks.setItem(botella)
        market.setItem(galleta)
        gym.setItem(energizante)
        deposit.setItem(escudo)
        market.setItem(antiguallave)
        park.setItem(teletransportador)
        park.NPC = mago
        
        self.currentRoom = park
        return

    def play(self):
        self.printWelcome()

        finished = False
        while(not finished):
            command = self.parser.getCommand()
            finished = self.processCommand(command)
        print("Thank you for playing.  Good bye.")

    def printWelcome(self):
        print()
        print("Welcome to the World of Zuul!")
        print("World of Zuul is a new, incredibly boring adventure game.")
        print("Type 'help' if you need help.")
        print("")
        self.currentRoom.print_location_information()
        print()

    def processCommand(self, command):
        wantToQuit = False

        if(command.isUnknown()):
            print("I don't know what you mean...")
            return False

        commandWord = command.getCommandWord()
        if(commandWord == "help"):
            self.printHelp()
        elif(commandWord == "go"):
            self.goRoom(command)
        elif(commandWord == "quit"):
            wantToQuit = self.quit(command)
        elif(commandWord == "look"):
            self.look_items()
        elif(commandWord == "bag"):
            self.bag_items()
        elif(commandWord == "back"):
            self.goBack()
        elif(commandWord == "take"):
            self.takeItem(command)
        elif(commandWord == "drop"):
            self.dropItem(command)
        elif(commandWord == "eat"):
            self.eatItem(command)
        elif(commandWord == "open"):
            self.openTransp(command)
        elif(commandWord == "activate"):
            self.activateTransp(command)
        elif(commandWord == "talk"):
            self.talkNpc(command)

        return wantToQuit

    def printHelp(self):
        print("You are lost. You are alone. You wander")
        print("around at the university.")
        print()
        print("Your command words are:")
        print("   go quit help look back bag take drop eat open activate")

    def goRoom(self, command):
        if(not command.hasSecondWord()):
            print("Go where?")
            return

        direction = command.getSecondWord()
        nextRoom = self.currentRoom.get_exit(direction)
       
        if(nextRoom is None):
            print("There is no door!")
        else:
            self.currentRoom = nextRoom
            self.currentRoom.print_location_information()
            self.stack.push(direction)
            print()
    
    def takeItem(self, command):
        if(not command.hasSecondWord()):
            print("Take what?")
            return

        item_name = command.getSecondWord()
        item = self.currentRoom.getItem(item_name)
       
        if(item is None):
            print("There is not item in the room with this name!")
        else:
            if(item.picked_up):
                if(self.player.can_picked_up_new_item(item.weight)):
                    self.player.setItem(item)
                else:
                    print('no puedes levantar tanto peso...')
                    self.currentRoom.setItem(item)
            else:
                print('ese item no puede ser levantado')
                self.currentRoom.setItem(item)

    def openTransp(self, command):
        if(not command.hasSecondWord()):
            print("Open what?")
            return
        
        item_name = command.getSecondWord()
        item = self.player.getItem(item_name)
       
        if(item is None):
            print("There is not item in the player bag with this name!")
        else:
            if(isinstance(item,Transportador)):
                print('room set to back is',self.currentRoom.description)
                item.room_volver = self.currentRoom
            else:
                print("Este item no es transportador, no es posible abrirlo")
                self.player.setItem(item)
            
    def activateTransp(self, command):
        if(not command.hasSecondWord()):
            print("Activate what?")
            return
        
        item_name = command.getSecondWord()
        item = self.player.getItem(item_name)
       
        if(item is None):
            print("There is not item in the player bag with this name!")
        else:
            if(isinstance(item,Transportador)):
                print('teletransportando')
                self.currentRoom = item.room_volver
            else:
                print("el teletransportador no se abrió todavia")
                self.player.setItem(item)
                
    def talkNpc(self, command):
        if(not command.hasSecondWord()):
            print("Talk what?")
            return
        
        item_name = command.getSecondWord()
        item = self.player.getItem(item_name)
       
        if(item is None):
            print("There is not item in the player bag with this name!")
        else:
            if(isinstance(item,Transportador)):
                print('teletransportando')
                self.currentRoom = item.room_volver
            else:
                print("el teletransportador no se abrió todavia")
                self.player.setItem(item)
        
    def dropItem(self, command):
        if(not command.hasSecondWord()):
            print("Drop what?")
            return

        item_name = command.getSecondWord()
        item = self.player.getItem(item_name)
       
        if(item is None):
            print("There is not item in the player bag with this name!")
        else:
            self.currentRoom.setItem(item)

    def eatItem(self, command):
        if(not command.hasSecondWord()):
            print("Eat what?")
            return

        item_name = command.getSecondWord()
        item = self.player.getItem(item_name)
       
        if(item is None):
            print("There is not item in the player bag with this name!")
        else:
            if(isinstance(item, Comestible)):
                response = item.comer(self.player)
                if(not response):
                    self.player.setItem(item)
            else:
                print('este item no es comestible')
                self.player.setItem(item)

    def look_items(self):
        self.currentRoom.print_items_information()
        
    def look_NPC(self):
        self.currentRoom.print_npc_info()

    def bag_items(self):
        self.player.print_items_information()
    
    def goBack(self):
        direction = self.stack.pop()
        if(direction):
            nextRoom = self.currentRoom.get_exit(direction)
       
            if(nextRoom is None):
                print("There is no door! to go", direction)
                self.stack.push(inverse[direction])
            else:
                self.currentRoom = nextRoom
                self.currentRoom.print_location_information()
                print()
        else:
            print('you are in the initial position, can not go back')

    def quit(self, command):
        if(command.hasSecondWord()):
            print("Quit what?")
            return False
        else:
            return True

g = Game()
g.play() 