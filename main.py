#Space Invader Arcade Game
import random
import math
import time
import sys
import pygame
from pygame import mixer


# Pygame Initialization
pygame.init()

#Pygame Font Initialization
pygame.font.init()

#Create the Screen
WIDTH, HEIGHT = 800, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

#Title on Top Left Corner of Game Screen
pygame.display.set_caption("Space Invader")
icon = pygame.image.load("spaceship1.png")
pygame.display.set_icon(icon)

#Player Image
playerImg = pygame.image.load("space.png")

#Enemies Images
spaceship1 = pygame.image.load("alien.png")
spaceship2 = pygame.image.load("enemylevel2.png")
spaceship3 = pygame.image.load("level3.png")

#Background
background = pygame.transform.scale(pygame.image.load("background.png"), (WIDTH, HEIGHT))


#Background Music
mixer.music.load('Never Surrender.ogg')
mixer.music.play(-1)
mixer.music.set_volume(0.20)


#Player and Enemy Bullets
player_bullet = pygame.image.load("bullet.png")
enemy_bullet = pygame.image.load("enemybomb.png")

#Code to create Laser
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

#Creating the Ships
class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            bullet_sound = mixer.Sound('laser.wav')
            bullet_sound.play()
            bullet_sound.set_volume(0.10)

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()


#Player Ship
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = playerImg
        self.laser_img = player_bullet
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    #Moving Lasers for PLayer and if bullet hits enemy, they explode and disappear
    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                            explosion_sound = mixer.Sound('explosion.wav')
                            explosion_sound.play()
                            explosion_sound.set_volume(0.20)


    #Drawing the Player on Screen
    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    #Drawing the Healthbar of the Player
    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10))


#Enemy Ship and Drawing them on Screen
class Enemy(Ship):
    COLOR_MAP = {
                "1": (spaceship1, enemy_bullet),
                "2": (spaceship2, enemy_bullet),
                "3": (spaceship3, enemy_bullet)
                }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    #How Enemy shoots its Lasers
    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + 15, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            bullet_sound = mixer.Sound('laser.wav')
            bullet_sound.play()
            bullet_sound.set_volume(0.10)

#Collision Detection
def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


#The game itself
def main():
    run = True
    FPS = 60
    level = 0
    lives = 10
    main_font = pygame.font.SysFont("Cheapsman Free Regular.ttf", 50)
    bullet_font = pygame.font.SysFont("Cheapsman Free Regular.ttf", 30)
    lost_font = pygame.font.SysFont("Cheapsman Free Regular.ttf", 50)
    win_font = pygame.font.SysFont("Cheapsman Free Regular.ttf", 50)
    s_font = pygame.font.SysFont("Cheapman Free Regular.tff", 35)

    #Number of Enemies
    enemies = []
    wave_length = 5

    #Enemy Speed, Player Speed, Player Bullet Speed, and Enemy Bullet Speed
    enemy_vel = 1
    player_vel = 3
    player_laser_vel = 3
    enemy_laser_vel = 3

    player = Player(375, 600)

    clock = pygame.time.Clock()

    lost = False
    lost_count = 0

    win = False
    win_count = 0


    def redraw_window():
        WIN.blit(background, (0,0))

        #Draw Text
        lives_label = main_font.render(f"Lives: {lives}", 5, (0, 255, 0))
        level_label = main_font.render(f"Level: {level}", 1, (0, 255, 0))

        WIN.blit(lives_label, (10, 10))
        WIN.blit(level_label, (660, 10))

        for enemy in enemies:
            enemy.draw (WIN)

        player.draw(WIN)

        #Losing Screen
        if lost:
            WIN.blit(background, (0, 0))
            lost_text = lost_font.render("You have lost!!", 1, (255,255,255))
            WIN.blit(lost_text, (275, 350))
            lost_text = s_font.render(f"Levels Completed: {level-1}", 1, (255,255,255))
            WIN.blit(lost_text, (280, 400))
            pygame.mixer.music.stop()
            lost_sound = mixer.Sound('losing.wav')
            lost_sound.play()
            lost_sound.set_volume(0.10)

        #Winning Screen
        elif win:
            WIN.blit(background, (0, 0))
            win_text = win_font.render("Congratulations!! You have won!", 1, (255,255,255))
            WIN.blit(win_text, (150, 350))
            lost_text = s_font.render(f"Levels Completed: {level-1}", 1, (255,255,255))
            WIN.blit(lost_text, (290, 400))
            pygame.mixer.music.stop()
            win_sound = mixer.Sound('w.wav')
            win_sound.play()
            win_sound.set_volume(0.10)

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        #Conditions for Losing
        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1


        #Conditions for Winning
        elif level >= 4:
            win = True
            win_count += 1


        #Amount of Time Losing Screen Stays on Screen
        if lost:
            if lost_count > FPS * 5:
                run = False
            else:
                continue


        #Amount of Time Winning Screen Stays on Screen
        elif win:
            if win_count > FPS * 5:
                run = False
            else:
                continue

        #Where enemy ships spawn
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500*level/5, -100), random.choice(["1", "2", "3"]))
                enemies.append(enemy)


            #Level 2
            if level == 2:
                player_laser_vel = 15
                bullet_text = bullet_font.render("Powerup Acquired: Faster Bullets", 1, (0, 255, 0))
                WIN.blit(bullet_text, (350, 50))
                bonus_sound = mixer.Sound('bonus.wav')
                bonus_sound.play()
                bonus_sound.set_volume(0.75)


            #Level 3
            if level == 3:
                bullet_text = bullet_font.render("Disadvantage Acquired: Slowness and Faster Enemy Bullets", 1, (0, 255, 0))
                WIN.blit(bullet_text, (330, 50))
                player_vel = 2
                player.health = 100
                player_laser_vel = 3
                enemy_laser_vel = 5
                bonus_sound = mixer.Sound('bonus.wav')
                bonus_sound.play()
                bonus_sound.set_volume(0.75)

            #Level 4
            if level == 4:
                enemy_vel = 1
                player_laser_vel = 3
                player_vel = 5
                enemy_laser_vel = 3
                bonus_sound = mixer.Sound('bonus.wav')
                bonus_sound.play()
                bonus_sound.set_volume(0.75)

            #Level 5
            if level == 5:
                bullet_text = bullet_font.render("Advantage Acquired: Flash Speed", 1, (0, 255, 0))
                WIN.blit(bullet_text, (350, 50))
                enemy_vel = 2
                player_vel = 10
                player_laser_vel = 6
                bonus_sound = mixer.Sound('bonus.wav')
                bonus_sound.play()
                bonus_sound.set_volume(0.75)

            #Level 6
            if level == 6:
                bullet_text = bullet_font.render("Disadvantage Acquired: Faster Enemies", 1, (0, 255, 0))
                WIN.blit(bullet_text, (350, 50))
                enemy_vel = 3
                player_vel = 3
                bonus_sound = mixer.Sound('bonus.wav')
                bonus_sound.play()
                bonus_sound.set_volume(0.75)

            #Level 7
            if level == 7:
                enemy_vel = 3
                player_vel = 3
                bonus_sound = mixer.Sound('bonus.wav')
                bonus_sound.play()
                bonus_sound.set_volume(0.75)

            #Level 8
            if level == 8:
                enemy_vel = 3
                player_vel = 3
                bonus_sound = mixer.Sound('bonus.wav')
                bonus_sound.play()
                bonus_sound.set_volume(0.75)

            #Level 9
            if level == 9:
                enemy_vel = 3
                player_vel = 3
                bonus_sound = mixer.Sound('bonus.wav')
                bonus_sound.play()
                bonus_sound.set_volume(0.75)

            #Level 10
            if level == 10:
                bullet_text = bullet_font.render("Advantages Acquired: Flash Speed and Speed Bullets", 1, (0, 255, 0))
                WIN.blit(bullet_text, (325, 50))
                enemy_vel = 3
                player_vel = 10
                player_laser_vel = 15
                bonus_sound = mixer.Sound('bonus.wav')
                bonus_sound.play()
                bonus_sound.set_volume(0.75)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        #Controls for User Player
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_vel > 0: #left
            player.x -= player_vel
        if keys[pygame.K_RIGHT] and player.x + player_vel + player.get_width() < WIDTH: #right
            player.x += player_vel
        if keys[pygame.K_UP] and player.y - player_vel > 0:   #up
            player.y -= player_vel
        if keys[pygame.K_DOWN] and player.y + player_vel + player.get_height() + 15 < HEIGHT: #down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot()

        #Directions where Enemies shoot
        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_lasers(enemy_laser_vel, player)

            if random.randrange(0, 120) == 1:
                enemy.shoot()


            #Player-Enemy Collision
            if collide(enemy, player):
                player.health -= 15
                enemies.remove(enemy)
                explosion_sound = mixer.Sound('explosion.wav')
                explosion_sound.play()
                explosion_sound.set_volume(0.20)

            pygame.display.update()


            #If Enemies go past screen, lives are substracted
            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)

        player.move_lasers(-player_laser_vel, enemies)


#Main Menu Screen
def main_menu():
    title_font = pygame.font.SysFont("Cheapsman Free Regular.ttf", 70)
    subtitle_font = pygame.font.SysFont("Cheapsman Free Regular.ttf", 35)
    press_font = pygame.font.SysFont("Cheapsman Free Regular.ttf",30)
    run = True
    while run:
        WIN.blit(background, (0,0))
        title_label = title_font.render("S", 1, (0,255,0))
        WIN.blit(title_label, (225, 50))
        title_label = title_font.render("P", 1, (255, 255, 0))
        WIN.blit(title_label, (255, 50))
        title_label = title_font.render("A", 1, (0, 255, 255))
        WIN.blit(title_label, (280, 50))
        title_label = title_font.render("C", 1, (155, 255, 0))
        WIN.blit(title_label, (310, 50))
        title_label = title_font.render("E", 1, (255, 255, 155))
        WIN.blit(title_label, (340, 50))
        title_label = title_font.render("I", 1, (155, 255, 155))
        WIN.blit(title_label, (390, 50))
        title_label = title_font.render("N", 1, (75, 75, 0))
        WIN.blit(title_label, (400, 50))
        title_label = title_font.render("V", 1, (100, 100, 100))
        WIN.blit(title_label, (432, 50))
        title_label = title_font.render("A", 1, (0, 0, 255))
        WIN.blit(title_label, (455, 50))
        title_label = title_font.render("D", 1, (128, 0, 0))
        WIN.blit(title_label, (485, 50))
        title_label = title_font.render("E", 1, (128, 0, 128))
        WIN.blit(title_label, (515, 50))
        title_label = title_font.render("R", 1, (0, 150, 150))
        WIN.blit(title_label, (545, 50))
        title_label = title_font.render("S", 1, (192, 192, 192))
        WIN.blit(title_label, (575, 50))
        subtitle_label = subtitle_font.render("Controls: Use arrow keys to control, and spacebar to shoot", 1, (255, 255, 255))
        WIN.blit(subtitle_label, (50, 150))
        subtitle_label = subtitle_font.render("Objective: Eliminate all targets before they reach you and avoid", 1, (255,255,255))
        WIN.blit(subtitle_label, (40, 200))
        subtitle_label = subtitle_font.render("getting hit by bullets or crashing into them", 1, (255, 255, 255))
        WIN.blit(subtitle_label, (180,250))
        subtitle_label = subtitle_font.render("You better eliminate them because each level gets harder!!", 1, (255, 0, 0))
        WIN.blit(subtitle_label, (65,315))
        subtitle_label = press_font.render("To start, press anywhere using your mouse button or keyboard touchpad", 1, (255,255,255))
        WIN.blit(subtitle_label, (50, 385))
        subtitle_label = press_font.render("To exit, press the red button on the top right of the screen or close this screen", 1, (255,255,255))
        WIN.blit(subtitle_label, (25, 455))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
                pygame.mixer.music.play()

    pygame.quit()
                #If Player clicks screen, they start the game. If they close the screen, pygame will quit and close the screen.
                #If the Player wins or loses, it goes to the winning or losing screen for a few seconds before going back to the main menu.

main_menu()


