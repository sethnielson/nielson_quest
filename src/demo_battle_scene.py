import pygame
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
        

def game_loop():
    pygame.init()
    game_fonts.default = pygame.font.SysFont("Arial", 20)
     
    HEIGHT = 500
    WIDTH = 750
    menu_height = int(.2*HEIGHT) # 20% of screen
    
    bg = pygame.image.load("../assets/backgrounds/forest_with_stairs_background.jpg")
    bg = pygame.transform.scale(bg, (WIDTH, HEIGHT-menu_height))
     
    displaysurface = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Game")
    displaysurface.blit(bg, [0,0])
    
    monster1_sprite = pygame.image.load("../assets/sprites/monster_sprite_001.png")
    monster1_sprite90 = pygame.image.load("../assets/sprites/monster_sprite_001_90.png")
    monster1_sprite180 = pygame.image.load("../assets/sprites/monster_sprite_001_180.png")
    monster1_sprite270 = pygame.image.load("../assets/sprites/monster_sprite_001_270.png")
    hero_sprite_standing = pygame.image.load("../assets/sprites/hero_sprite_standing.png")
    hero_sprite_standing = pygame.transform.scale(hero_sprite_standing, (170,170))
    hero_sprite_attack1 = pygame.image.load("../assets/sprites/hero_sprite_attack1.png")
    hero_sprite_attack1 = pygame.transform.scale(hero_sprite_attack1, (170, 170))
    
    player_menu_data = {
        "Party": {
            "Urmahm": {
                "Melee": {
                    "Slash Attack": None
                    }
                }
            }
        }
        
    player_menu_screen = Menu(player_menu_data)
    player_menu_screen.anchor(0, HEIGHT-menu_height, WIDTH, menu_height)
    
    enemy_menu_data = {
        "Party": {
            "Ground Dragon": {
                "Melee": {
                    "Roll Attack": None
                    }
                }
            }
        }
    enemy_menu_screen = Menu(enemy_menu_data)
    enemy_menu_screen.anchor(450, HEIGHT-menu_height, WIDTH, menu_height)
    
    clock = pygame.time.Clock()
    
    running = True
    hattack = 0
    gdattack = 0
    while running:
        displaysurface.blit(bg, [0,0])
        player_menu_screen.display(displaysurface)
        enemy_menu_screen.display(displaysurface)
        if hattack>28:
            displaysurface.blit(hero_sprite_standing, [110, 125])
            hattack = hattack - 1
        elif hattack>24:
            displaysurface.blit(hero_sprite_standing, [170, 75])
            hattack = hattack - 1
        elif hattack>20:
            displaysurface.blit(hero_sprite_attack1, [230, 25])
            hattack = hattack - 1
        elif hattack>16:
            displaysurface.blit(hero_sprite_attack1, [290, 100])
            hattack = hattack - 1
        elif hattack>12:
            displaysurface.blit(hero_sprite_attack1, [350, 175])
            hattack = hattack - 1
        elif hattack>8:
            displaysurface.blit(hero_sprite_standing, [275, 175])
            hattack = hattack - 1
        elif hattack >4:
            displaysurface.blit(hero_sprite_standing, [200, 175])
            hattack = hattack - 1
        elif hattack>0:
            displaysurface.blit(hero_sprite_standing, [125, 175])
        ##Dragon attack
        if gdattack>28:
            displaysurface.blit(monster1_sprite90, [430, 200])
            gdattack = gdattack - 1
        elif gdattack>24:
            displaysurface.blit(monster1_sprite90, [360, 250])
            gdattack = gdattack - 1
        elif gdattack>20:
            displaysurface.blit(monster1_sprite180, [290, 275])
            gdattack = gdattack - 1
        elif gdattack>16:
            displaysurface.blit(monster1_sprite270, [220, 225])
            gdattack = gdattack - 1
        elif gdattack>12:
            displaysurface.blit(monster1_sprite, [150, 175])
            gdattack = gdattack - 1
        elif gdattack>8:
            displaysurface.blit(monster1_sprite, [230, 175])
            gdattack = gdattack - 1
        elif gdattack>4:
            displaysurface.blit(monster1_sprite, [320, 175])
            gdattack = gdattack - 1
        elif gdattack>0:
            displaysurface.blit(monster1_sprite, [410, 175])
            gdattack = gdattack - 1
        if hattack == 0:
            displaysurface.blit(hero_sprite_standing, [50, 175])
        if gdattack == 0:
            displaysurface.blit(monster1_sprite, [500,175])
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
                            if result[1][-1] == "Dab Attack":
                                hattack = 32
                    result = enemy_menu_screen.process_click(mx,my)
                    if result is not None:
                        if result[0] == "expand":
                            enemy_menu_screen.expand(result[1])
                        if result[0] == "collapse":
                            enemy_menu_screen.collapse(result[1])
                        if result[0] == "menu_up":
                            enemy_menu_screen.menu_up()
                        if result[0] == "menu_down":
                            enemy_menu_screen.menu_down()
                        if result[0] == "select":
                            if result[1][-1] == "Roll Attack":
                                gdattack = 32
        clock.tick(100)
    
if __name__=="__main__":
    game_loop()