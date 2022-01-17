import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
import pygame , random, math , os

WIDTH, HEIGHT = 1200,800

green = (0,255,0)
red = (255,0,0)
blue = (0,0,255)
purple = (128, 0, 128)
white = (255,255,255)

max_apple = 200
obs_radius = 100

background = os.path.join('background.jpg')

class Snake(object):
    
    def __init__(self,pos_x,pos_y):
        # init snake body with 4 parts
        self.body = [(pos_x,pos_y), (pos_x,pos_y-10),(pos_x,pos_y-20),(pos_x,pos_y-30)]
        self.direction = 1    
        # list to save snake body parts as sprite (to check collision)
        self.group = pygame.sprite.Group()
        self.direction_change = True
        self.aim_loc = []
        
    def move(self, x, y, speed):
        
        if 25 <= self.body[0][0] <= WIDTH-25 and 25<= self.body[0][1] <= HEIGHT-25 :
            del self.body[-1]
            self.body.insert(0,(self.body[0][0]+x  , self.body[0][1]+y)) 
            if speed:
                del self.body[-1]
                self.body.insert(0,(self.body[0][0]+x  , self.body[0][1]+y)) 
            return False
        else: 
            return True
            
            

    def build_group(self):
        self.group = pygame.sprite.Group()
        head_sprite = pygame.sprite.Sprite()
        head_flag = False # to get only the head
        for loc in self.body: # make a sprite of all the body parts
            sprite_rect = pygame.sprite.Sprite()
            sprite_rect.image = pygame.Surface((30, 30),pygame.SRCALPHA)
            pygame.draw.circle(sprite_rect.image, green , (15, 15), 15,2)
            sprite_rect.rect = pygame.Rect(loc[0],loc[1], 30, 30)
            # 
            if not head_flag :
                head_sprite = sprite_rect
                head_flag = True
                
            self.group.add(sprite_rect)
            
        return  head_sprite
        
class Apple(object):
    def __init__(self,pos_x,pos_y):
        self.x , self.y = pos_x,pos_y

    
class Snake_game(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        """
        Every environment should be derived from gym.Env and at least contain the variables observation_space and action_space 
        specifying the type of possible observations and actions using spaces.Box or spaces.Discrete.
        Example:
        >>> EnvTest = FooEnv()
        >>> EnvTest.observation_space=spaces.Box(low=-1, high=1, shape=(3,4))
        >>> EnvTest.action_space=spaces.Discrete(2)
        """
        # Define a 2-D observation space
        self.observation_shape = (12, 3) # num of apple, num of body, isWall in each slice
        self.observation_space = spaces.Box(low = np.zeros(self.observation_shape), 
                                            high = np.ones(self.observation_shape),
                                            dtype = np.int)
        
        #Define action space
        self.action_space = spaces.Discrete(24)
        
        
        self.initialize_value()
        
        
        
        
    def dir_to_xy(self,direction):
        
        if direction == 0:
            return 3,0
        if direction == 1:
            return 2,-1
        if direction == 2:
            return 1,-2
        if direction == 3:
            return 0,-3
        if direction == 4:
            return -1,-2
        if direction == 5:
            return -2,-1
        if direction == 6:
            return -3,0
        if direction == 7:
            return -2,1
        if direction == 8:
            return -1,2
        if direction == 9:
            return 0,3
        if direction == 10:
            return 1,2
        if direction == 11:
            return 2,1
        else: 
            return random.randrange(-3,3), random.randrange(-3,3)   
    
    

    
    def manage_oppos(self):
        
        for i ,snake in enumerate(self.opponnents):
            
            head_x, head_y = snake.body[0][0] ,snake.body[0][1]
            if 40 <= head_x <= WIDTH-40 and 40<= head_y <= HEIGHT-40 :
                
                if snake.direction_change:
                    snake.direction_change = False
                    t,n = self.dir_to_xy(self.get_nearest_slice(head_x,head_y) )
                    snake.aim_loc = [t,n]

                snake.move(snake.aim_loc[0],snake.aim_loc[1],random.randrange(0,2))
                
            else :
                t,n = self.dir_to_xy(self.get_nearest_slice(head_x,head_y) )
                snake.aim_loc = [t,n]
                snake.move(snake.aim_loc[0],snake.aim_loc[1],random.randrange(0,2))
                
                snake.direction_change = False
                                 
             #check hiting the apple
            head = pygame.sprite.Sprite()
            head.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            head.rect = pygame.Rect(head_x,head_y, 30, 30)

            for apple in self.apple_group:
                if self.checkCollision(head,apple):
                    self.apple_group.remove(apple)
                    self.add_apple()
                    self.grow_snake(snake)                     
                    snake.direction_change = True         
                    
            #check hit the main snake
            for part in self.snake.group:
                if self.checkCollision(head, part):
                    
                    print("snake : ", i , "hit you")
                    self.reward += 20
                    for i in range(len(snake.body)//4):
                        loc = random.choice(snake.body)
                        self.add_apple(locx = loc[0] , locy = loc[1] )
                        
                    if snake in self.opponnents : 
                        self.opponnents.remove(snake)
                        self.build_snake()
          
    
    def step(self, action):
        """
        This method is the primary interface between environment and agent.
        Paramters: 
            action: int
                    the index of the respective action (if action space is discrete)
        Returns:
            output: (array, float, bool)
                    information provided by the environment about its current state:
                    (observation, reward, done)
        """
        
#         assert self.action_space.contains(action) # check if the action is legit
        
        
        self.done = False
        
        self.reward += 1 # reward 1 for each step alive
   
        direction, speed = action//2,action %2
        # 12 slices
        self.direction = direction
        
        x,y = self.dir_to_xy(direction)
        self.done = self.snake.move(x,y,speed)
    
        self.check_body_hit()
        self.check_apple_hit()
        
        self.manage_oppos()
        
        return self.get_obs() , self.reward , self.done, {}
    
    
    
    
    
    
    
    
    
    
    def get_nearest_slice(self,locx, locy):
        
        min_d = 30
        nearest_apple_xy = next((apple.rect.center for apple in self.apple_group if self.get_distance_loc(locx, locy, apple.rect.centerx, apple.rect.centery) <min_d),
                                (WIDTH//2,HEIGHT//2))
        return self.get_slice(locx,locy,nearest_apple_xy[0], nearest_apple_xy[1]) 
       
    
    def build_oppo_group(self):
        
        self.opponent_group = pygame.sprite.Group()
        for snake in self.opponnents:
            for loc in snake.body:
                sprite_rect = pygame.sprite.Sprite()
                sprite_rect.image = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.circle(sprite_rect.image, blue , (15, 15), 15 ,2)
                sprite_rect.rect = pygame.Rect(loc[0],loc[1], 30, 30)
                self.opponent_group.add(sprite_rect)
        return self.opponent_group
    
    
    def get_slice(self, sprite1_x, sprite1_y, sprite2_x,sprite2_y):
        degree = math.degrees(math.atan2(sprite1_x-sprite2_x, sprite1_y-sprite2_y))
        if degree > 0 and degree < 30 :
            return 3
        elif degree > 30 and degree < 60 :
            return 4
        elif degree > 60 and degree < 90 :
            return 5
        elif degree > 90 and degree < 120 :
            return 6
        elif degree > 120 and degree < 150 :
            return 7
        elif degree > 150 and degree < 180 :
            return 8
        elif degree > -30 and degree < 0 :
            return 2
        elif degree > -60 and degree < -30 :
            return 1
        elif degree > -90 and degree < -60 :
            return 0
        elif degree > -120 and degree < -90 :
            return 11
        elif degree > -150 and degree < -120 :
            return 10
        elif degree > -180 and degree < -150 :
            return 9
        else : 
            return self.snake.direction
        
    
    def get_distance(self, sprite1 ,sprite2):
        dist = math.sqrt((sprite1.rect.center[0]-sprite2.rect.center[0])**2+(sprite1.rect.center[1]-sprite2.rect.center[1])**2) 
        return int(dist)
    def get_distance_loc(self, locx1,locy1,locx2,locy2):
        dist = math.sqrt((locy2-locy1)**2+(locx2-locx1)**2)
        return dist
    
    def get_obs(self):
        
        obs = np.zeros((12,3))
        head = self.snake.build_group()
        
        # check for apple 
        for apple in self.apple_group:
            if self.get_distance(head,apple) < obs_radius:
                slice_num = self.get_slice(head.rect.x, head.rect.y, apple.rect.centerx,apple.rect.centery)
                obs[slice_num,0] = 1
                
        #check for wall 
        head_x , head_y = head.rect.centerx ,head.rect.centery
        
        if head_y < obs_radius and head_y > math.sqrt(3)* obs_radius /2:
            obs[2:4,2] = 1 
        if head_y < math.sqrt(3)* obs_radius /2 and head_y > obs_radius/2:
            obs[1:5,2] = 1
        if head_y < obs_radius/2 : 
            obs[0:6,2] = 1
        if head_x < obs_radius and head_x > math.sqrt(3)* obs_radius /2:
            obs[5:7,2] = 1
        if head_x < math.sqrt(3)* obs_radius /2 and head_x > obs_radius/2:
            obs[4:8,2] = 1
        if head_x < obs_radius/2 : 
            obs[3:9,2] = 1 
        if (HEIGHT - head_y) < obs_radius and  (HEIGHT - head_y) >   math.sqrt(3)* obs_radius /2 : 
            obs[8:10,2] = 1
        if (HEIGHT - head_y) < math.sqrt(3)* obs_radius /2 and (HEIGHT - head_y) > obs_radius/2:
            obs[7:11,2] = 1
        if (HEIGHT - head_y) < obs_radius/2 : 
            obs[6:12,2] = 1
        if (WIDTH-head_x)  < obs_radius and (WIDTH-head_x) > math.sqrt(3)* obs_radius / 2 : 
            obs[0,2] , obs[11,2] = 1, 1
        if (WIDTH-head_x) < math.sqrt(3)* obs_radius /2 and (WIDTH-head_x) > obs_radius/2 :
            obs[0:2,2] , obs[10:12,2] = 1, 1
        if (WIDTH-head_x) <  obs_radius/2 :
            obs[0:3,2] , obs[9:12,2] = 1, 1
            
        #check for opponent
        for sprite in self.opponent_group:
            if self.get_distance(head,sprite) < obs_radius:
                slice_num = self.get_slice(head.rect.centerx, head.rect.centery , sprite.rect.centerx,sprite.rect.centery)
                obs[slice_num,1] = 1
                
                
        return obs
                
        
    
    def checkCollision(self,sprite1, sprite2):
        col = pygame.sprite.collide_rect(sprite1, sprite2)
        
        return col

    def check_body_hit(self):
        head = self.snake.build_group()
        all_parts = self.snake.group
        all_parts.remove(head)
#         for elm in all_parts:
#             if self.checkCollision(head,elm):
#                 print('self body collision')
#                 self.reward -= 100
#                 self.done = True
               
        self.build_oppo_group()
        
        for elm in self.opponent_group:
            if self.checkCollision(head,elm):
                print('opponent collision')
                self.reward -= 100
                self.done = True
                print(self.reward)
                break
    
    
    
    def build_snake(self):
        oppo_snake = Snake(random.randrange(WIDTH),random.randrange(HEIGHT))
        self.opponnents.append(oppo_snake)
    
    
    def add_apple(self, locx = random.randrange(WIDTH), locy = random.randrange(HEIGHT)):
        
        apple_rect = pygame.sprite.Sprite()
        apple_rect.image = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.circle(apple_rect.image, white , (2, 2), 2)
        apple_rect.rect = pygame.Rect(locx,locy, 4, 4)
        self.apple_group.add(apple_rect)
        
        
    def grow_snake(self,snake):
        new_x, new_y = 2*snake.body[-1][0] - snake.body[-2][0] , 2*snake.body[-1][1] - snake.body[-2][1]
        snake.body.append([new_x,new_y])
        
    def check_apple_hit(self):
        head = self.snake.build_group()
        for apple in self.apple_group:
            if self.checkCollision(head,apple):
                self.reward += 5 
                self.apple_group.remove(apple)
                self.add_apple()
                self.grow_snake(self.snake)
                

    def reset(self):
        """
        This method resets the environment to its initial values.
        Returns:
            observation:    array
                            the initial state of the environment
        """
        self.initialize_value()
        return self.get_obs()
        

    def get_action(self):
        mouse_x ,mouse_y = pygame.mouse.get_pos()
        head = self.snake.build_group()
        speed = pygame.mouse.get_pressed()[0]  #This returns a tuple in the form: (leftclick, middleclick, rightclick)
        
        return self.get_slice(head.rect.centerx,head.rect.centery , mouse_x, mouse_y) *2 + speed
    
    def initialize_value(self):
        pygame.init()
        self.fps = 30  # frame rate
        self.clock = pygame.time.Clock()
        self.world = pygame.display.set_mode([WIDTH, HEIGHT])
        
        self.elements = []
        self.reward = 0
        self.total = 0
        self.snake = Snake(200,200)
        self.apple_group = pygame.sprite.Group()# to group all the apples 
        
        self.backdrop = pygame.transform.scale(pygame.image.load(background), (WIDTH, HEIGHT))
        self.backdropbox = self.world.get_rect()
        
        for i in range(max_apple):
            apple = Apple(random.randrange(WIDTH),random.randrange(HEIGHT))
            
            sprite_apple = pygame.sprite.Sprite()
            sprite_apple.image = pygame.Surface((4, 4),pygame.SRCALPHA)
            pygame.draw.circle(sprite_apple.image, white , (2, 2), 2)
            sprite_apple.rect = pygame.Rect(apple.x,apple.y, 4, 4)
            
            self.apple_group.add(sprite_apple)
            
        self.opponnents = []
        for i in range(3): # puts 3 snakes 
            self.build_snake()
        self.opponent_group = pygame.sprite.Group()# to group all the apponent 
        
        
        self.done = False
        
    def render(self, mode='human', close=False):
        """
        This methods provides the option to render the environment's behavior to a window 
        which should be readable to the human eye if mode is set to 'human'.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                self.done = True
                sys.exit()
                
        self.world.blit(self.backdrop, self.backdropbox)
        self.snake.group.draw(self.world)
        self.apple_group.draw(self.world)
        self.opponent_group.draw(self.world)
        pygame.display.flip()
        self.clock.tick(self.fps)
 

    def close(self):
        """
        This method provides the user with the option to perform any necessary cleanup.
        """
        pygame.display.quit()
        pygame.quit()


if __name__ == '__main__':
    # https://stackoverflow.com/questions/58974034/pygame-and-open-ai-implementation
    game = Snake_game()
    loop = 0
    while not game.done:
        loop += 1
        actions = game.get_action()
        print(actions)
        game.step(action=actions)

        if loop % 1 == 0:
            game.render()
    game.close()