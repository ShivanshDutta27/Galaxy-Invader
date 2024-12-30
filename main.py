import random

import pygame
import os


pygame.init()
pygame.font.init()

#LOADING IN ALL THE IMAGES         We can do it directly too but its cleaner if we use os.path.join
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# LASERS
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

# BACKGROUND
bg_path = os.path.join("assets", "background-black.png")
print("Loading background from:", bg_path)  # Debugging
BG = pygame.transform.scale(pygame.image.load(bg_path), (1000, 800))


# Setting Up the Window
WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Galaxy Invader")

# Abstract class for all Ships , so it wont be directly used but inherited from
class Laser:
    def __init__(self,x,y,img):
        self.x=x
        self.y=y
        self.img=img
        self.mask=pygame.mask.from_surface(self.img)
    def draw(self,window):
        window.blit(self.img,(self.x,self.y))
    def move(self,vel):
        self.y+=vel
    def offscreen(self,h):
        return self.y<=h and self.y>=0
    def collision(self,obj):
        return collide(obj,self)


def collide(obj1,obj2):
    offset_x=obj2.x-obj1.x
    offset_y=obj2.y-obj1.y
    return obj1.mask.overlap(obj2,(offset_x,offset_y)) !=None

class Ship:
    COOLDOWN=40
    def __init__(self,x,y,health=100):
        self.x=x
        self.y=y
        self.health=health
        self.ship_img=None
        self.laser_img=None
        self.lasers=[]
        self.cooldown_counter=0

    def shoot(self):
        if self.cooldown_counter==0:
            laser=Laser(self.x,self.y,self.laser_img)
            self.lasers.append(laser)
            self.cooldown_counter=1
    # This function is just to check collision with player, for enemies , seperate function in player class
    def move_lasers(self,vel,obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.offscreen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health-=10



    def cooldown(self):
        if self.cooldown_counter >= self.COOLDOWN:
            self.cooldown_counter=0
        elif self.cooldown_counter>0:
            self.cooldown_counter+=1

    def draw(self,WIN):                         #position, size
        WIN.blit(self.ship_img,(self.x,self.y))
        for laser in self.lasers:
            laser.draw(WIN)


    def get_width(self):
        return self.ship_img.get_width()
    def get_height(self):
        return self.ship_img.get_height()



class Player(Ship):
    def __init__(self,x,y,health=100):
        super().__init__(x, y, health)

        self.ship_img=YELLOW_SPACE_SHIP
        self.laser_img=YELLOW_LASER

        # Masking for Pixel Perfect Collision
        self.mask=pygame.mask.from_surface(self.ship_img)# Identifies where pixels are and aren't
        self.max_health=health



class Enemy(Ship):
    COLOR_MAP={
        "red":[RED_SPACE_SHIP,RED_LASER],
        "green":[GREEN_SPACE_SHIP,GREEN_LASER],
        "blue":[BLUE_SPACE_SHIP,BLUE_LASER]
    }
    def __init__(self,x,y,color,health=100):
        super().__init__(x, y, health)

        self.ship_img,self.laser_img=self.COLOR_MAP[color]
        self.mask=pygame.mask.from_surface(self.ship_img)
        self.max_health=health
    def move(self,vel):
        self.y+=vel

# Main game loop
def main():
    run = True
    fps = 80
    clock = pygame.time.Clock()
    level,lives=1,5
    player_velocity=4

    enemies=[]
    wavelength=5
    enemy_vel=1


    main_font = pygame.font.SysFont("JetBrains Mono",24)
    lost_font = pygame.font.SysFont("Arial", 50)

    player=Player(WIDTH//2-25,700)
    lost = False
    lost_count=0

    def redraw():
        WIN.blit(BG, (0, 0))
        lives_text=main_font.render(f"Lives left: {lives}",1,"white")
        level_text = main_font.render(f"Level: {level}",1,"white")

        WIN.blit(level_text,(10,10))
        WIN.blit(lives_text,(10,10+level_text.get_height()+5))

        for enemy in enemies:
            enemy.draw(WIN)
        # The ordering here makes it so that if they overlap then player will be visible as it is drawn later
        player.draw(WIN)

        if lost:
            lost_label=lost_font.render("Git Gud",1,"white")
            WIN.blit(lost_label,(WIDTH//2-lost_label.get_width()//2, HEIGHT//2-lost_label.get_height()//2))

        pygame.display.update()

    while run:
        clock.tick(fps)

        #Checking if lost
        if lives<=0 or player.health<=0:
            lost=True
            lost_count+=1

        if lost:
            redraw()
            if lost_count>fps*5:
                run=False
            else:
                continue

        if len(enemies)==0:
            level+=1           # All destroyed so level over
            wavelength+=3*level//2
            enemy_vel+=0.2

            #Spawning enemies
            for i in range(wavelength):
                enemy_x=random.randrange(50, WIDTH-100,)
                enemy_y=random.randrange(-round(800*(level/4)),-100)
                enemy=Enemy(enemy_x,enemy_y,random.choice(["red","green","blue"]))
                enemies.append(enemy)


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        # if we handle the movement inside this for loop, it wont register multiple clicks at the same time
        keys=pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x-player_velocity>0: #moving left
            player.x-=player_velocity
        if keys[pygame.K_d]and player.x+player.get_width()+player_velocity<WIDTH: #moving right
            player.x+=player_velocity
        if keys[pygame.K_s] and player.y+player.get_hegiht()+player_velocity<HEIGHT: #moving down
            player.y+=player_velocity
        if keys[pygame.K_w] and player.y+player_velocity>0: #moving up
            player.y-=player_velocity

        if keys[pygame.K_SPACE]:
            player.shoot()


        for enemy in enemies[:]:
            enemy.move(round(enemy_vel))

            if enemy.y +enemy.get_height()>HEIGHT:
                lives-=1
                enemies.remove(enemy)

        redraw()

    pygame.quit()

if __name__ == "__main__":
    main()
