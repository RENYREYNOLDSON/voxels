import sys,pygame,random
from tkinter import W
pygame.init()
clock=pygame.time.Clock()
info = pygame.display.Info()

width=info.current_w
height=info.current_w*(9/16)

screen = pygame.display.set_mode((width,height))#pygame.FULLSCREEN
pixel = pygame.Surface((320,180))#pygame.FULLSCREEN

worldx,worldy=0,0
blocksx,blocksy=1000,200
velocityx,velocityy=0,0
mousex,mousey=0,0
speed=1
gravity=10
collision_array=[False,False,False,False]#N,E,S,W
clicked=False
direction="right"

font = pygame.font.SysFont("Arial" , 20)
back = pygame.image.load("back1.png").convert()
character = pygame.image.load("character.png").convert_alpha()


def fps_counter():
    fps = str(int(clock.get_fps()))
    fps_t = font.render(fps , 1, pygame.Color("RED"))
    pixel.blit(fps_t,(0,0))




class Block:
    def __init__(self,x,y,item,listx,listy):
        self.x=x
        self.y=y
        self.item=item
        self.listx=listx
        self.listy=listy

    def draw(self):
        pygame.draw.rect(pixel,(150,75,0),(worldx+self.x,worldy+self.y,16,16),0)
        pygame.draw.rect(pixel,(145,70,0),(worldx+self.x,worldy+self.y,16,16),2)
        if worldx+self.x<mousex and worldx+self.x+16>mousex and worldy+self.y<mousey and worldy+self.y+16>mousey:
            if clicked==True:
                global_array[self.listx][self.listy]=0
            else:
                pygame.draw.rect(pixel,(255,255,255),(worldx+self.x,worldy+self.y,16,16),1)

    def check_col(self):
        global collision_array,worldy,worldx
        #South
        if worldx+self.x>137 and worldx+self.x<166 and worldy+self.y>90 and worldy+self.y<100:
            collision_array[2]=True

        #North
        if worldx+self.x>137 and worldx+self.x<166 and worldy+self.y>67 and worldy+self.y<75:
            collision_array[0]=True

        #East

        if worldx+self.x>=166 and worldx+self.x<166+speed and worldy+self.y>67 and worldy+self.y<97:
            collision_array[1]=True

        #West

        if worldx+self.x<=137 and worldx+self.x>137-speed and worldy+self.y>67 and worldy+self.y<97:
            collision_array[3]=True


def rounder(number,multiple):
    return multiple*round(number/multiple)


def draw_character():
    if direction=="right":
        pixel.blit(character,(152,82))
    else:
        rev=pygame.transform.flip(character,True,False)
        pixel.blit(rev,(152,82))


def draw_inventory():
    for i in range(8):
        pygame.draw.rect(pixel,(53,30,40),(80+i*20+2,2,16,16),2)
        pygame.draw.rect(pixel,(218,165,32),(80+i*20+3,3,14,14),1)

def move_character():
    global worldx,worldy,velocityy


    if collision_array[2]==False:
        if velocityy>(-gravity):
            velocityy-=0.3
    if collision_array[2]==True and velocityy<0:
        velocityy=0
        worldy=rounder(worldy,8)
    if collision_array[0]==True and velocityy>0:
        worldy=rounder(worldy,16)
        velocityy=0

    if collision_array[1]==False and velocityx<0:
        worldx+=velocityx

    if collision_array[3]==False and velocityx>0:
        worldx+=velocityx

    worldy+=velocityy

def check_collisions():
    for b in block_array:
        b.check_col()

def draw_blocks():
    for b in block_array:
        b.draw()

#worldx,worldy needed and starty. 1000 is very bottom, first added. -600 is top. each bit 16
def generate_block_array():
    global block_array
    block_array=[]
    firsty=int((starty+worldy+122)/16)
    firstx=-int((startx+worldx)/16)

    for y in range(13):
        for x in range(22):
            add=global_array[firstx+x][firsty-y]
            if add!=0:
                block_array.append(add)
    #if block in worldx-320 worldy-180

def generate_caves():
    global global_array
    for i in range(100000):
        global_array[random.randint(0,999)][random.randint(0,199)]=0

def background():
    #pixel.blit(back,(0,0))
    pass

#Create blocks from bottom, with semi random heights
global_array=[]
for x in range(blocksx):
    new=[]
    for y in range(blocksy):
        new.append(0)
    global_array.append(new)


count=50
starty=1200
startx=-(blocksx*8)
for x in range(blocksx):
    count+=random.randint(-2,2)
    for y in range(count):
        global_array[x][y]=Block(startx+worldx+x*16,worldy+starty-(y*16)+98,(200,100,67),x,y)

generate_caves()
block_array=[]

while True:
    pixel.fill([173,216,230])
    background()
    generate_block_array()
    check_collisions()
    move_character()

    draw_blocks()
    draw_character()

    draw_inventory()
    fps_counter()

    clicked=False
    collision_array=[False,False,False,False]#N,E,S,W
    screen.blit(pygame.transform.scale(pixel,(width,height)),(0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type==pygame.KEYUP:
            if event.key==pygame.K_d:
                velocityx+=speed
            elif event.key==pygame.K_a:
                velocityx-=speed
            elif event.key==pygame.K_SPACE:
                if velocityy==0:
                    velocityy=5
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_d:
                velocityx-=speed
                direction="right"
            elif event.key==pygame.K_a:
                velocityx+=speed
                direction="left"
        elif event.type==pygame.MOUSEMOTION:
            mousex,mousey=event.pos
            mousex=mousex*(320/width)
            mousey=mousey*(180/height)
        elif event.type==pygame.MOUSEBUTTONUP:
            clicked=True
            print(mousex,mousey)

    pygame.display.flip()
    clock.tick(60)


#Add DEV MODE

#Simply subtract velocity for better collisions
#Make north collision smaller, so can squeeze through gaps
#Calculate square on click, not check each one
#Cave Gen
#Create several types
#Add placing of blocks
#Add inventory
#Add lighting
#Add enemies
#Add combat/health etc
#Add items and crafting
#Add storage
#Create animations & textures for prototype
#Add a boss
#Add random item stats etc







    
