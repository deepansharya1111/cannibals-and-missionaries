import pygame
import sys
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class LakeCrossingGame:
    def __init__(self):
        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Lake Crossing Game")
        
        self.reset_game()
        
        self.font = pygame.font.Font(None, 36)
        self.button_font = pygame.font.Font(None, 24)  # Smaller font for buttons
        self.load_images()
        self.create_buttons()

    def reset_game(self):
        self.left_shore = {"priests": 3, "carnivores": 3}
        self.right_shore = {"priests": 0, "carnivores": 0}
        self.boat_position = "left"
        self.boat = {"priests": 0, "carnivores": 0}
        self.moves = 0
        self.boat_x = 200
        self.boat_speed = 5
        self.moving_boat = False
        self.game_over = False
        self.win = False

    def load_images(self):
        self.background = pygame.transform.scale(pygame.image.load(resource_path("background.png")).convert(), (self.width, self.height))
        self.priest_img = self.load_and_scale("priest.png", (50, 50))
        self.carnivore_img = self.load_and_scale("carnivore.png", (50, 50))
        self.boat_img = self.load_and_scale("boat.png", (100, 60))
        self.button_img = self.load_and_scale("button.png", (120, 50))

    def load_and_scale(self, image_name, size):
        return pygame.transform.scale(pygame.image.load(resource_path(image_name)).convert_alpha(), size)

    def create_buttons(self):
        self.move_boat_button = pygame.Rect(340, 20, 120, 50)
        self.try_again_button = pygame.Rect(250, 300, 120, 50)
        self.end_game_button = pygame.Rect(430, 300, 120, 50)

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        
        self.draw_shore(self.left_shore, 50, True)
        self.draw_shore(self.right_shore, 700, False)
        
        self.screen.blit(self.boat_img, (self.boat_x, 500))
        
        for i, character in enumerate(["carnivores", "priests"]):
            for j in range(self.boat[character]):
                self.screen.blit(self.carnivore_img if character == "carnivores" else self.priest_img,
                                 (self.boat_x + 10 + j * 55, 460 + i * 50))
        
        self.draw_button(self.move_boat_button, "Move Boat")
        
        moves_text = self.font.render(f"Moves: {self.moves}", True, (255, 255, 255))
        self.screen.blit(moves_text, (10, 10))
        
        if self.game_over:
            print("Drawing game over screen")  # Debug print
            self.draw_game_over_screen()
        
        pygame.display.flip()

    def draw_shore(self, shore, x, is_left):
        for i, character in enumerate(["carnivores", "priests"]):
            for j in range(shore[character]):
                if is_left:
                    pos_x = x - 30 + j * 60  # Moved left side sprites 30 pixels to the left
                else:
                    pos_x = x + 100 - (j + 1) * 60
                self.screen.blit(self.carnivore_img if character == "carnivores" else self.priest_img,
                                 (pos_x, 400 + i * 60))

    def draw_button(self, button_rect, text):
        self.screen.blit(self.button_img, button_rect)
        text_surf = self.button_font.render(text, True, (255, 255, 255))  # White text
        text_rect = text_surf.get_rect(center=button_rect.center)
        self.screen.blit(text_surf, text_rect)

    def draw_game_over_screen(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        if self.win:
            text = self.font.render(f"Congratulations! You've won in {self.moves} moves.", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.width // 2, 200))
            self.screen.blit(text, text_rect)
            
            play_again_button = pygame.Rect(0, 0, 120, 50)
            play_again_button.center = (self.width // 2, 300)  # Centered and moved down by 150 pixels
            self.draw_button(play_again_button, "Play Again")
            self.try_again_button = play_again_button  # Update the button rect for click detection
        else:
            text = self.font.render("Game over! The carnivores have eaten the priests.", True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.width // 2, 200))
            self.screen.blit(text, text_rect)
            
            self.draw_button(self.try_again_button, "Try Again")
            self.draw_button(self.end_game_button, "End Game")

    def handle_click(self, pos):
        x, y = pos
        if self.game_over:
            if self.try_again_button.collidepoint(pos):
                self.reset_game()
            elif self.end_game_button.collidepoint(pos) and not self.win:
                pygame.quit()
                sys.exit()
        else:
            if self.move_boat_button.collidepoint(pos) and not self.moving_boat:
                self.start_boat_movement()
            else:
                self.handle_character_click(x, y)

    def handle_character_click(self, x, y):
        shore = self.left_shore if self.boat_position == "left" else self.right_shore
        shore_x = 20 if self.boat_position == "left" else 800  # Adjusted left shore x to match new position
        boat_chars = sum(self.boat.values())

        print(f"Click at ({x}, {y})")  # Debug print

        # Check if clicking on the boat
        if self.boat_x < x < self.boat_x + 100 and 460 < y < 560:
            print("Clicked on boat")  # Debug print
            if 460 < y < 510 and self.boat["carnivores"] > 0:
                self.move_character("carnivores", from_boat=True)
            elif 510 < y < 560 and self.boat["priests"] > 0:
                self.move_character("priests", from_boat=True)
        # Check if clicking on the shore
        else:
            shore_width = 210  # Increased to account for the wider clickable area on the left
            shore_start = shore_x - shore_width if self.boat_position == "right" else shore_x
            shore_end = shore_start + shore_width

            print(f"Shore area: {shore_start} to {shore_end}")  # Debug print
            
            if shore_start <= x <= shore_end:
                print("Clicked on shore")  # Debug print
                if 400 <= y < 450 and shore["carnivores"] > 0 and boat_chars < 2:
                    self.move_character("carnivores", from_boat=False)
                elif 450 <= y < 500 and shore["priests"] > 0 and boat_chars < 2:
                    self.move_character("priests", from_boat=False)

        print(f"After click - Boat: {self.boat}, Left Shore: {self.left_shore}, Right Shore: {self.right_shore}")  # Debug print

    def move_character(self, character, from_boat=False):
        shore = self.left_shore if self.boat_position == "left" else self.right_shore
        if from_boat:
            if self.boat[character] > 0:
                self.boat[character] -= 1
                shore[character] += 1
                print(f"Moved {character} from boat to shore")  # Debug print
        else:
            if shore[character] > 0 and sum(self.boat.values()) < 2:
                shore[character] -= 1
                self.boat[character] += 1
                print(f"Moved {character} from shore to boat")  # Debug print
            else:
                print(f"Failed to move {character} - Shore: {shore[character]}, Boat: {sum(self.boat.values())}")  # Debug print
        
        self.check_game_state()  # Check game state after every movement
        print(f"After move - Boat: {self.boat}, Left Shore: {self.left_shore}, Right Shore: {self.right_shore}")  # Debug print

    def start_boat_movement(self):
        if sum(self.boat.values()) > 0:
            self.moving_boat = True

    def update_boat_position(self):
        if self.moving_boat:
            if self.boat_position == "left":
                self.boat_x += self.boat_speed
                if self.boat_x >= 500:
                    self.finish_boat_movement()
            else:
                self.boat_x -= self.boat_speed
                if self.boat_x <= 200:
                    self.finish_boat_movement()

    def finish_boat_movement(self):
        self.boat_position = "right" if self.boat_position == "left" else "left"
        self.moves += 1
        self.moving_boat = False
        print(f"Boat movement finished. Position: {self.boat_position}, Moves: {self.moves}")  # Debug print
        self.check_game_state()
        print(f"Game state after boat movement: Game over: {self.game_over}, Win: {self.win}")  # Additional debug print

    def check_game_state(self):
        if self.is_win_state():
            self.game_over = True
            self.win = True
            print("Game over: Win state")
        elif not self.is_valid_state():
            self.game_over = True
            self.win = False
            print("Game over: Invalid state")
        print(f"Game state checked - Game over: {self.game_over}, Win: {self.win}")
        print(f"Current state - Left: {self.left_shore}, Right: {self.right_shore}, Boat: {self.boat}, Boat position: {self.boat_position}")

    def is_valid_state(self):
        for shore in [self.left_shore, self.right_shore]:
            shore_priests = shore["priests"]
            shore_carnivores = shore["carnivores"]
            if self.boat_position == "left" and shore == self.left_shore:
                shore_priests += self.boat["priests"]
                shore_carnivores += self.boat["carnivores"]
            elif self.boat_position == "right" and shore == self.right_shore:
                shore_priests += self.boat["priests"]
                shore_carnivores += self.boat["carnivores"]
            if shore_priests > 0 and shore_carnivores > shore_priests:
                return False
        return True

    def is_win_state(self):
        win_condition = (self.right_shore["priests"] == 3 and 
                         self.right_shore["carnivores"] == 3 and
                         self.left_shore["priests"] == 0 and 
                         self.left_shore["carnivores"] == 0 and
                         self.boat["priests"] == 0 and 
                         self.boat["carnivores"] == 0 and
                         self.boat_position == "right")
        print(f"Win state check:")
        print(f"Right shore: {self.right_shore}")
        print(f"Left shore: {self.left_shore}")
        print(f"Boat: {self.boat}")
        print(f"Boat position: {self.boat_position}")
        print(f"Win condition met: {win_condition}")
        return win_condition

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            
            self.update_boat_position()
            self.draw()
            clock.tick(60)

if __name__ == "__main__":
    game = LakeCrossingGame()
    game.run()