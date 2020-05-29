import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import random, pygame, datetime, socket, sys
from tkinter import *
from tkinter import messagebox
from pymongo import MongoClient
from PIL import Image, ImageTk
from requests import get


#Database
cluster = MongoClient("mongodb+srv://admin:v3CBjmlGg0xVkKW1@farkle-mgfna.gcp.mongodb.net/test?retryWrites=true&w=majority")
db = cluster["farkle"]
servers = db["servers"]

global IP
IP = get('https://api.ipify.org').text

directory = os.getcwd() + '\\'
os.chdir(directory)
sys.path.append(directory + r'\TkTreectrl')
from TkTreectrl import *

pygame.mixer.init()

class Music:
    def __init__(self, player):
        global path
        global soundtracks
        path = directory + r'\soundtrack\\'
        soundtracks = ['A winter tale.mp3' , 'Around the fire.mp3', 'Cloak and Dagger.mp3', 'Drink up.mp3', 'Evening in the tavern.mp3', 'Merchants of novigrad.mp3', 'Tavern theme 1.mp3',
        'Tavern theme 2.mp3', 'Tavern theme 3.mp3', 'Tavern theme 4.mp3', 'The bannered mare.mp3', 'The nightingale.mp3' ]
        random.shuffle(soundtracks)
        self.x = 0
        self.skip = False
        self.playing = True
        pygame.mixer.music.load(path + soundtracks[self.x])
        pygame.mixer.music.set_volume(0.4)
        pygame.mixer.music.play(0)
        self.queue()
        
    def queue(self):
        pos = pygame.mixer.music.get_pos()
        if int(pos) == -1 or self.skip:
            self.skip = False
            self.x += 1
            if self.x == len(soundtracks):
                random.shuffle(soundtracks)
                self.x = 0
            pygame.mixer.music.load(path + soundtracks[self.x])
            pygame.mixer.music.play(0)
        window.after(50, self.queue) 

    def skip_music(self):
        if self.playing:
            self.skip = True

    def pause_play_music(self):
        if self.playing:
            self.playing = False
            pygame.mixer.music.pause()
            pause_play_button0.configure(image=play_image)
            pause_play_button1.configure(image=play_image)
            pause_play_button2.configure(image=play_image)
            pause_play_button3.configure(image=play_image)
            pause_play_button4.configure(image=play_image)
            pause_play_button_wait.configure(image=play_image)

        else:
            self.playing = True
            pygame.mixer.music.unpause()
            pause_play_button0.configure(image=pause_image)
            pause_play_button1.configure(image=pause_image)
            pause_play_button2.configure(image=pause_image)
            pause_play_button3.configure(image=pause_image)
            pause_play_button4.configure(image=pause_image)       
            pause_play_button_wait.configure(image=pause_image)      


class Die:
    'A simple d6 die class'

    def __init__(self, die_number):
        self.dice_images = [die1_image2, die2_image2, die3_image2, die4_image2, die5_image2, die6_image2]
        self.image = die1_image2

        self.die_number = die_number
        self.i = self.die_number - 1

        global dice_numbers
        dice_numbers = []

        self.button_appearing = True
        global buttons_appearing
        buttons_appearing = 6

        self.selected = False

    def roll_number(self):
            self.number = random.randint(1, 6)
            self.get_image()

    def get_image(self):
        global dice_buttons 
        dice_buttons = [die1_button, die2_button, die3_button, die4_button, die5_button, die6_button]
        index = self.number - 1
        self.image = self.dice_images[index]
        dice_buttons[self.i].configure(image=self.image)
        
    def select_die(self):
        if not game.paused:
            if self.selected == False:
                dice_numbers.append(self.number)
                self.selected = True
                dice_buttons[self.i].configure(borderwidth=4)
            elif self.selected == True:
                dice_numbers.remove(self.number)
                self.selected = False
                dice_buttons[self.i].configure(borderwidth=0)
            
            if game.actual_player == 1:
                game.player1_selected_pontuation = game.calculate_pontuation(dice_numbers)
            elif game.actual_player == 2:
                game.player2_selected_pontuation = game.calculate_pontuation(dice_numbers)
            
            game.update_pontuations()
            

class Game:
    def __init__(self):
        self.player1_pontuation = 0
        self.player2_pontuation = 0
        self.player1_turn_pontuation = 0
        self.player2_turn_pontuation = 0
        self.player1_selected_pontuation = 0
        self.player2_selected_pontuation = 0
        self.actual_player = 1
        self.paused = False
        self.unlocked_pause = True
        self.game_time = 0
        self.player1_time = 0
        self.player2_time = 0
        self.win = False
        self.bust_counter = 0
        self.player1_bust_counter = 0
        self.player2_bust_counter = 0
        self.turn_count = 1
        self.countdown_zero = False
        self.bust_bool = False
    
    def start_game(self):
        if first_player.get() == 3:
            self.actual_player = random.choice([1, 2])
        else:
            self.actual_player = first_player.get()
        self.actual_player_text()
        self.win_pontuation = win_pontuation.get()
        self.unselect_and_roll_dice()
        self.bust()
        self.update_pontuations()
        self.add_buttons()
        raise_frame('3')
        window.after(1000, self.count_time)
        window.after(1000, self.decrease_countdown)

    def actual_player_text(self):
        if self.actual_player == 1:
            actual_player.set('Turno do jogador 1')

        else:
            actual_player.set('Turno do jogador 2')

    def switch_player(self):
        self.turn_count += 1

        if self.actual_player == 1:
            self.actual_player = 2
            actual_player.set('Turno do jogador 1')
        else:
            self.actual_player = 1
            actual_player.set('Turno do jogador 2')

        self.actual_player_text()

    def roll_dice(self, e=None):
        if not self.paused:
            self.bigger_than_0 = False

            if self.actual_player == 1 and self.player1_selected_pontuation > 0:
                self.player1_turn_pontuation += self.player1_selected_pontuation
                self.player1_selected_pontuation = 0
                self.bigger_than_0 = True
                
            elif self.actual_player == 2 and self.player2_selected_pontuation > 0:
                self.player2_turn_pontuation += self.player2_selected_pontuation
                self.player2_selected_pontuation = 0
                self.bigger_than_0 = True

            if self.bigger_than_0:
                self.reset_countdown()          
                self.update_pontuations()
                dice_numbers.clear()
                self.remove_buttons()
                self.add_buttons()
                self.unselect_and_roll_dice()
                self.bust()

    def unselect_and_roll_dice(self):
        global dice
        dice = [die1, die2, die3, die4, die5, die6]
        for y in range(6):
            dice[y].selected = False
            dice[y].roll_number()
            dice_buttons[y].configure(borderwidth=0) 

    def calculate_pontuation(self, dice_numbers):
        self.pontuation = 0
        
        no_pontuation_numbers = (2, 3, 4, 6)

        for number in range(1, 7):
            times = dice_numbers.count(number)
            
            if number == 1:
                if times <= 2 and times > 0:
                    self.pontuation += times * 100
                elif times > 2:
                    self.pontuation += (times - 2) * 1000
                
            elif number == 5:
                if times <= 2 and times > 0:
                    self.pontuation += times * 50
                elif times > 2:
                    self.pontuation += (times - 2) * 500
                
            elif number in no_pontuation_numbers:
                if times <= 2 and times > 0:
                    self.pontuation = 0
                    break
                elif times > 2:
                    self.pontuation += (times - 2) * number * 100
                    
            
        dice_numbers_tuple = set(dice_numbers)

        if len(dice_numbers_tuple) == 6:
            self.pontuation = 1200

        return self.pontuation

    def update_pontuations(self):
        if not self.paused:
            player1_pontuation_treated = 'Total: ' + str(self.player1_pontuation) + '/' + str(self.win_pontuation)
            player1_pontuation.set(player1_pontuation_treated)

            player2_pontuation_treated = 'Total: ' + str(self.player2_pontuation) + '/' + str(self.win_pontuation)
            player2_pontuation.set(player2_pontuation_treated)

            player1_turn_pontuation_treated = 'Turno: ' + str(self.player1_turn_pontuation)
            player1_turn_pontuation.set(player1_turn_pontuation_treated)

            player2_turn_pontuation_treated = 'Turno: ' + str(self.player2_turn_pontuation)
            player2_turn_pontuation.set(player2_turn_pontuation_treated)

            player1_selected_pontuation_treated = 'Selecionado: ' + str(self.player1_selected_pontuation)
            player1_selected_pontuation.set(player1_selected_pontuation_treated)

            player2_selected_pontuation_treated = 'Selecionado: ' + str(self.player2_selected_pontuation)
            player2_selected_pontuation.set(player2_selected_pontuation_treated)

            window.after(2000, self.winning)
    
    def bust(self):
        global dice
        self.bust_bool = False
        bust_dice_numbers = []
        for y in dice:
            if y.button_appearing == True:
                bust_dice_numbers.append(y.number)

        one_times = bust_dice_numbers.count(1)
        two_times = bust_dice_numbers.count(2)
        three_times = bust_dice_numbers.count(3)
        four_times = bust_dice_numbers.count(4)
        five_times = bust_dice_numbers.count(5)
        six_times = bust_dice_numbers.count(6)

        if one_times < 1 and two_times < 3 and three_times < 3 and four_times < 3 and five_times < 1 and six_times < 3:
            self.bust_bool = True
        if one_times == 1 and two_times == 1 and three_times == 1 and four_times == 1 and five_times == 1 and six_times == 1:
            self.bust_bool = False
        
        if self.bust_bool:
            self.bust_counter += 1
            if self.actual_player == 1:
                self.player1_bust_counter += 1
            elif self.actual_player == 2:
                self.player2_bust_counter += 1
            window.after(400)
            bust_label.place(x=485, y=240)
            bust_sound.play()
            window.after(2500, bust_label.place_forget)
            window.after(2550, game.end_turn)
            self.player1_turn_pontuation = 0
            self.player2_turn_pontuation = 0
            self.update_pontuations()

    def end_turn(self, e=None):
        if not self.paused:
            global buttons_appearing

            self.bigger_than_0 = False

            if self.actual_player == 1 and self.player1_selected_pontuation > 0:
                self.player1_turn_pontuation += self.player1_selected_pontuation
                self.player1_selected_pontuation = 0
                self.player1_pontuation += self.player1_turn_pontuation
                self.player1_turn_pontuation = 0
                self.bigger_than_0 = True
                
            elif self.actual_player == 2 and self.player2_selected_pontuation > 0:
                self.player2_turn_pontuation += self.player2_selected_pontuation
                self.player2_selected_pontuation = 0
                self.player2_pontuation += self.player2_turn_pontuation
                self.player2_turn_pontuation = 0
                self.bigger_than_0 = True
            
            if self.bigger_than_0 or self.bust_bool or self.countdown_zero:
                self.bigger_than_0 = False
                self.bust_bool = False
                self.countdown_zero = False
                self.reset_countdown()    
                self.update_pontuations()
                buttons_appearing = 0
                self.add_buttons()
                dice_numbers.clear()
                self.switch_player()
                self.unselect_and_roll_dice()
                self.bust()
            
    def decrease_countdown(self):
        if not self.paused:
            countdown.set(countdown.get() - 1)
            if countdown.get() < 0:
                self.countdown_zero = True
                self.end_turn()
                countdown.set(15)
            countdown_text.set(str(countdown.get()))
            if countdown.get() < 10:
                countdown_text.set('0' + countdown_text.get())
            window.after(1000, self.decrease_countdown)
    
    def reset_countdown(self):
        countdown.set(16)
    
    def remove_buttons(self):
        global dice_buttons 
        global dice
        global buttons_appearing
        for x in range(6):
            if dice[x].selected == True:
                dice[x].button_appearing = False
                buttons_appearing -= 1
            dice_buttons[x].place_forget()

    def add_buttons(self):
        global dice
        global dice_buttons
        dice_buttons = [die1_button, die2_button, die3_button, die4_button, die5_button, die6_button]
        global buttons_appearing
        dice = [die1, die2, die3, die4, die5, die6]
        dice_buttons_x_plus = 0
        
        if buttons_appearing <= 0 :
            buttons_appearing = 6
            for x in dice:
                x.button_appearing = True

        if buttons_appearing == 1:
            dice_buttons_x = 510
            dice1_sound.play()
        
        elif buttons_appearing == 2:
            dice_buttons_x = 440
            dice2_sound.play()

        elif buttons_appearing == 3:
            dice_buttons_x = 370
            dice3_sound.play()
        
        elif buttons_appearing == 4:
            dice_buttons_x = 300
            dice4_sound.play()
        
        elif buttons_appearing == 5:
            dice_buttons_x = 230
            dice_sound.play()
           
        elif buttons_appearing == 6:
            dice_buttons_x = 160
            dice_sound.play()

        window.after(700)

        for x in range(6):  
            if dice[x].button_appearing == True:
                dice_buttons[x].place(x=dice_buttons_x +dice_buttons_x_plus, y= dice_buttons_y)
                dice_buttons_x_plus += 140

    def count_time(self):
        if not game.paused:
            self.game_time += 1
            if self.actual_player == 1:
                self.player1_time += 1
            elif self.actual_player == 2:
                self.player2_time += 1

            window.after(1000, game.count_time)
    
    def winning(self):
        if self.player1_pontuation >= win_pontuation.get():
            winner.set('O vencedor é o Jogador 1')
            self.win = True
            loser_pontuation.set(str(self.player2_pontuation) + '/' + str(win_pontuation.get()))

        elif self.player2_pontuation >= win_pontuation.get():
            winner.set('O vencedor é o Jogador 2')
            self.win = True
            loser_pontuation.set(str(self.player1_pontuation) + '/' + str(win_pontuation.get()))
            
        if self.win:
            turn_count.set(str(self.turn_count))
            game_time.set(str(datetime.timedelta(seconds=self.game_time)))
            player1_time.set(str(datetime.timedelta(seconds=self.player1_time)))
            player2_time.set(str(datetime.timedelta(seconds=self.player2_time)))
            bust_times.set(str(self.bust_counter))
            player1_bust_times.set(str(self.player1_bust_counter))
            player2_bust_times.set(str(self.player2_bust_counter))
            self.pause_game()
            raise_frame('4')

    def restart_game(self):
        game.reset_countdown()
        raise_frame('1')
        paused_label.place_forget()
        game.__init__()

    def pause_game(self, e=None):
        if self.paused == False and self.unlocked_pause:
            self.paused = True
            self.unlocked_pause = False
            paused_label.place(x=340, y=200)
            window.after(1500, game.unlock_pause)

        elif self.paused == True and self.unlocked_pause:
            self.paused = False
            game.unlocked_pause = False
            paused_label.place_forget()
            window.after(1050, game.decrease_countdown)
            window.after(1500, game.unlock_pause)

    def unlock_pause(self):
        self.unlocked_pause = True


#OTher functions  
def raise_frame(frame):
    global actual_frame
    actual_frame = frame
    frames[frame].tkraise()
    
def instructions_raise_return():
    global last_frame
    global first_time
    if first_time:
        raise_frame('1')
        first_time = False
        welcome_label.place_forget()
        rules_label.configure(font='Times 11 bold')
        rules_label.place(x=140, y=40)
    elif actual_frame in ('1', '2', '3', '4', 'wait'):
        last_frame = actual_frame
        raise_frame('0')
    elif actual_frame == '0':
        raise_frame(last_frame)
    
def skip_to_win_frame():
    game.win_pontuation = 3000
    game.player1_pontuation = 4000
    game.update_pontuations()
    game.pause_game()

def enable_disable_password():
    if password_active.get():
        password.configure(state=NORMAL)
    else:
        password.configure(state=DISABLED)
        password_value.set('')

def room_name_treatement(room_name):
    name = room_name.get()
    alphanumeric = ''
    for character in name:
        if character.isalnum():
            alphanumeric += character
    name = alphanumeric.title()
    room_name.set(name[:10])

def password_treatement(password_value):
    p = password_value.get()
    alphanumeric = ''
    for character in p:
        if character.isalnum():
            alphanumeric += character
    password_value.set(alphanumeric[:8])

def waiting_player():
    texts = ('Esperando pelo segundo jogador.  ', 'Esperando pelo segundo jogador.. ', 'Esperando pelo segundo jogador...')
    index = texts.index(waiting_player_text.get()) + 1
    if index > 2:
        index = 0
    waiting_player_text.set(texts[index])
    window.after(1000, waiting_player)

def servers_list_update():
    servers_list.delete(ALL)
    for server in servers.find():
        servers_list.insert(END, server['room_name'], server['win_pontuation'], server['first_player'], server['password_active'])

def create_server():
    if room_name.get() != '':
        name_exist = False
        results = servers.find({"room_name": room_name.get()}) 
        for result in results:
            name_exist = result['room_name']
        if name_exist == False:
            raise_frame('wait')
            waiting_player()
            if first_player.get() == 1:
                first_player_treated = 'Jogador 1'
            elif first_player.get() == 2:
                first_player_treated = 'Jogador 2'
            elif first_player.get() == 3:
                first_player_treated = 'Aleatório'
            
            if password_active.get():
                password_active_treated = 'Sim'
            else:
                password_active_treated = 'Não'

            new_server = {"ip": IP,
            "room_name": room_name.get(),
            "password_active": password_active_treated,
            "password": password_value.get(),
            "win_pontuation": win_pontuation.get(),
            "first_player": first_player_treated}
            servers.insert_one(new_server)
            
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((IP, 5555)) 
            s.listen(2)
            while True:
             conn, addr = s.accept()
             game.start_game()

        else:
            messagebox.showerror(title='Não criada!', message='Já existe uma sala com esse nome.')
    else:
        messagebox.showerror(title='Não criada!', message='Não é possível criar uma sala sem nome')

def connect_to_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    selected_server = servers_list.get(servers_list.index(ACTIVE))
    selected_server_name = selected_server[0][0]
    server = servers.find_one({'room_name': selected_server_name})
    selected_server_ip = server['ip']
    
    s.connect((selected_server_ip, 5555))
    

#Window Configuration
window = Tk()
window.title("Farkle")
window.resizable(0, 0)
window.wm_iconbitmap(directory + r'images\logo.ico')

w = 1100
h = 900

ws = window.winfo_screenwidth() # width of the screen
hs = window.winfo_screenheight() # height of the screen

# calculate x and y coordinates for the Tk root window
x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

# set the dimensions of the screen 
# and where it is placed
window.geometry('%dx%d+%d+%d' % (w, h, x, y))


#Images creation
background = PhotoImage(file = directory + r'images\darkwood_background.png')

die1_image2 = ImageTk.PhotoImage(Image.open(directory + r'images\die1.png'))
die2_image2 = ImageTk.PhotoImage(Image.open(directory + r'images\die2.png'))
die3_image2 = ImageTk.PhotoImage(Image.open(directory + r'images\die3.png'))
die4_image2 = ImageTk.PhotoImage(Image.open(directory + r'images\die4.png'))
die5_image2 = ImageTk.PhotoImage(Image.open(directory + r'images\die5.png'))
die6_image2 = ImageTk.PhotoImage(Image.open(directory + r'images\die6.png'))

skip_image = PhotoImage(file = directory + r'images\skip.png')
pause_image = PhotoImage(file = directory + r'images\pause.png')
play_image = PhotoImage(file = directory + r'images\play.png')
info_image = PhotoImage(file = directory + r'images\info.png')
refresh_image = PhotoImage(file = directory + r'images\refresh.png')

bust_image = PhotoImage(file= directory + r'images\Bust.png')
paused_game_image = PhotoImage(file= directory + r'images\paused.png')

#Sounds creation
bust_sound = pygame.mixer.Sound(file= directory + r'soundtrack\sound_effects\bust_sound.wav')
dice1_sound = pygame.mixer.Sound(file= directory + r'soundtrack\sound_effects\1_dice_sound.wav')
dice2_sound = pygame.mixer.Sound(file= directory + r'soundtrack\sound_effects\2_dice_sound.wav')
dice3_sound = pygame.mixer.Sound(file= directory + r'soundtrack\sound_effects\3_dice_sound.wav')
dice4_sound = pygame.mixer.Sound(file= directory + r'soundtrack\sound_effects\4_dice_sound.wav')
dice_sound = pygame.mixer.Sound(file= directory + r'soundtrack\sound_effects\6_dice_sound.wav')
select_sound = pygame.mixer.Sound(file= directory + r'soundtrack\sound_effects\select_sound.wav')

#Frames creation
frames_names = ('0', '1', '2', '3', '4', 'wait')
frames = {}
for index, frame in enumerate(frames_names):
    frame = frames_names[index]
    frames[frame] = Frame(window, width=1100, height=900)
    frames[frame].grid(row=0, column=0, sticky='news')
    Label(frames[frame], image=background).place(x=0, y=0)

raise_frame('0')

#Variables
first_player, win_pontuation, countdown, countdown_text, actual_player = IntVar(window, 1), IntVar(window, 4000), IntVar(window, 15), StringVar(window, '15'), StringVar(window)
player1_pontuation, player2_pontuation, player1_turn_pontuation, player2_turn_pontuation, player1_selected_pontuation, player2_selected_pontuation = StringVar(window), StringVar(window), StringVar(window), StringVar(window), StringVar(window), StringVar(window)
winner, game_time, player1_time, player2_time, loser_pontuation, bust_times, player1_bust_times, player2_bust_times, turn_count  = StringVar(window), StringVar(window), StringVar(window), StringVar(window), StringVar(window), StringVar(window), StringVar(window), StringVar(window), StringVar(window)
room_name, password_active, password_value, waiting_player_text = StringVar(window), BooleanVar(window, False), StringVar(window), StringVar(window, 'Esperando pelo segundo jogador...')

first_time = True

game_rules = '''Regras do jogo:\n
Farkle é jogado por dois jogadores, com cada jogador em sucessão tendo um turno em que joga os dados.\nPor sua vez a rolagem resulta em uma pontuação para cada jogador, que se acumulam até uma pontuação de vitória.\n
No início de cada turno, o jogador joga todos os seis dados ao mesmo tempo.\n
Depois de cada lance, um ou mais dados de pontuação devem ser retirados (ver regras de pontuação abaixo).\n
O jogador pode, então, terminar o seu turno e guardar a pontuação acumulada até agora,\nou continuar a jogar os dados restantes (aqueles que não foram retirados).\n
Se o jogador retirou todos os seis dados, ele pode continuar a sua vez com um novo lance de todos os seis dados,\n aumentando a pontuação que ele já acumulou. Não há limite para o número de vezes que um jogador pode rolar em um turno.\n
Se nenhum dos dados valer pontos em algum lance, o jogador teve um "Bust!" e todos\nos pontos que ele havia acumulado no turno são perdidos, os pontos dos turnos anteriores permancem sem alteração.\n
No final do turno do jogador, os dados são passados para o próximo jogador, e ele tem sua vez.\n
Uma vez que um jogador alcançou ou ultrapassou a pontuação de vitória, ele vence.\n\n
Pontuação:\n\ncada 1 - 100\n\ncada 5 - 50\n\nTrês 1s - 1000 e + 1000 a cada 1 adicional\n\nTrês 2s - 200 e + 200 a cada 2 adicional\n\nTrês 3s - 300 e + 300 a cada 3 adicional\n
Três 4s - 400 e + 400 a cada 4 adicional\n\nTrês 5s - 500 e + 500 a cada 5 adicional\n\nTrês 6s - 600 e + 600 a cada 6 adicional\n\nSequência de 1 à 6 - 1200\n'''

#Instance Creating
die1 = Die(1)
die2 = Die(2)
die3 = Die(3)
die4 = Die(4)
die5 = Die(5)
die6 = Die(6)
game = Game()

players_music = Music(0)

#Interface Parameters
titles_background_color = 'saddle brown'
titles_text_color = 'gold2'
titles_font = 'Times 36 bold'

radio_buttons_font = 'Times 20 bold'
radio_buttons_width = 20
radio_buttons_height = 2
radio_buttons_background = "saddle brown"
radio_buttons_bg_selected = "burlywood3"
radio_buttons_fg = "white"

dice_buttons_y = 370
dice_buttons_x = 160

labels_text_color = 'gold2'
labels_border_color = 'gold2'
labes_background_color = 'red4'

win_frame_labels_x = 540
win_frame_labels_width = 20
win_frame_titles_x = 240



#Frame 0 - Instructions
welcome_label = Label(frames['0'], text='Seja bem-vindo à Farkle!', bg=labes_background_color, fg=labels_text_color, font=titles_font, width=38)
welcome_label.place(x=3, y=3)

rules_label = Label(frames['0'], text= game_rules, bg=labes_background_color, fg=labels_text_color, font='Times 11 bold')
rules_label.place(x=140, y=80)

Button(frames['0'], width=10, height=2, font='Times 16 bold', text="Entendido!", fg='black', bg='gold2', command=instructions_raise_return).place(x=490, y=825)

pause_play_button0 = Button(frames['0'], bg='white', image=pause_image, command=players_music.pause_play_music)
pause_play_button0.place(x=1040, y=870)


#Frame 1 - Servers List
Label(frames['1'], text='Salas:', bg=labes_background_color, fg=labels_text_color, font='Times 40 bold', width=35).place(x=3, y=3)

servers_list = MultiListbox(frames['1'], width=900, height=600, bg=labes_background_color, fg='white', font='Times 35 bold', columns=('Nome da sala', 'Pontuação de vitória', 'Primeiro jogador', 'Senha ativa?'),
selectmode='extended', selectbackground='red2', selectforeground='white')
servers_list.place(x=100, y=100)
servers_list_update()


Button(frames['1'], width=10, height=2, font='Times 16 bold', text="Criar Partida", fg='black', bg='gold2', command=lambda: raise_frame('2')).place(x=400, y=825)
Button(frames['1'], width=10, height=2, font='Times 16 bold', text="Entrar", fg='black', bg='gold2', command=connect_to_server).place(x=550, y=825)
Button(frames['1'], image=refresh_image, command=servers_list_update).place(x=1020, y=100)

pause_play_button1 = Button(frames['1'], bg='white', image=pause_image, command=players_music.pause_play_music)
pause_play_button1.place(x=1040, y=870)


#Frame 2 - Create server
Label(frames['2'], text='Nome da sala:', bg=titles_background_color, fg=titles_text_color, font='Times 25 bold').place(x=350, y=10)
Entry(frames['2'], textvariable=room_name, font='Times 25', width=13).place(x=600, y=13)

Label(frames['2'], text='Senha:', bg=titles_background_color, fg=titles_text_color, font='Times 25 bold').place(x=452, y=70)
password = Entry(frames['2'], textvariable=password_value, font='Times 25', width=13, state=DISABLED, disabledbackground='gray47')
password.place(x=600, y=70)

room_name.trace("w", lambda *args: room_name_treatement(room_name))
password_value.trace("w", lambda *args: password_treatement(password_value))

Checkbutton(frames['2'], text="Senha?", variable=password_active, command=enable_disable_password).place(x=760, y=120)

Label(frames['2'], text='Quem começa?', bg=titles_background_color, fg=titles_text_color, font=titles_font, width=38).place(x=0, y=150)
Label(frames['2'], text='Quantos pontos para vencer?', bg=titles_background_color, fg=titles_text_color, font=titles_font, width=38).place(x=0, y=500)

Radiobutton(frames['2'], width=radio_buttons_width, height=radio_buttons_height, fg=radio_buttons_fg, text="Jogador 1", font=radio_buttons_font, variable =first_player, value=1, indicator=0, background=radio_buttons_background, selectcolor=radio_buttons_bg_selected, command=select_sound.play).place(x=390, y=220)
Radiobutton(frames['2'], width=radio_buttons_width, height=radio_buttons_height, fg=radio_buttons_fg, text="Jogador 2", font=radio_buttons_font, variable =first_player, value=2, indicator=0, background=radio_buttons_background, selectcolor=radio_buttons_bg_selected, command=select_sound.play).place(x=390, y=300)
Radiobutton(frames['2'], width=radio_buttons_width, height=radio_buttons_height, fg=radio_buttons_fg, text="Aleatório", font=radio_buttons_font, variable =first_player, value=3, indicator=0, background=radio_buttons_background, selectcolor=radio_buttons_bg_selected, command=select_sound.play).place(x=390, y=380) 

Radiobutton(frames['2'], width=radio_buttons_width, height=radio_buttons_height, fg=radio_buttons_fg, text="2000", font=radio_buttons_font, variable=win_pontuation, value=2000, indicator=0, background=radio_buttons_background, selectcolor=radio_buttons_bg_selected, command=select_sound.play).place(x=390, y=570)
Radiobutton(frames['2'], width=radio_buttons_width, height=radio_buttons_height, fg=radio_buttons_fg, text="3000", font=radio_buttons_font, variable=win_pontuation, value=3000, indicator=0, background=radio_buttons_background, selectcolor=radio_buttons_bg_selected, command=select_sound.play).place(x=390, y=650)
Radiobutton(frames['2'], width=radio_buttons_width, height=radio_buttons_height, fg=radio_buttons_fg, text="4000", font=radio_buttons_font, variable=win_pontuation, value=4000, indicator=0, background=radio_buttons_background, selectcolor=radio_buttons_bg_selected, command=select_sound.play).place(x=390, y=730) 

Button(frames['2'], width=15, height=2, font='Times 16 bold', text="Criar sala", fg='black', bg='gold2', command=create_server).place(x=460, y=830)

pause_play_button2 = Button(frames['2'], bg='white', image=pause_image, command=players_music.pause_play_music)
pause_play_button2.place(x=1040, y=870)

#Awaiting for second player
Label(frames['wait'], textvariable=waiting_player_text, bg=labes_background_color, fg=labels_text_color, font='Times 40 bold').place(x=170, y=360)

pause_play_button_wait = Button(frames['wait'], bg='white', image=pause_image, command=players_music.pause_play_music)
pause_play_button_wait.place(x=1040, y=870)


#Frame 3 - Game
Label(frames['3'], width=85, height = 7, bg=labels_border_color, font='Times 5 bold').place(x=2, y=2)
Label(frames['3'], textvariable=actual_player, bg=labes_background_color, fg=labels_text_color, font='Times 30 bold', anchor=W).place(x=7, y=7)

Label(frames['3'], width=30, height = 17, bg=labels_border_color, font='Times 5 bold').place(x=506, y=2)
Label(frames['3'], textvariable=countdown_text, bg=labes_background_color, fg=labels_text_color, font='Times 80 bold', anchor=E).place(x=512, y=10)

Label(frames['3'], width=47, height = 12, bg=labels_border_color, font='Times 5 bold').place(x=2, y=812)
Label(frames['3'], textvariable=player1_selected_pontuation, width=15, bg=labes_background_color, fg=labels_text_color, font='Times 15 bold', anchor=W).place(x=5, y=817)
Label(frames['3'], textvariable=player1_turn_pontuation, width=15, bg=labes_background_color, fg=labels_text_color, font='Times 15 bold', anchor=W).place(x=5, y=842)
Label(frames['3'], textvariable=player1_pontuation, width=15, bg=labes_background_color, fg=labels_text_color, font='Times 15 bold', anchor=W).place(x=5, y=867)

Label(frames['3'], width= 50, height = 10, bg=labels_border_color, font='Times 5 bold').place(x=905, y=2)
Label(frames['3'], textvariable=player2_selected_pontuation, width=15, bg=labes_background_color, fg=labels_text_color, font='Times 15 bold', anchor=W).place(x=910, y=5)
Label(frames['3'], textvariable=player2_turn_pontuation, width=15, bg=labes_background_color, fg=labels_text_color, font='Times 15 bold', anchor=W).place(x=910, y=30)
Label(frames['3'], textvariable=player2_pontuation, width=15, bg=labes_background_color, fg=labels_text_color, font='Times 15 bold', anchor=W).place(x=910, y=55)

bust_label = Label(frames['3'], bg='red4', image=bust_image)
paused_label = Label(frames['3'], bg='red4', image=paused_game_image)

Button(frames['3'], width=15, height=2, font='Times 16 bold', text="Re-rolar [F]", fg='black', bg='gold2', command=game.roll_dice).place(x=560, y=800)
Button(frames['3'], width=15, height=2, font='Times 16 bold', text="Finalizar turno [Q]", fg='black', bg='gold2', command=game.end_turn).place(x=360, y=800)

die1_button = Button(frames['3'], image=die1.image, borderwidth=0, highlightthickness=0, highlightbackground="red", highlightcolor= "red", command=die1.select_die)
die2_button = Button(frames['3'], image=die2.image, borderwidth=0, command=die2.select_die)
die3_button = Button(frames['3'], image=die3.image, borderwidth=0, command=die3.select_die)
die4_button = Button(frames['3'], image=die4.image, borderwidth=0, command=die4.select_die)
die5_button = Button(frames['3'], image=die5.image, borderwidth=0, command=die5.select_die)
die6_button = Button(frames['3'], image=die6.image, borderwidth=0, command=die6.select_die)

pause_play_button3 = Button(frames['3'], bg='white', image=pause_image, command=players_music.pause_play_music)
pause_play_button3.place(x=1040, y=870)



#Frame 4 - Win
Label(frames['4'], textvariable=winner, bg=labes_background_color, fg=labels_text_color, font='Times 60 bold', width=24).place(x=3, y=20)

Label(frames['4'], text='Quantidade de turnos:', bg=labes_background_color, fg=labels_text_color, font='Times 20 bold', width=win_frame_labels_width, anchor=W).place(x=win_frame_titles_x, y=170)
Label(frames['4'], textvariable=turn_count, bg=labes_background_color, fg=labels_text_color, font='Times 20 bold', width=win_frame_labels_width, anchor=E).place(x=win_frame_labels_x, y=170)

Label(frames['4'], text='Tempo de jogo:', bg=labes_background_color, fg=labels_text_color, font='Times 20 bold', width=win_frame_labels_width, anchor=W).place(x=win_frame_titles_x, y=250)
Label(frames['4'], textvariable=game_time, bg=labes_background_color, fg=labels_text_color, font='Times 20 bold', width=win_frame_labels_width, anchor=E).place(x=win_frame_labels_x, y=250)

Label(frames['4'], text='Tempo do jogador 1:', bg=labes_background_color, fg=labels_text_color, font='Times 20 bold', width=win_frame_labels_width, anchor=W).place(x=win_frame_titles_x, y=300)
Label(frames['4'], textvariable=player1_time, bg=labes_background_color, fg=labels_text_color, font='Times 20 bold', width=win_frame_labels_width, anchor=E).place(x=win_frame_labels_x, y=300)

Label(frames['4'], text='Tempo do jogador 2:', bg=labes_background_color, fg=labels_text_color, font='Times 20 bold', width=win_frame_labels_width, anchor=W).place(x=win_frame_titles_x, y=350)
Label(frames['4'], textvariable=player2_time, bg=labes_background_color, fg=labels_text_color, font='Times 20 bold', width=win_frame_labels_width, anchor=E).place(x=win_frame_labels_x, y=350)

Label(frames['4'], text='Pontuação do perdedor:', bg=labes_background_color, fg=labels_text_color, font='Times 20 bold', width=win_frame_labels_width, anchor=W).place(x=win_frame_titles_x, y=430)
Label(frames['4'], textvariable=loser_pontuation, bg=labes_background_color, fg=labels_text_color, font='Times 20 bold', width=win_frame_labels_width, anchor=E).place(x=win_frame_labels_x, y=430)

Label(frames['4'], text='Quantidade de Busts:', bg=labes_background_color, fg=labels_text_color, font='Times 20 bold', width=win_frame_labels_width, anchor=W).place(x=win_frame_titles_x, y=510)
Label(frames['4'], textvariable=bust_times, bg=labes_background_color, fg=labels_text_color, font='Times 20 bold', width=win_frame_labels_width, anchor=E).place(x=win_frame_labels_x, y=510)

Label(frames['4'], text='Busts do Jogador 1:', bg=labes_background_color, fg=labels_text_color, font='Times 20 bold', width=win_frame_labels_width, anchor=W).place(x=win_frame_titles_x, y=560)
Label(frames['4'], textvariable=player1_bust_times, bg=labes_background_color, fg=labels_text_color, font='Times 20 bold', width=win_frame_labels_width, anchor=E).place(x=win_frame_labels_x, y=560)

Label(frames['4'], text='Busts do Jogador 2:', bg=labes_background_color, fg=labels_text_color, font='Times 20 bold', width=win_frame_labels_width, anchor=W).place(x=win_frame_titles_x, y=610)
Label(frames['4'], textvariable=player2_bust_times, bg=labes_background_color, fg=labels_text_color, font='Times 20 bold', width=win_frame_labels_width, anchor=E).place(x=win_frame_labels_x, y=610)

Button(frames['4'], width=20, height=2, font='Times 16 bold', text="Voltar ao inicio", fg='black', bg='gold2', command=game.restart_game).place(x=430, y=800)

pause_play_button4 = Button(frames['4'], bg='white', image=pause_image, command=players_music.pause_play_music)
pause_play_button4.place(x=1040, y=870)



for frame in frames:
    Button(frames[frame], width=20, height=20, bg='white', image=skip_image, command=players_music.skip_music).place(x=1070, y=870)
    if frame not in ('0', '4'):
        Button(frames[frame], bg='white', image=info_image, command=instructions_raise_return).place(x=1010, y=870)

#Keybindings
keybindings = {'<q>': game.end_turn, '<f>': game.roll_dice, '<Escape>': game.pause_game, '<p>': game.pause_game}
for key in keybindings:
    window.bind(key, keybindings[key])

window.mainloop()


        
        
       