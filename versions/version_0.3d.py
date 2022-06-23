import sys,pygame,random,copy,math
pygame.init()
clock=pygame.time.Clock()
info = pygame.display.Info()

width=info.current_w
height=info.current_w*(9/16)

screen = pygame.display.set_mode((width,height))#pygame.FULLSCREEN
pixel = pygame.Surface((320,180))#pygame.FULLSCREEN

worldx,worldy=0,0
blocksx,blocksy=200,2000
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
climbing=False

font = pygame.font.SysFont("Arial" , 20)
font=pygame.font.Font("./fonts/small_pixel.ttf", 6)

character = pygame.image.load("./textures/character.png").convert_alpha()

break_0 = pygame.image.load("./textures/break_0.png").convert_alpha()
break_1 = pygame.image.load("./textures/break_1.png").convert_alpha()
break_2 = pygame.image.load("./textures/break_2.png").convert_alpha()
pickaxe = pygame.image.load("./textures/pickaxe.png").convert_alpha()

#Block images
dirt_img = pygame.image.load("./textures/Dirt.png").convert()

dirt_imgB = pygame.image.load("./textures/Dirt.png").convert()
dirt_imgB.fill((50,50,50), special_flags=pygame.BLEND_RGB_ADD) 
stone_img = pygame.image.load("./textures/Stone.png").convert()
stone_imgB = pygame.image.load("./textures/StoneB.png").convert()
grass_img = pygame.image.load("./textures/Grass.png").convert()
gold_img = pygame.image.load("./textures/Gold.png").convert()
marble_img = pygame.image.load("./textures/Marble.png").convert()
lead_img = pygame.image.load("./textures/Lead.png").convert()
diamond_img = pygame.image.load("./textures/Diamond.png").convert()
iron_img = pygame.image.load("./textures/Iron.png").convert()
copper_img = pygame.image.load("./textures/Copper.png").convert()
brick_img = pygame.image.load("./textures/Brick.png").convert()
light_img = pygame.image.load("./textures/Light.png").convert_alpha()
ladder_img = pygame.image.load("./textures/Ladder.png").convert_alpha()
glass_img = pygame.image.load("./textures/Glass.png").convert_alpha()
metal_img = pygame.image.load("./textures/Metal.png").convert_alpha()
chest_img = pygame.image.load("./textures/Chest.png").convert_alpha()

#Importing Sounds
pygame.mixer.init()
break_SOUND=pygame.mixer.Sound("./sounds/break.ogg")
pygame.mixer.Sound.set_volume(break_SOUND,0.2)

click_SOUND=pygame.mixer.Sound("./sounds/click.ogg")
pygame.mixer.Sound.set_volume(click_SOUND,0.3)







#Items - store in folder and load later on
item_dict={"Dirt":[(127,81,18),(123,76,15),10,dirt_img,dirt_imgB],
            "Grass":[(127,81,18),(123,76,15),10,grass_img],
            "Stone":[(100,100,100),(110,110,100),30,stone_img,stone_imgB],
            "Diamond":[(0,191,255),(30,144,255),120,diamond_img],
            "Iron":[(18,35,53),(15,30,50),50,iron_img],
            "Lead":[(30,30,30),(25,25,25),50,lead_img],
            "Copper":[(214,118,0),(210,114,0),40,copper_img],
            "Gold":[(254,221,0),(250,215,0),60,gold_img],
            "Marble":[(250,250,250),(240,240,240),40,marble_img],
            "Brick":[(250,200,250),(240,240,240),60,brick_img],
            "Light":[(0,200,250),(20,240,240),5,light_img],
            "Ladder":[(0,200,250),(20,240,240),5,ladder_img],
            "Glass":[(0,200,250),(20,240,240),5,glass_img],
            "Metal":[(0,200,250),(20,240,240),40,metal_img],
            "Chest":[(0,200,250),(20,240,240),20,chest_img],}







###########DEVELOPER OPTIONS
double_jump=False
speed_mult=1
jump_mult=1
mine_mult=1
action_dist_mult=1

god_mode=False


#################

#Global Variables
speed=1*speed_mult
jump_velocity=5*jump_mult
gravity=10
action_distance=56*action_dist_mult
climbing_speed=1

count=1050
starty=17000
startx=-(blocksx*8)



def fps_counter():
    fps = str(int(clock.get_fps()))
    fps_t = font.render(fps , False, pygame.Color("RED"))
    pixel.blit(fps_t,(0,0))

def dev_info():
    x= font.render(str("x:"+str(int((worldx+8)/16))+" y:"+str(int((starty+worldy)/16))), False, pygame.Color("RED"))
    pixel.blit(x,(0,174))

class Recipe:
    def __init__(self,item,ingredients,number):
        self.item=item
        self.ingredients=ingredients
        self.number=number
    def draw(self,x,y):
        img=pygame.transform.scale(item_dict[self.item][3],(8,8))
        pixel.blit(img,(x,y))
        text = font.render(str(self.number), False,(255,255,255))
        pixel.blit(text,(x+11-(text.get_width()),y+4))

#INITIALISE RECIPES HERE
recipe_dict=[Recipe("Brick",[["Dirt",5],["Stone",2]],3),
            Recipe("Light",[["Dirt",5]],3),
            Recipe("Ladder",[["Dirt",5]],10),
            Recipe("Glass",[["Dirt",2]],10),
            Recipe("Metal",[["Iron",5]],5),
            Recipe("Chest",[["Dirt",5],["Iron",2]],1)]


    

class Item:
    def __init__(self,item):
        self.item=item
        self.count=1
class Tool(Item):
    def __init__(self,item,img):
        self.item=item
        self.health=100
        self.img=img
        self.count=1
    def draw(self,x,y):
        pixel.blit(self.img,(x,y))
class ItemBlock(Item):
    def draw(self,x,y):
        img=pygame.transform.scale(item_dict[self.item][3],(8,8))
        pixel.blit(img,(x,y))
        text = font.render(str(self.count), False,(255,255,255))
        pixel.blit(text,(x+11-(text.get_width()),y+4))
        


class ItemOther(Item):
    pass



class Inventory:
    def __init__(self):
        self.items=[Tool("Pickaxe",pickaxe),"None","None","None","None","None","None","None",
        "None","None","None","None","None","None","None","None",
        "None","None","None","None","None","None","None","None"]#Item,Count
        self.selected=0
        self.held="None"

    def add_item(self,item,number):
        for i in self.items:
            if i!="None":
                if i.item==item:
                    i.count+=number
                    return


        for i in range(len(self.items)):
            if self.items[i]=="None":#Change this depending on item
                self.items[i]=ItemBlock(item)
                self.items[i].count+=number-1
                return

    def remove_item(self,item,number):
        for i in range(len(self.items)):
            if self.items[i]!="None":
                if self.items[i].item==item:
                    self.items[i].count-=number
                    if self.items[i].count<=0:
                        self.items[i]="None"
                    return

    def update_selected(self,value):
        self.selected+=value
        if self.selected>7:
            self.selected=0
        elif self.selected<0:
            self.selected=7

    def check_item(self,item,count):
        current=0
        for i in self.items:
            if i!="None":
                if i.item==item:
                    current+=i.count
        if current>=count:
            return True
        else:
            return False


class Block:
    def __init__(self,x,y,item,listx,listy):
        self.x=x
        self.y=y
        self.item=item
        self.listx=listx
        self.listy=listy
        self.health=10
        self.max_health=10
        self.back=False
        self.passable=False
    def drawR(self):
        pygame.draw.rect(pixel,(255,0,0),(worldx+self.x,worldy+self.y,16,16),2)

    def draw(self):
        if self.item=="None":
            return
        
        
        if self.back==False:#Only process if an actual block
            #Distance from centre:
            #dist=math.sqrt((worldx+self.x-160)**2+(worldy+self.y-90)**2)
            new=item_dict[self.item][3].copy()
            if not god_mode:
                v=light_global_array[self.listx][self.listy]
                new.fill((v,v,v), special_flags=pygame.BLEND_RGB_SUB) 
            pixel.blit(new,(worldx+self.x,worldy+self.y))

            if worldx+self.x<mousex and worldx+self.x+16>mousex and worldy+self.y<mousey and worldy+self.y+16>mousey:
                #Check mouse within range
                if mousex>160-action_distance and mousex<160+action_distance and mousey>90-action_distance and mousey<90+action_distance:
                    if inventory.items[inventory.selected]!="None":
                        if mouse_down==True and inventory.items[inventory.selected].item=="Pickaxe":
                            self.health-=1*mine_mult
                            if self.health<=0:
                                if self.item=="Light":
                                    update_light_array(-150,self.listx,self.listy)
                                pygame.mixer.Sound.play(break_SOUND)
                                inventory.add_item(self.item,1)
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

                    #draw_selected(worldx+self.x,worldy+self.y,(255,255,255))
                    pygame.draw.rect(pixel,(255,255,255),(worldx+self.x,worldy+self.y,16,16),1)
        else:
            #Distance from centre:
            #dist=math.sqrt((worldx+self.x-160)**2+(worldy+self.y-90)**2)
            new=item_dict[self.item][4].copy()
            if not god_mode:
                v=light_global_array[self.listx][self.listy]
                new.fill((v,v,v), special_flags=pygame.BLEND_RGB_SUB) 
            pixel.blit(new,(worldx+self.x,worldy+self.y))

    def check_col(self):
        if self.item=="None" or self.passable==True:
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

        #Set passable here for now
        if self.item=="Light" or self.item=="Ladder":
            self.passable=True
        else:
            self.passable=False

    def set_item(self,new):
        self.item=new
        if new!="None":
            self.reset_health()
        if new=="Light":
            update_light_array(150,self.listx,self.listy)


def update_light_array(lux,x,y):
    global light_global_array
    #light_global_array[x][y]=max(0,light_global_array[x][y]-lux)
    #Do in circle surrounding from here, make it affected by walls later
    for xb in range(15):
        for yb in range(15):
            val=max(0,255-lux*8/(math.sqrt(abs(xb-7)**2+abs(yb-7)**2)+1))
            if lux>0:
                if light_global_array[x-7+xb][y+7-yb]>val:
                    light_global_array[x-7+xb][y+7-yb]=val
            else:
                light_global_array[x-7+xb][y+7-yb]=min(255,val)

    #Max distance is 4, which should be 0, exponential


def rounder(number,multiple):
    return multiple*round(number/multiple)


def draw_character():
    firsty=int((starty+worldy+122)/16)#Lighting character based on global light array
    firstx=-int((startx+worldx)/16)-1
    v=light_global_array[firstx+11][firsty-7]
    c=character.copy()
    if not god_mode:
        c.fill((v,v,v), special_flags=pygame.BLEND_RGB_SUB) 

    if direction=="right":
        pixel.blit(c,(152,82))
    else:
        rev=pygame.transform.flip(c,True,False)
        pixel.blit(rev,(152,82))


def draw_selected(x,y,colour):
    size=2
    pygame.draw.line(pixel,colour,(x-1,y-1),(x+4,y-1),size)
    pygame.draw.line(pixel,colour,(x-1,y-1),(x-1,y+4),size)

    pygame.draw.line(pixel,colour,(x+15,y-1),(x+11,y-1),size)
    pygame.draw.line(pixel,colour,(x+15,y-1),(x+15,y+4),size)

    pygame.draw.line(pixel,colour,(x-1,y+15),(x-1,y+11),size)
    pygame.draw.line(pixel,colour,(x-1,y+15),(x+4,y+15),size)

    pygame.draw.line(pixel,colour,(x+15,y+15),(x+15,y+11),size)
    pygame.draw.line(pixel,colour,(x+16,y+15),(x+11,y+15),size)


def draw_inventory():



    xSize=3
    ySize=8

    for y in range(ySize):
        start=(180-(ySize*16))/2-4
        pygame.draw.rect(pixel,(100,100,100),(5,start+y*17,16,16))
        if y==inventory.held:
            pygame.draw.rect(pixel,(255,255,255),(5,start+y*17,16,16),2)
        else:
            pygame.draw.rect(pixel,(60,60,60),(5,start+y*17,16,16),2)

        #Draw on selected
        draw_selected(5,start+inventory.selected*17,(255,255,255))
        #Add first column of items
        item=inventory.items[y]
        if item!="None":
            item.draw(9,start+y*17+4)
        if inventory_open:
            if mousex>5 and mousex<21 and mousey>start+y*17 and mousey<start+y*17+16:
                pygame.draw.rect(pixel,(255,255,255),(5,start+y*17,16,16),2)
                if item!="None":
                    text = font.render(str(item.item), False,(255,255,255))
                    pixel.blit(text,(5,158))
                if clicked:
                    pygame.mixer.Sound.play(click_SOUND)
                    if inventory.held=="None":
                        inventory.held=y
                    else:
                        temp=inventory.items[inventory.held]
                        inventory.items[inventory.held]=inventory.items[y]
                        inventory.items[y]=temp
                        inventory.held="None"
            

    if inventory_open:
        #Draw Grid
        #Text above and below
        text = font.render(str("Inventory"), False,(255,255,255))
        pixel.blit(text,(11,12))


        for x in range(xSize-1):
            for y in range(ySize):
                pygame.draw.rect(pixel,(120,120,120),(22+x*17,start+y*17,16,16))
                if inventory.held==(x+1)*8+y:
                    pygame.draw.rect(pixel,(255,255,255),(22+x*17,start+y*17,16,16),2)
                else:
                    pygame.draw.rect(pixel,(80,80,80),(22+x*17,start+y*17,16,16),2)
                item=inventory.items[(x+1)*8+y]
                if item!="None":
                    item.draw(26+x*17,start+y*17+4)

                if mousex>22+x*17 and mousex<38+x*17 and mousey>start+y*17 and mousey<start+y*17+16:
                    pygame.draw.rect(pixel,(255,255,255),(22+x*17,start+y*17,16,16),2)
                    if item!="None":
                        text = font.render(str(item.item), False,(255,255,255))
                        pixel.blit(text,(5,158))
                    if clicked:
                        pygame.mixer.Sound.play(click_SOUND)
                        if inventory.held=="None":
                            inventory.held=y+(x+1)*8
                        else:
                            temp=inventory.items[inventory.held]
                            inventory.items[inventory.held]=inventory.items[(x+1)*8+y]
                            inventory.items[(x+1)*8+y]=temp
                            inventory.held="None"

        #CRAFTING MENU
        text = font.render(str("Crafting"), False,(255,255,255))
        pixel.blit(text,(274,12))
        for r in range(len(recipe_dict)):

            pygame.draw.rect(pixel,(120,120,120),(299,start+r*17,16,16))
            itemR=recipe_dict[r].item
            recipe_dict[r].draw(303,start+r*17+4)
            #Draw each item here
            if mousex>299 and mousex<299+16 and mousey>start+r*17 and mousey<start+r*17+16:
                

                pygame.draw.rect(pixel,(255,255,255),(299,start+r*17,16,16),2)
                #Shows ingredients
                c=0
                craftable=True
                for ing in recipe_dict[r].ingredients:
                    if inventory.check_item(recipe_dict[r].ingredients[c][0],recipe_dict[r].ingredients[c][1]):
                        pygame.draw.rect(pixel,(120,120,120),(299-17*c,162,16,16))
                        pygame.draw.rect(pixel,(80,80,80),(299-17*c,162,16,16),2)
                    else:
                        pygame.draw.rect(pixel,(200,120,120),(299-17*c,162,16,16))
                        pygame.draw.rect(pixel,(120,80,80),(299-17*c,162,16,16),2)
                        craftable=False

                    orig = pygame.transform.scale(item_dict[recipe_dict[r].ingredients[c][0]][3],(8,8))
                    pixel.blit(orig,(303-17*c,166))

                    #Text for each ing
                    text = font.render(str(recipe_dict[r].ingredients[c][1]), False,(255,255,255))
                    pixel.blit(text,(314-17*c-text.get_width(),170))

                    c+=1
                text = font.render(str(itemR), False,(255,255,255))
                pixel.blit(text,(315-text.get_width()-c*17,170))



                #item.draw(293,start+r*17+4)
                if clicked==True and (craftable==True or god_mode==True):
                    #Check if player has ingredients and inv space here
                    inventory.add_item(itemR,recipe_dict[r].number)
                    if god_mode==False:
                        c=0
                        for ing in recipe_dict[r].ingredients:
                            inventory.remove_item(recipe_dict[r].ingredients[c][0],recipe_dict[r].ingredients[c][1])
                            c+=1
            else:
                pygame.draw.rect(pixel,(80,80,80),(299,start+r*17,16,16),2)




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
    if velocityy<1 and climbing:
        velocityy+=climbing_speed

def check_collisions():
    for b in block_array:
        b.check_col()

def draw_blocks():
    for b in block_array:
        b.draw()

def draw_back():
    for b in back_array:
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

def generate_back_array():
    global back_array
    back_array=[]
    firsty=int((starty+worldy+122)/16)
    firstx=-int((startx+worldx)/16)-1

    for y in range(14):
        for x in range(22):
            add=back_global_array[firstx+x][firsty-y]
            if add!=0:
                back_array.append(add)

def generate_veins(transform,total,minH,maxH,minStart,maxStart,size):
    global global_array
    for i in range(total):
        px,py=random.randint(0,blocksx-1),random.randint(minStart,maxStart)
        for i in range(size):
            px+=random.choice([-1,0,1])
            py+=random.choice([-1,0,1])
            if px<0:
                px=0
            elif px>blocksx-1:
                px=blocksx-1
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
        px,py=random.randint(0,blocksx-1),random.randint(minStart,maxStart)
        move_arrayx=[-1,0,1]
        move_arrayy=[-1,0,1]
        move_arrayx.append(random.choice(move_arrayx))
        move_arrayy.append(random.choice(move_arrayy))
        for l in range(length):
            px+=random.choice(move_arrayx)
            py+=random.choice(move_arrayy)

            if px<0:
                px=0
            elif px>blocksx-1:
                px=blocksx-1
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
            back_global_array[x][y+min].set_item(item)

    #Blending into current ground
    odds=0.9
    for y in range(8):
        odds-=0.1
        for x in range(blocksx):
            rando=random.random()
            if rando<odds:
                if global_array[x][max+y]!=0:
                    global_array[x][max+y].set_item(item)
                    back_global_array[x][max+y].set_item(item)

#For now fill space under ground level
def background():
    if worldy<-(ground_level+180):
        pixel.fill([64,41,9])
    elif worldy<-(ground_level-90):
        pygame.draw.rect(pixel,(64,41,9),(0,ground_level+90+worldy,320,300))#Y pos should be where level 1000 is

#God
def toggle_god():
    global double_jump,mine_mult,action_dist_mult,action_distance,god_mode
    if god_mode==False:
        double_jump=True
        mine_mult=100
        action_dist_mult=10
        action_distance=56*action_dist_mult
        god_mode=True
    else:
        double_jump=False
        mine_mult=1
        action_dist_mult=1
        action_distance=56*action_dist_mult
        god_mode=False

def check_action():
    #Place Item here
    #Use maths to calculate where to place new block and use inventory selection to place
    #use mousex,mousey
    global global_array
    if inventory.items[inventory.selected]!="None":
        if inventory.items[inventory.selected].item!="Pickaxe":#Remove this and replace with blocks/item system
            if mousex>160-action_distance and mousex<160+action_distance and mousey>90-action_distance and mousey<90+action_distance:
                x=int((mousex-worldx-startx)/16)
                y=int(-(mousey-worldy-starty-98)/16)+1

                #Get item and place if possible, and not over character
                if global_array[x][y].item=="None":
                    #Check mouse not over character
                    if not (mousex>152 and mousex<168 and mousey>82 and mousey<98):
                        if inventory.items[inventory.selected]!="None":
                            global_array[x][y].set_item(inventory.items[inventory.selected].item)
                            inventory.remove_item(inventory.items[inventory.selected].item,1)


def check_ladder():
    #143 IS BLOCK PLAYER IS AT
    if block_array[143].item=="Ladder":
        return True
    else:
        return False

#Create blocks from bottom, with semi random heights
global_array=[]
back_global_array=[]
light_global_array=[]
for x in range(blocksx):
    new=[]
    newB=[]
    newL=[]
    for y in range(blocksy):
        new.append(Block(startx+worldx+x*16,worldy+starty-(y*16)+98,"None",x,y))
        newB.append(Block(startx+worldx+x*16,worldy+starty-(y*16)+98,"None",x,y))
        if int((count-y)*10)>0:
            newL.append(min(int((count-y)*10),255))
        else:
            newL.append(0)
    global_array.append(new)
    back_global_array.append(newB)
    light_global_array.append(newL)

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
        back_global_array[x][y].set_item("Dirt")
    global_array[x][count].set_item("Grass")
    #Set all light above here to higher etc


#Generate veins and caves trans,total,min,max,size
##Iron,Lead,Copper,Gold

#Stone layer
create_layer(0,1000,"Stone")
"""
back_global_array=copy.deepcopy(global_array)
"""
for i in back_global_array:
    for b in i:
        b.back=True

generate_caves(int(blocksx),20,1050,100,1000,300,10)#LONG CAVES
generate_veins("None",int(blocksx),0,1050,0,950,200)#HOLLOW CAVES

generate_veins("Dirt",int(blocksx*2),0,1000,0,900,200)
generate_veins("Stone",int(blocksx/2),950,1050,950,1030,100)
generate_veins("Marble",int(blocksx/20),0,1000,0,700,500)
generate_veins("Iron",int(blocksx),0,1000,0,980,20)
generate_veins("Lead",int(blocksx),0,1000,0,980,20)
generate_veins("Copper",int(blocksx),0,1000,0,950,10)
generate_veins("Gold",int(blocksx),0,500,0,480,10)
generate_veins("Diamond",int(blocksx/10),0,200,0,200,5)

remove_lone_blocks()


block_array=[]
back_array=[]
inventory=Inventory()

while True:
    pixel.fill([173,216,230])

    if right_mouse_down or right_clicked:
        check_action()
    if climbing==True:
        if check_ladder()==False:
            climbing_speed=0
        else:
            climbing_speed=1

    generate_block_array()
    generate_back_array()


    check_collisions()
    move_character()
    background()
    draw_back()
    draw_blocks()
    draw_character()
    check_ladder()

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
            elif event.key==pygame.K_w:
                climbing=False
                climbing_speed=1
        elif event.type==pygame.KEYDOWN:
            if event.key==pygame.K_d:
                velocityx-=speed
                direction="right"
            elif event.key==pygame.K_a:
                velocityx+=speed
                direction="left"
            elif event.key==pygame.K_w:
                if check_ladder()==True:
                    climbing=True
            elif event.key==pygame.K_r:
                worldx,worldy=0,0
            elif event.key==pygame.K_e:
                inventory_open=not inventory_open
            elif event.key==pygame.K_g:
                toggle_god()
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
            elif event.key==pygame.K_SPACE:
                if velocityy==0 or double_jump:
                    velocityy=jump_velocity
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
#Added new inventory 15/06
#Added texture support 15/06
#Added back texture support 15/06
#Added ability to organically change world size 15/06
#ADDED LIGHTING FEATURE! 15/06
#Added click sound 15/06
#Added torches and lighting of character 16/06
#Added brick item 16/06
#Added crafting menu 16/06
#Added text for crafting menu 16/06
#Added ladders and passable attribute to block 16/06
#Ladder climbing 16/06
#Made lamps nicer 16/06
#Made inventory look better 17/06
#Made crafting class and now it works! 17/06
#Added more craftables 21/06


#Make climbing smoother
#Add colour to lights
#Make lamps breaking work!
#Add ladder speed
#Add god mode lighting
#Make lighting actually work well
#Fix line glitch at around 1050
#Need to cancel held item when closed or clicked off
#Only draw back when visible
#Add items dropping and picking them up
#Add usable objects - chest, door, hatch, ladder
#Binning items
#popout animation for inv








#Plan for V0.4 Combat
#Add health system
#Add enemies
#Add weapons
#Add armour
#World edges

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










    
