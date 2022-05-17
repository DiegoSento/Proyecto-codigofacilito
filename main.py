"""
El core del juego es tomado de https://github.com/y330/Pydash, la funcionabilidad, el modo de juego, los mapas, los controles
por medio del procesado de imagenes es propiedad de los autores citados el inicio
"""

#IMPORTE DE LIBRERIAS
import csv
import os
import random
import cv2
import copy
import math
import pygame
from pygame.math import Vector2
from pygame.draw import rect
import scipy.io as sio
import numpy as np
import cv2
from pdi import *



pygame.init()                                                                   # Inicializar modulo Pygame
screen = pygame.display.set_mode([800, 600])                                    # Formato ventana juego (Dimensiones)
done = False                                                                    # Bandera para el Loop principal
start = False                                                                   # bandera para el ciclo principal
clock = pygame.time.Clock()                                                     # selección de reloj    




"""lambda functions are anonymous functions that you can assign to a variable.
e.g.
1. x = lambda x: x + 2  # takes a parameter x and adds 2 to it
2. print(x(4))
>>6
"""
color = lambda: tuple([random.randint(0, 255) for i in range(3)])  # lambda function for random color, not a constant.



""" Clases del Juego y sus respectivos constructores"""

class Player(pygame.sprite.Sprite):
    """Class for player. Holds update method, win and die variables, collisions and more."""
    win: bool
    died: bool

    def __init__(self, image, platforms, pos, *groups):
        """
        :param image: block face avatar
        :param platforms: obstacles such as coins, blocks, spikes, and orbs
        :param pos: starting position
        :param groups: takes any number of sprite groups.
        """
        super().__init__(*groups)
        self.onGround = False  # player on ground?
        self.platforms = platforms  # obstacles but create a class variable for it
        self.died = False  # player died?
        self.win = False  # player beat level?

        self.image = pygame.transform.smoothscale(image, (32, 32))
        self.rect =self.image.get_rect(center=pos)  # get rect gets a Rect object from the image
        
        self.particles = []  # player trail
      
        
        self.vel = Vector2(0, 0)  # velocity starts at zero

    def draw_particle_trail(self, x, y, color):
        
        """draws a trail of particle-rects in a line at random positions behind the player"""
        
        self.particles.append([[x - 5, y - 8], [random.randint(0, 25) / 10 - 1, random.choice([0, 0])],
                  random.randint(5, 8)])
        

        for particle in self.particles:
            particle[0][0] += particle[1][0]
            particle[0][1] += particle[1][1]
            particle[2] -= 0.5
            particle[1][0] -= 0.4
            rect(alpha_surf, color,
                  ([int(particle[0][0]), int(particle[0][1])], [int(particle[2]) for i in range(2)]))
            if particle[2] <= 0:
                self.particles.remove(particle)

    def collide(self, yvel, platforms):
        global coins

        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                """pygame sprite builtin collision method,
                sees if player is colliding with any obstacles"""
                                   

                if isinstance(p, End):
                    self.win = True
                    
                if(attempts < 10):                                              #despues de 10 intentos, las picas no colisionan                
                    if isinstance(p, Spike):
                        self.died = True                                        #Muere al colisioanr con una pica
                    
                    
                if isinstance(p, Coin):
                    
                    coins += 1                                                  #Contador de monedas colisonadas

                    # Borar Monedas
                    p.rect.x = 100                                              #coordenadas del contador de monedas
                    p.rect.y = 570                                              #Coordenadas del contador de monedas

                if isinstance(p, Platform):  

                    if yvel > 0:
                        """if player is going down(yvel is +)"""
                        self.rect.bottom = p.rect.top                           # Evita que el avatr pase el piso
                        self.vel.y = 0  # rest y velocity because player is on ground

                      
                    elif yvel < 0:
                        """if yvel is (-),player collided while jumping"""
                        self.rect.top = p.rect.bottom  # player top is set the bottom of block like it hits it head
                    else:
                        """otherwise, if player collides with a block, he/she dies."""
                        self.vel.x = 0
                        self.rect.right = p.rect.left                           #Evita que avatar atarviese los muros
                        self.died = True                                        #Muere al colisonar con un bloque

    

    def update(self):
        

            # max falling speed
        if self.vel.y > 100: self.vel.y = 100

        # do x-axis collisions
        self.collide(0, self.platforms)

        """Control de la posicion del avatr"""
        self.rect.centery = Y                                                   #ASIGNA LA POS de Y desde el calculo de momneto en imagenes
        #self.rect.centerx = X                                                  #ASIGNA LA POS de X desde el calculo de momneto en imagenes --En caso de querer controlar en 2D
        
    

        # assuming player in the air, and if not it will be set to inversed after collide
        self.onGround = False

        # do y-axis collisions
        self.collide(self.vel.y, self.platforms)

        # check if we won or if player won
        eval_outcome(self.win, self.died)


"""
Obstacle classes
"""


# Parent class
class Draw(pygame.sprite.Sprite):
    """parent class to all obstacle classes; Sprite class"""

    def __init__(self, image, pos, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect(topleft=pos)


#  ====================================================================================================================#
#  classes of all obstacles. this may seem repetitive but it is useful(to my knowledge)
#  ====================================================================================================================#
# children
class Platform(Draw):
    """block"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Spike(Draw):
    """spike"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Coin(Draw):
    """coin. get 6 and you win the game"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Orb(Draw):
    """orb. click space or up arrow while on it to jump in midair"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class Trick(Draw):
    """block, but its a trick because you can go through it"""

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)


class End(Draw):
    "place this at the end of the level"

    def __init__(self, image, pos, *groups):
        super().__init__(image, pos, *groups)

"""
Functions
"""


def init_level(map):
    """this is similar to 2d lists. it goes through a list of lists, and creates instances of certain obstacles
    depending on the item in the list"""
    x = 0
    y = 0

    for row in map:
        for col in row:

            if col == "0":
                Platform(block, (x, y), elements)

            if col == "Coin":
                Coin(coin, (x, y), elements)

            if col == "Spike":
                Spike(spike, (x, y), elements)
            if col == "Orb":
                orbs.append([x, y])

                Orb(orb, (x, y), elements)

            if col == "T":
                Trick(trick, (x, y), elements)

            if col == "End":
                End(orb, (x, y), elements)
            x += 32
        y += 32
        x = 0


def won_screen():
    """show this screen when beating a level"""
    global attempts, coins, level, fill
    attempts = 0
    coins    = 0
    fill     = 0
    player_sprite.clear(player.image, screen)
    screen.fill(pygame.Color("white"))
    txt_win1 = txt_win2 = "Nothing"
   
    txt_win = f"Lo Lograste! "
    txt1=  f" Esc   --> Salir "
    txt2 = f" SPACE --> Seguir Jugando Modo Pro"
    

    won_game = font.render(txt_win, True, BLUE)
    esc = font.render(txt1 , True, BLUE)
    space = font.render(txt2, True, BLUE)

    screen.blit(won_game, (100, 300))
    screen.blit(esc, (100, 350))
    screen.blit(space, (100, 400))
    wait_for_key()
    reset()


def death_screen():
    """show this screenon death"""
    global attempts, fill
    fill = 0
    player_sprite.clear(player.image, screen)
    attempts = attempts + 1
    game_over = font.render("Perdiste -> Presione SPACIO para reintentar ",
                            True, WHITE)

    screen.fill(pygame.Color("sienna1"))
    screen.blits([[game_over, (100, 100)], [tip, (100, 400)]])

    wait_for_key()
    reset()


def eval_outcome(won: bool, died: bool):
    """simple function to run the win or die screen after checking won or died"""
    if won:
        won_screen()
    if died:
        death_screen()


def block_map(level_num):
    """
    :type level_num: rect(screen, BLACK, (0, 0, 32, 32))
    open a csv file that contains the right level map
    """
    lvl = []
    with open(level_num, newline='') as csvfile:
        trash = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in trash:
            lvl.append(row)
    return lvl


def start_screen():
    """main menu. option to switch level, and controls guide, and game overview."""
    global level
    bg1 = pygame.image.load(os.path.join("images", "bg1.png"))

    if not start:
        screen.blit(bg1, (0,0))
        if pygame.key.get_pressed()[pygame.K_1]:
            level = 0
        level_memo = font.render(f"SPACE para iniciar.", True, (255, 255, 0))
        screen.blit(level_memo, (300, 450))


def reset():
    """resets the sprite groups, music, etc. for death and new level"""
    global player, elements, player_sprite, level

    
    pygame.mixer.music.load(os.path.join("music", "castle-town.mp3"))
    pygame.mixer_music.play()
    player_sprite = pygame.sprite.Group()
    elements = pygame.sprite.Group()
    player = Player(avatar, elements, (150, 150), player_sprite)
    init_level(block_map(level_num=levels[level]))
    speed = 1                                                                   #Renicia la velocidad
    coins = 0                                                                   #Reincia el nuemro de monedas    
    fill = 0                                                                    # Reinicia la  barra de progreso  


def move_map():
    """moves obstacles along the screen"""
    for sprite in elements:
        sprite.rect.x -= CameraX
        


def draw_stats(surf, money=0):
    """
    draws progress bar for level, number of attempts, displays coins collected, and progressively changes progress bar
    colors
    """
    global fill
    progress_colors = [pygame.Color("red"), pygame.Color("orange"),
                       pygame.Color("yellow"), pygame.Color("lightgreen"),
                       pygame.Color("green")]

    tries = font.render(f" Intentos: {attempts} " , True, WHITE)               #Numero de intentos
    sspeed= font.render(f"vel:{speed:.2f} ", True, WHITE)                      #Velocidad, 2 cifras decimales
    scoins = font.render(f"Monedas:{coins}", True, WHITE)                      #Cantidad demonedas recogidas  
    BAR_LENGTH = 600                                                           #Longitud de la barra de progreso
    BAR_HEIGHT = 10                                                            #Ancho de la barra de progreso
    for i in range(1, money):
        screen.blit(coin,(100,570))
    fill += 0.5
    outline_rect = pygame.Rect(0, 0, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(0, 0, fill, BAR_HEIGHT)
    col = progress_colors[int(fill / 150)]
    rect(surf, col, fill_rect, 0, 4)
    rect(surf, WHITE, outline_rect, 3, 4)
    screen.blit(tries, (BAR_LENGTH, 0))
    screen.blit(sspeed, (300,580))
    screen.blit(scoins, (150,580))
 

def wait_for_key():
    """separate game loop for waiting for a key press while still running game loop
    """
    global level, start
    waiting = True
    while waiting:
        clock.tick(60)
        pygame.display.flip()

        if not start:
            start_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cv2.destroyAllWindows()              
                pygame.quit()
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    
                    start = True
                    waiting = False
                if event.key == pygame.K_ESCAPE:
                    cv2.destroyAllWindows() 
                    pygame.quit()


def coin_count(coins):
    """counts coins"""
    if coins >= 3:
        coins = 3
    coins += 1
    return coins


def resize(img, size=(32, 32)):
    """resize images
    :param img: image to resize
    :type img: im not sure, probably an object
    :param size: default is 32 because that is the tile size
    :type size: tuple
    :return: resized img

    :rtype:object?
    """
    resized = pygame.transform.smoothscale(img, size)               
    return resized


"""
Variables Y Constantes Globales

"""

#Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

#Control posición y velocidad

speed=2.0                                                                       #variable velocidad
Y=250                                                                           #coordenada Y avatar -->Iniciar en zona central
X=0                                                                             #Coordenada X avatar

font = pygame.font.SysFont("lucidaconsole", 20)                                 #Define un color de fondo

# square block face is main character the icon of the window is the block face
avatar = pygame.image.load(os.path.join("images", "avatar.png"))                 #Carga el avatar de la galeria de imagenes
pygame.display.set_icon(avatar)                                                 # pone el avatar como icono de la aplicación

alpha_surf = pygame.Surface(screen.get_size(), pygame.SRCALPHA)                 #desvanece el rastro del avatar a medida que avanza

# sprite groups
player_sprite = pygame.sprite.Group()
elements = pygame.sprite.Group()

# images
spike = pygame.image.load(os.path.join("images", "obj-spike.png"))
spike = resize(spike)
coin = pygame.image.load(os.path.join("images", "coin.png"))
coin = pygame.transform.smoothscale(coin, (32, 32))
block = pygame.image.load(os.path.join("images", "block_1.png"))
block = pygame.transform.smoothscale(block, (32, 32))
orb = pygame.image.load((os.path.join("images", "orb-yellow.png")))
orb = pygame.transform.smoothscale(orb, (32, 32))
trick = pygame.image.load((os.path.join("images", "obj-breakable.png")))
trick = pygame.transform.smoothscale(trick, (32, 32))

#  ints
fill = 0
num = 0
CameraX = 0
attempts = 0
coins = 0
angle = 0
level = 0

# list
particles = []
orbs = []
win_cubes = []

# initialize level with
levels = ["level_1.csv"]
level_list = block_map(levels[level])
level_width = (len(level_list[0]) * 32)
level_height = len(level_list) * 32
init_level(level_list)



pygame.display.set_caption('Geometry Dash Fly - PDI')                           #Poner titulo a la ventana de Juego


text = font.render('image', False, (255, 255, 0))                               #Inicaliza el fonso, para poner texto


music = pygame.mixer_music.load(os.path.join("music", "bossfight-Vextron.mp3")) #Carga musica de la carpeta de medios
pygame.mixer_music.play()                                                       # reporduce musica en el intro    


bg = pygame.image.load(os.path.join("images", "bg.png"))                        #Carga imagen de fondo del menu de inicio


player = Player(avatar, elements, (150, 150), player_sprite)                    #Crea un objeto de la clase jugador


tip = font.render("Procesamiento Digital de Imagenes 2022", True, GREEN)        # Agrega texto al fondo    



"""
-------------------------------------------------------------------------------
Ciclo Principal
-------------------------------------------------------------------------------
"""
while not done:
    keys = pygame.key.get_pressed()                                             #escanea interrupciones del teclado

    if not start:                                                               #Inicia el juego si no ha empezado
        wait_for_key()
        reset()                                                                 #da un reset 

        start = True

    player.vel.x = 0                                                            #Velocidad de avatar en cero                                                           

    eval_outcome(player.win, player.died)                                       #Función que procesa el estado de ganó o perdió
   
    alpha_surf.fill((255, 255, 255, 1), special_flags=pygame.BLEND_RGBA_MULT)   

    player_sprite.update()                                                      #Actualizar cinemática del avatar y del juego
    
    """ Llamado a la funcion de PDI la cual retorna la posición en Y"""
    Y = pdifun()                                                                #Funcion pdifun del modulo di
    


    """Define la velocidad de desplzamiento en X"""
    
    CameraX = player.vel.x = speed                                              # Velocidad en x
    move_map()                                                                  # Aplicar velocidad al mapa

    screen.blit(bg, (0, 0))                                                     # Clear the screen(with the bg)

    player.draw_particle_trail(player.rect.left - 1, player.rect.bottom + 2,
                               WHITE)                                           #Llama a la función que grafica la estela que deja el avatar
    screen.blit(alpha_surf, (0, 0))  # Blit the alpha_surf onto the screen.
    
    draw_stats(screen, coin_count(coins))                                       #Llama a la función que grafica la barra de estado y progreso

    player_sprite.draw(screen)                                                  # Dibuja el avatr y sus caracteristicas en pantalla de juego
    elements.draw(screen)                                                       # dinuja el mapa de obstáculos
   
    """Aumentar la velocidad progresivamente"""
    speed = speed + 0.01                                                        #cada ciclo aumenta la velocidad
    if (attempts == 10):
        speed = 5                                                              #reduce la velocidad despues de 10 intentos facilita jugabilidad
        #speed = speed + 0.01
       
    """Detección de eventos """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:                                           #salir del juego
            cv2.destroyAllWindows()                                             #Destruir ventanas de CV2
            done = True                                                         #Cerrar el ciclo principal
                
           
        if event.type == pygame.KEYDOWN:                                        #salir del juego
            if event.key == pygame.K_ESCAPE:                                   #Se presionó Esc        
                cv2.destroyAllWindows()                                        #Destruir ventanas de CV2         
                done = True                                                    #Terminar ciclo principal                                 
                
            

                
        
    pygame.display.flip()                                                       #Lanzar la pantalla de juego
    clock.tick(60)                                                              #define la velocidad del reloj
cv2.destroyAllWindows()                                                         #Destruir todas las ventanas de cv2   
pygame.quit()                                                                   #Cerrar y quitar  -->Finaliza el juego

