import pygame
import random
from pygame.locals import *

# make this not global
class Dummy:
    pass
game_fonts = Dummy()
game_fonts.default = None


class Label:
    def __init__(self, text):
        self.change_text(text)
        
    def change_text(self, text):
        self.raw_text = text
        self.text = game_fonts.default.render(self.raw_text, 1, pygame.Color("White"))
        
    def anchor(self, x, y):
        self.x, self.y = x, y
        size = w, h = self.text.get_size()
        self.w, self.h = w, h
        self.rect = pygame.Rect(x, y, w, h)
 
    def display(self, surface):
        pygame.draw.rect(surface, pygame.Color("Black"), self.rect)
        surface.blit(self.text, (self.x,self.y))
        
class Menu:
    def __init__(self, menu_data):
        self._menu_data = menu_data
        self._y_offset = 0
        self.label_up = Label("/\\")
        self.label_down = Label("\\/")
        self.expanded = set([()])
            
    def resolve_path(self, menu_path):
        cur_d  = self._menu_data
        while menu_path:
            next_key, *menu_path = menu_path
            cur_d = cur_d[next_key]
        return cur_d
            
    def expandable(self, menu_path):
        value = self.resolve_path(menu_path)
        return value is not None
        
    def expand(self, menu_path):
        self.expanded.add(menu_path)
                
    def collapse(self, menu_path):
        self.expanded.remove(menu_path)
    
    def visible_paths(self):
        visible = []
        to_expand = [()]
        while to_expand:
            cur_path = to_expand.pop(0)
            if cur_path not in self.expanded:
                continue
            d = self.resolve_path(cur_path)
            if d:
                for key in d.keys():   
                    next_path = cur_path + (key,)
                    visible.append(next_path)
                    to_expand.append(next_path)
        return visible
        
    def menu_up(self):
        if self._y_offset > 0:
            self._y_offset = self._y_offset - 1
            
    def menu_down(self):
        if self._y_offset < len(self.visible_items):
            self._y_offset = self._y_offset + 1
        
    def anchor(self, x, y, w, h):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.menu_rect = pygame.Rect(x, y, w, h)
        self.label_up.anchor(x,y)
        self.label_down.anchor(x,y+h-self.label_up.h)
        self.menu_item_height = self.label_up.h * 1.1 # 10 percent padding)
        
    def redraw_labels(self):
        num_items = int(self.h/self.menu_item_height)
        self.menu_item_labels = {}
        self.visible_items = self.visible_paths()
        on_screen_items = self.visible_items[self._y_offset:self._y_offset+num_items]
        menu_y = self.y
        menu_x = self.x+self.label_up.w
        for menu_path in on_screen_items:
            value = self.resolve_path(menu_path)
            text = menu_path[-1]
            indent = 5 * len(menu_path)
            expand_icon = "   "
            if value and menu_path in self.expanded:
                expand_icon = "-  "
            elif value:
                expand_icon = "+ "
            text = expand_icon + text
            l = Label(text)
            l.anchor(menu_x+indent, menu_y)
            menu_y += self.menu_item_height
            self.menu_item_labels[l] = menu_path
        
    def display(self, surface):
        pygame.draw.rect(surface, pygame.Color("Black"), self.menu_rect)
        self.label_up.display(surface)
        self.label_down.display(surface)
        self.redraw_labels()
        for label in self.menu_item_labels.keys():
            label.display(surface)
            
    def process_click(self, mx, my):
        if self.label_up.rect.collidepoint(mx, my):
            return ("menu_up",)
        elif self.label_down.rect.collidepoint(mx, my):
            return ("menu_down",)
        for label in self.menu_item_labels.keys():
            if label.rect.collidepoint(mx, my):
                menu_path = self.menu_item_labels[label]
                value = self.resolve_path(menu_path)
                if value and menu_path in self.expanded:
                    return ("collapse", menu_path)
                elif value and menu_path not in self.expanded:
                    return ("expand", menu_path)
                else:
                    return ("select", menu_path)
        return None
        
    
mhealth = 100

def game_loop():
    global mhealth
    pygame.init()
    game_fonts.default = pygame.font.SysFont("Arial", 20)
    game_fonts.events = pygame.font.SysFont("Arial", 35)
     
    HEIGHT = 500
    WIDTH = 750
    menu_height = int(.2*HEIGHT) # 20% of screen
    
    bg = pygame.image.load("../assets/backgrounds/forest_with_stairs_background.jpg")
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT-menu_height))
     
    displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game")
    displaysurface.blit(bg, [0,0])
    
    monster1_sprite = pygame.image.load("../assets/sprites/monster_sprite_001.png")
    hero_sprite_standing = pygame.image.load("../assets/sprites/hero_sprite_standing.png")
    hero_sprite_standing = pygame.transform.scale(hero_sprite_standing, (170,170))
    hero_sprite_attack1 = pygame.image.load("../assets/sprites/hero_sprite_attack1.png")
    hero_sprite_attack1 = pygame.transform.scale(hero_sprite_attack1, (170, 170))
    
    player_menu_data = {
        "encounter": {
            "fighter": {
                "melee": {
                    "sword":{
                        "attack 1": None
                        }
                    }
                }
            , "monster": {
                "health": {
                    str(mhealth): None}
                }
            }
        }
    """
    player_menu_data = {"encounter": {"fighter": {"melee": {"sword": {"attack 1":None}}}, "monster": {health: {v1: None}}}}
    """
    player_menu_screen = Menu(player_menu_data)
    player_menu_screen.anchor(0, HEIGHT-menu_height, WIDTH, menu_height)
    
    clock = pygame.time.Clock()
    
    hattack1 = 5
    hattack2 = 0    
    running = True
    while running:
        
        displaysurface.blit(bg, [0,0])
        player_menu_screen.display(displaysurface)
        if hattack2:
            displaysurface.blit(hero_sprite_attack1, [350, 175])
            if hattack1 < 10:
                displaysurface.blit(game_fonts.events.render("-" + str(hattack1), 1, pygame.Color(79, 2, 2)), [495, (190 - (60 - (3*hattack2)))])
            if hattack1 >= 10:
                displaysurface.blit(game_fonts.events.render("-" + str(hattack1), 1, pygame.Color(14, 97, 1)), [485, (190 - (60 - (3*hattack2)))])
            hattack2 = hattack2 - 1
        else:
            displaysurface.blit(hero_sprite_standing, [50, 175])
        if mhealth > 0:
            displaysurface.blit(monster1_sprite, [500,175]) 
        else:
            print("You win!")
            running = False
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    mx, my = pygame.mouse.get_pos()
                    result = player_menu_screen.process_click(mx, my)
                    #print(result)
                    if result is not None:
                        if result[0] == "expand":
                            player_menu_screen.expand(result[1])
                        if result[0] == "collapse":
                            player_menu_screen.collapse(result[1])
                        if result[0] == "menu_up":
                            player_menu_screen.menu_up()
                        if result[0] == "menu_down":
                            player_menu_screen.menu_down()
                        if result[0] == "select":
                            if result[1][-1] == "attack 1":
                                #hattack1 = 5
                                hattack1 = random.randint(1, 20)
                                mhealth -= hattack1
                                hattack2 = 20
                                #player_menu_data
        """mhealth -= hattack1
        hattack1 = 0"""
        #print(mhealth)
        clock.tick(100)
    
if __name__=="__main__":
    game_loop()