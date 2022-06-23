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
blocksx,blocksy=1000,2000
ground_level=1000
sky_level=1200
velocityx,velocityy=0,0
mousex,mousey=0,0
collision_array=[False,False,False,False]#N,E,S,W
clicked=False
right_clicked=False
direction="right"
mouse_down=False
right_mouse_down=False
inventory_open=False

font = pygame.font.SysFont("Arial" , 20)
font=pygame.font.Font("small_pixel.ttf", 6)
back = pygame.image.load("back1.png").convert()
character = pygame.image.load("character.png").convert_alpha()

break_0 = pygame.image.load("break_0.png").convert_alpha()
break_1 = pygame.image.load("break_1.png").convert_alpha()
break_2 = pygame.image.load("break_2.png").convert_alpha()
pickaxe = pygame.image.load("pickaxe.png").convert_alpha()

#Importing Sounds
pygame.mixer.init()
break_SOUND=pygame.mixer.Sound("break.ogg")
pygame.mixer.Sound.set_volume(break_SOUND,0.2)








#Items - store in folder and load later on
item_dict={"Dirt":[(127,81,18),(123,76,15),10],
            "Grass":[(127,81,18),(123,76,15),10],
            "Stone":[(100,100,100),(110,110,100),30],
            "Diamond":[(0,191,255),(30,144,255),120],
            "Iron":[(18,35,53),(15,30,50),50],
            "Lead":[(30,30,30),(25,25,25),50],
            "Copper":[(214,118,0),(210,114,0),40],
            "Gold":[(254,221,0),(250,215,0),60],
            "Marble":[(250,250,250),(240,240,240),40]}

#Block Ideas Iron, Lead, Copper, Gold, Marble, Limestone



#DEVELOPER OPTIONS
double_jump=True
speed_mult=1
jump_mult=1
mine_mult=1
action_dist_mult=1

#################

#Global Variables
speed=1*speed_mult
jump_velocity=5*jump_mult
gravity=10
action_distance=56*action_dist_mult

count=1050
starty=17000
startx=-(blocksx*8)



def fps_counter():
    fps = str(int(clock.get_fps()))
    fps_t = font.render(fps , False, pygame.Color("RED"))
    pixel.blit(fps_t,(0,0))

def dev_info():
    x= font.render(str("x:"+str(int((worldx+8)/16))+" y:"+str(int((starty+worldy)/16))), False, pygame.Color("RED"))
    pixel.blit(x,(0,160))


class Item:
    def __init__(self,item):
        self.item=item
        self.count=1
    pass
class Tool(Item):
    def __init__(self,item):
        self.item=item
        self.health=100
class ItemBlock(Item):
    pass
class ItemOther(Item):
    pass



class Inventory:
    def __init__(self):
        self.items=[["Pickaxe",0],["None",0],["None",0],["None",0],["None",0],["None",0],["None",0],["None",0]]#Item,Count
        self.selected=0

    def add_item(self,item):
        for i in self.items:
            if i[0]==item:
                i[1]+=1
                return

        new=[item,1]
        for i in self.items:
            if i[0]=="None":
                i[0]=item
                i[1]=1
                return

    def remove_item(self,item):
        for i in self.items:
            if i[0]==item:
                i[1]-=1
                if i[1]<=0:
                    i[0]="None"
                    i[1]=0
                return

    def draw(self):
        c=0
        for i in self.items:
            if i[0]=="Pickaxe":
                pixel.blit(pickaxe,(80+c*20+6,2+4))
            elif i[0]!="None":
                pygame.draw.rect(pixel,item_dict[i[0]][0],(80+c*20+6,2+4,8,8))
                pygame.draw.rect(pixel,item_dict[i[0]][1],(80+c*20+6,2+4,8,8),1)
                text = font.render(str(i[1]), False,(255,255,255))
                pixel.blit(text,(91+c*20-(text.get_width()/2),10))
            c+=1

    def update_selected(self,value):
        self.selected+=value
        if self.selected>7:
            self.selected=0
        elif self.selected<0:
            self.selected=7


class Block:
    def __init__(self,x,y,item,listx,listy):
        self.x=x
        self.y=y
        self.item=item
        self.listx=listx
        self.listy=listy
        self.health=10
        self.max_health=10

    def draw(self):
        if self.item=="None":
            return

        pygame.draw.rect(pixel,item_dict[self.item][0],(worldx+self.x,worldy+self.y,16,16),0)
        pygame.draw.rect(pixel,item_dict[self.item][1],(worldx+self.x,worldy+self.y,16,16),2)
        if self.item=="Grass":
            pygame.draw.rect(pixel,(34,139,34),(worldx+self.x,worldy+self.y,16,2),2)
        if worldx+self.x<mousex and worldx+self.x+16>mousex and worldy+self.y<mousey and worldy+self.y+16>mousey:
            #Check mouse within range
            if mousex>160-action_distance and mousex<160+action_distance and mousey>90-action_distance and mousey<90+action_distance:
                if mouse_down==True and inventory.items[inventory.selected][0]=="Pickaxe":
                    self.health-=1*mine_mult
                    if self.health<=0:
                        pygame.mixer.Sound.play(break_SOUND)
                        inventory.add_item(self.item)
                        self.item="None"
                        return
                    else:
                        proportion=self.health/self.max_health
                        if proportion>0.66:
                            pixel.blit(break_0,(worldx+self.x,worldy+self.y))
                        elif proportion>0.33:
                            pixel.blit(break_1,(worldx+self.x,worldy+self.y))
                        else:
                            pixel.blit(break_2,(worldx+self.x,worldy+self.y))

                pygame.draw.rect(pixel,(255,255,255),(worldx+self.x,worldy+self.y,16,16),1)

    def check_col(self):
        if self.item=="None":
            return
        global collision_array,worldy,worldx

        #South- check if about to collide, set accordingly. Use velocityy
        if worldx+self.x>137 and worldx+self.x<166 and worldy+self.y+velocityy<=98 and worldy+self.y+velocityy>82:
            collision_array[2]=True

        #North - use velocityy here too
        if worldx+self.x>137 and worldx+self.x<166 and worldy+self.y+velocityy>=67 and worldy+self.y+velocityy<80:
            collision_array[0]=True

        #East

        if worldx+self.x>=166 and worldx+self.x<166+speed and worldy+self.y>67 and worldy+self.y<97:
            collision_array[1]=True

        #West

        if worldx+self.x<=137 and worldx+self.x>137-speed and worldy+self.y>67 and worldy+self.y<97:
            collision_array[3]=True

    def reset_health(self):
        if self.item=="None":
            return
        self.health=item_dict[self.item][2]
        self.max_health=item_dict[self.item][2]

    def set_item(self,new):
        self.item=new
        if new!="None":
            self.reset_health()


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
    inventory.draw()
    pygame.draw.rect(pixel,(255,255,255),(80+inventory.selected*20+2,2,16,16),2)

def move_character():
    global worldx,worldy,velocityy


    if collision_array[2]==False:
        if velocityy>(-gravity):
            velocityy-=0.3

    if collision_array[2]==True and velocityy<0:#South
        worldy+=velocityy
        velocityy=0
        worldy=rounder(worldy,16)+8

    if collision_array[0]==True and velocityy>0:
        worldy+=velocityy
        velocityy=0
        worldy=rounder(worldy,16)-6


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
    firstx=-int((startx+worldx)/16)-1

    for y in range(14):
        for x in range(22):
            add=global_array[firstx+x][firsty-y]
            if add!=0:
                block_array.append(add)
    #if block in worldx-320 worldy-180

def generate_veins(transform,total,minH,maxH,minStart,maxStart,size):
    global global_array
    for i in range(total):
        px,py=random.randint(0,999),random.randint(minStart,maxStart)
        for i in range(size):
            px+=random.choice([-1,0,1])
            py+=random.choice([-1,0,1])
            if px<0:
                px=0
            elif px>999:
                px=999
            if py<minH:
                py=minH
            elif py>maxH:
                py=maxH

            if transform==0:
                global_array[px][py]=transform
            else:
                if global_array[px][py]!=0:
                    global_array[px][py].set_item(transform)



def generate_caves(total,minH,maxH,minStart,maxStart,length,width):
    #Give weight to certain direction
    #Length of cave and width, will cross into others to create caves
    global global_array
    
    for i in range(total):
        px,py=random.randint(0,999),random.randint(minStart,maxStart)
        move_arrayx=[-1,0,1]
        move_arrayy=[-1,0,1]
        move_arrayx.append(random.choice(move_arrayx))
        move_arrayy.append(random.choice(move_arrayy))
        for l in range(length):
            px+=random.choice(move_arrayx)
            py+=random.choice(move_arrayy)

            if px<0:
                px=0
            elif px>999:
                px=999
            if py<minH:
                py=minH
            elif py>maxH:
                py=maxH

            global_array[px][py].set_item("None")

def remove_lone_blocks():
    global global_array
    for y in range(blocksy):
        if y!=0 and y!=blocksy:
            for x in range(blocksx):
                if global_array[x][y].item!="None":
                    if x!=9 and x!=blocksx-1:
                        if global_array[x-1][y].item=="None" and global_array[x+1][y].item=="None" and global_array[x][y-1].item=="None" and global_array[x][y+1].item=="None":
                            global_array[x][y].set_item("None")
                

def create_layer(min,max,item):#Use to create a layer of blocks
    for y in range(max-min):
        for x in range(blocksx):
            global_array[x][y+min].set_item(item)

    #Blending into current ground
    odds=0.9
    for y in range(8):
        odds-=0.1
        for x in range(blocksx):
            rando=random.random()
            if rando<odds:
                if global_array[x][max+y]!=0:
                    global_array[x][max+y].set_item(item)

#For now fill space under ground level
def background():
    if worldy<-(ground_level+180):
        pixel.fill([64,41,9])
    elif worldy<-(ground_level-90):
        pygame.draw.rect(pixel,(64,41,9),(0,ground_level+90+worldy,320,300))#Y pos should be where level 1000 is


def check_action():
    #Place Item here
    #Use maths to calculate where to place new block and use inventory selection to place
    #use mousex,mousey
    global global_array
    if inventory.items[inventory.selected][0]!="Pickaxe":#Remove this and replace with blocks/item system
        if mousex>160-action_distance and mousex<160+action_distance and mousey>90-action_distance and mousey<90+action_distance:
            x=int((mousex-worldx-startx)/16)
            y=int(-(mousey-worldy-starty-98)/16)+1

            #Get item and place if possible, and not over character
            if global_array[x][y].item=="None":
                #Check mouse not over character
                if not (mousex>152 and mousex<168 and mousey>82 and mousey<98):
                    if inventory.items[inventory.selected]!="None":
                        global_array[x][y].set_item(inventory.items[inventory.selected][0])
                        inventory.remove_item(inventory.items[inventory.selected][0])



#Create blocks from bottom, with semi random heights
global_array=[]
for x in range(blocksx):
    new=[]
    for y in range(blocksy):
        new.append(Block(startx+worldx+x*16,worldy+starty-(y*16)+98,"None",x,y))
    global_array.append(new)

#Change at most -3 3
change=0
weight=0
for x in range(blocksx):
    change+=random.randint(-1-int(weight/2),1-int(weight/2))
    weight+=change
    if change>2:
        change=2
    elif change<-2:
        change=-2
    count+=change
    if count<ground_level:
        count=ground_level
    elif count>sky_level:
        count=sky_level
    for y in range(count):
        global_array[x][y].set_item("Dirt")
    global_array[x][count].set_item("Grass")


#Generate veins and caves trans,total,min,max,size
##Iron,Lead,Copper,Gold

#Stone layer
create_layer(0,1000,"Stone")

generate_caves(1000,20,1050,100,1000,300,10)#LONG CAVES
generate_veins("None",1000,0,1050,0,950,200)#HOLLOW CAVES

generate_veins("Dirt",3000,0,1000,0,900,200)
generate_veins("Stone",500,950,1050,950,1030,100)
generate_veins("Marble",50,0,1000,0,700,500)
generate_veins("Iron",1000,0,1000,0,980,20)
generate_veins("Lead",1000,0,1000,0,980,20)
generate_veins("Copper",1000,0,1000,0,950,10)
generate_veins("Gold",1000,0,500,0,480,10)
generate_veins("Diamond",100,0,200,0,200,5)

remove_lone_blocks()


block_array=[]
inventory=Inventory()

while True:
    pixel.fill([173,216,230])

    if right_mouse_down or right_clicked:
        check_action()

    generate_block_array()



    check_collisions()
    move_character()
    background()
    draw_blocks()
    draw_character()

    draw_inventory()
    fps_counter()
    dev_info()

    clicked=False
    right_clicked=False
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
                if velocityy==0 or double_jump:
                    velocityy=jump_velocity
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_d:
                velocityx-=speed
                direction="right"
            elif event.key==pygame.K_a:
                velocityx+=speed
                direction="left"
            elif event.key==pygame.K_r:
                worldx,worldy=0,0
            elif event.key==pygame.K_e:
                inventory_open=not inventory_open
            elif event.key==pygame.K_1:
                inventory.selected=0
            elif event.key==pygame.K_2:
                inventory.selected=1
            elif event.key==pygame.K_3:
                inventory.selected=2
            elif event.key==pygame.K_4:
                inventory.selected=3
            elif event.key==pygame.K_5:
                inventory.selected=4
            elif event.key==pygame.K_6:
                inventory.selected=5
            elif event.key==pygame.K_7:
                inventory.selected=6
            elif event.key==pygame.K_8:
                inventory.selected=7
        elif event.type==pygame.MOUSEMOTION:
            mousex,mousey=event.pos
            mousex=mousex*(320/width)
            mousey=mousey*(180/height)
        elif event.type==pygame.MOUSEBUTTONUP:
            if event.button==1:
                clicked=True
                mouse_down=False
            elif event.button==3:
                right_clicked=True
                right_mouse_down=False
        elif event.type==pygame.MOUSEBUTTONDOWN:
            if event.button==1:
                mouse_down=True
            elif event.button==3:
                right_mouse_down=True
        elif event.type==pygame.MOUSEWHEEL:
            inventory.update_selected(-event.y)


    pygame.display.flip()
    clock.tick(60)

#Removed lone blocks 13/06
#Added double cave gen 13/06
#Adding stone below certain level 13/06
#Add random stone and dirt to world 13/06
#Adding item collection,using dict 13/06
#Get font to display small text in game 13/06
#Made first bar of inventory work 13/06
#V0.2
#Added sound 13/06
#Added grass 13/06
#Changed dirt terrain gen 13/06
#Added marble 13/06
#Made numbers work on inventory 13/06
#Fixed remove lone blocks 13/06
#Created item setter function, so health resets now 15/06
#Then can add block breaking animation 15/06
#Added action distance, needed to break n place 15/06
#Added pickaxe 15/06


#Plan for V0.3 Inventory
#Redo inventory using item classes
#Add items dropping and picking them up
#Add crafting system
#Add some craftable blocks and items
#Add usable objects - chest, door, hatch, ladder
#Binning items

#Plan for V0.4 Combat
#Add health system
#Add enemies
#Add weapons
#Add armour

#Plan for V0.5 Improvements & Bosses
#Add 2 bosses
#Improve textures
#Rehaul surface generation
#Add underground structures/caves
#Add deeper cave layers
#Parallax background
#Try lighting
#Add blowing grass and lots of pixel art

#Plan for V0.6 Functionality Update
#Furnaces
#Machines
#Workbench
#Computer / wiki
#Enchantor
#Trees and axe










    
