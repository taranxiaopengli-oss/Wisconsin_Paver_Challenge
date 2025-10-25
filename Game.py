
import pygame
import sys

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font
        self.is_hovered = False
    
    def draw(self, surface):
        # Draw button with hover effect
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (0, 0, 0), self.rect, 2, border_radius=10)  # Border
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left mouse button
            return self.rect.collidepoint(pos)
        return False


class MySprite(pygame.sprite.Sprite):
    def __init__(self, image_path, pos, size=None):
        super().__init__()
        image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.smoothscale(image, size) if size else image
        self.rect = self.image.get_rect(topleft=pos)
    def move_to(self, x, y):
        self.rect.topleft = (x, y)


class user:
    def __init__(self, username, password):
        self.username = str(username)
        self.password = str(password)
        
        






class InputBox:
    def __init__(self, x, y, w, h, font, blink_ms=500):
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font
        self.text = ""
        self.active = False

        # caret (blinking cursor)
        self.caret_visible = True
        self.blink_ms = blink_ms
        self.last_blink = pygame.time.get_ticks()

    def handle_event(self, e):
        if e.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(e.pos)
        elif e.type == pygame.KEYDOWN and self.active:
            if e.key == pygame.K_RETURN:
                return True  # submit
            elif e.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += e.unicode
        return False

    def update(self):
        # toggle caret visibility on a timer (no frame freezing)
        now = pygame.time.get_ticks()
        if now - self.last_blink >= self.blink_ms:
            self.caret_visible = not self.caret_visible
            self.last_blink = now

    def draw(self, surface):
        # box
        pygame.draw.rect(surface, (255,255,255), self.rect)
        pygame.draw.rect(surface, (0,0,0), self.rect, 2)

        # text
        txt = self.font.render(self.text, True, (0,0,0))
        text_y = self.rect.y + (self.rect.h - txt.get_height()) // 2
        surface.blit(txt, (self.rect.x + 8, text_y))

        # caret at end of text (only when active + visible)
        if self.active and self.caret_visible:
            caret_x = self.rect.x + 8 + txt.get_width()
            caret_y = self.rect.y + 6
            caret_h = self.rect.h - 12
            pygame.draw.rect(surface, (0,0,0), (caret_x, caret_y, 2, caret_h))

    def get_text(self):
        return self.text.strip()



class Game:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
    
        # Initialize cell size
        self.CELL_SIDE = 110
        self.ROWS = 6
        self.COLS = 10
        
       
        
        # Initialize players
        self.all_players = []
        self.current_player = None
         
        # Initialize whether or not the game is going to end
        self.end_game = True

        # Game window settings
        self.BANNER_HEIGHT = self.CELL_SIDE 
        self.WINDOW_WIDTH = self.CELL_SIDE * self.COLS
        self.PLAYZONE_HEIGHT = self.CELL_SIDE * self.ROWS 
        self.window = pygame.display.set_mode((self.WINDOW_WIDTH, self.PLAYZONE_HEIGHT + self.BANNER_HEIGHT))
        pygame.display.set_caption("My Game")
        

        # List of blocked positions
        self.blocked_positions = [[2,1],[3,1],[4,1],[5,1],[5,2],[5,3],[5,4],[8,2],[9,3],[3,6],[4,6],[6,6],[7,6],[6,3]]
        self.road_blocked_cells = self.blocked_positions

        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREY = (128, 128, 128)
        self.BUTTON_COLOR = (100, 200, 100)  # Green
        self.BUTTON_HOVER = (100, 255, 100)  # Lighter green
        self.BUTTON_TEXT = (255, 255, 255)  # White
        

        # Font
        self.font = pygame.font.Font(None, 48)  # Default font, size 48

        # Initialize full window size
        self.FULL_WINDOW_HEIGHT = self.PLAYZONE_HEIGHT + self.BANNER_HEIGHT
        
        # Game clock
        self.clock = pygame.time.Clock()
        self.running = True

        # Page state variable 
        self.pages = ["title", "game", "end"]
        self.page = self.pages[0]
        
        # Create replay button
        replay_button_width = 200
        replay_button_height = 50
        replay_button_x = (self.WINDOW_WIDTH - replay_button_width) // 2
        replay_button_y = self.PLAYZONE_HEIGHT + self.BANNER_HEIGHT - 50  # Position near bottom
        self.replay_button = Button(
                replay_button_x, replay_button_y, 
                replay_button_width, replay_button_height,
                "Replay?",
                self.BUTTON_COLOR,
                self.BUTTON_HOVER,
                self.BUTTON_TEXT,
                self.font
            )
        # Create next button 
        button_width = 200
        button_height = 50
        button_x = (self.WINDOW_WIDTH - button_width) // 2
        button_y = self.PLAYZONE_HEIGHT + self.BANNER_HEIGHT - 100  # Position near bottom
        self.next_button = Button(
                button_x, button_y, 
                button_width, button_height,
                "Start Game",
                self.BUTTON_COLOR,
                self.BUTTON_HOVER,
                self.BUTTON_TEXT,
                self.font
            )
        
        # Create exit button
        exit_button_width = 200
        exit_button_height = 50
        exit_button_x = (self.WINDOW_WIDTH - exit_button_width) // 2
        exit_button_y = self.PLAYZONE_HEIGHT + self.BANNER_HEIGHT - 150  # Position near bottom
        self.exit_button = Button(
                exit_button_x, exit_button_y, 
                exit_button_width, exit_button_height,
                "Exit",
                self.BUTTON_COLOR,
                self.BUTTON_HOVER,
                self.BUTTON_TEXT,
                self.font
            )
        # Create a function that finds the coords from the cell position
        self.find_coords_from_cell = lambda cell_x, cell_y: ((cell_x - 1) * self.CELL_SIDE + 1, (cell_y - 1) * self.CELL_SIDE + 1)
        
        # Initialize sprites
        self.cheese_factories_cells = [[1,1],[10,6]]
        cheese = pygame.image.load("assets/cheese.png") 
        self.scaled_cheese = pygame.transform.scale(cheese, (self.CELL_SIDE, self.CELL_SIDE))
        self.groceries_cells = [[4,2],[2,4],[8,3]]
        store = pygame.image.load("assets/store.png") 
        self.scaled_store = pygame.transform.scale(store, (self.CELL_SIDE, self.CELL_SIDE))
        self.asphalt_paver_cell = [1,1]
        x_pos = (self.asphalt_paver_cell[0] - 1) * self.CELL_SIDE + 1
        y_pos = (self.asphalt_paver_cell[1] - 1) * self.CELL_SIDE + 1
        self.scaled_paver = MySprite("assets/asphalt_paver.png",(x_pos,y_pos),(self.CELL_SIDE, self.CELL_SIDE)) 
        self.steps_of_paver_cells = [[1,1]]
        self.cells_paved = [[1,1]]
        self.road_blocked_sign = pygame.image.load("assets/road_blocked.png")
        self.scaled_road_blocked_sign = pygame.transform.scale(self.road_blocked_sign, (self.CELL_SIDE, self.CELL_SIDE))
        self.road_blocked_cells = self.blocked_positions
        
        # Initialize the best record of cells paved and steps of paver
        self.best_cells_paved = 0
        self.best_steps_of_paver = 0

        # Initialize paver visibility for the blinking effect
        self.is_paver_visible = True
        self.last_blink_time = pygame.time.get_ticks()

        # Create best record for cells paved and steps of paver
        self.record_of_cells_paved = []
        self.record_of_steps_of_paver = []
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            
            # Check for button clicks
            if self.page == self.pages[0]:  # Only on title page
                if self.next_button.is_clicked(mouse_pos, event):
                    self.next_page()                           

            # Check for exit button clicks
            if self.page == self.pages[2]:
                if self.exit_button.is_clicked(mouse_pos, event):
                    self.running = False    
            
            # Check for replay button clicks
            if self.page == self.pages[2]:
                if self.replay_button.is_clicked(mouse_pos, event):
                    self.page = self.pages[1]
                    self.asphalt_paver_cell = [1,1]
                    x_pos = (self.asphalt_paver_cell[0] - 1) * self.CELL_SIDE + 1
                    y_pos = (self.asphalt_paver_cell[1] - 1) * self.CELL_SIDE + 1
                    self.scaled_paver = MySprite("assets/asphalt_paver.png",(x_pos,y_pos),(self.CELL_SIDE, self.CELL_SIDE)) 
                    self.steps_of_paver_cells = [[1,1]]
                    self.cells_paved = [[1,1]]
            
            # Check for keydown events during game
            elif self.page == self.pages[1]:
                if event.type == pygame.KEYDOWN:
                    is_updated = False
                    if event.key == pygame.K_UP:
                        if self.asphalt_paver_cell[1] > 1:
                            is_updated = True
                            self.asphalt_paver_cell[1] -= 1
                        if self.asphalt_paver_cell in self.blocked_positions:
                            is_updated = False
                            self.asphalt_paver_cell[1] += 1    
                            
                    elif event.key == pygame.K_DOWN:
                        if self.asphalt_paver_cell[1] < self.ROWS:
                            is_updated = True
                            self.asphalt_paver_cell[1] += 1
                        if self.asphalt_paver_cell in self.blocked_positions:
                            is_updated = False
                            self.asphalt_paver_cell[1] -= 1
                            
                    elif event.key == pygame.K_LEFT:
                        if self.asphalt_paver_cell[0] > 1:
                            is_updated = True
                            self.asphalt_paver_cell[0] -= 1
                        if self.asphalt_paver_cell in self.blocked_positions:
                            is_updated = False
                            self.asphalt_paver_cell[0] += 1
                        if self.asphalt_paver_cell in self.blocked_positions:
                            is_updated = False
                            self.asphalt_paver_cell[0] -= 1
                            
                    elif event.key == pygame.K_RIGHT:
                        if self.asphalt_paver_cell[0] < self.COLS:
                            is_updated = True
                            self.asphalt_paver_cell[0] += 1
                        if self.asphalt_paver_cell in self.blocked_positions:
                            is_updated = False
                            self.asphalt_paver_cell[0] -= 1
                                              
                    
                    if is_updated:
                        new_paved_pos = [self.asphalt_paver_cell[0], self.asphalt_paver_cell[1]]
                        self.steps_of_paver_cells.append(new_paved_pos)
                        if new_paved_pos not in self.cells_paved:
                            self.cells_paved.append(new_paved_pos)
                    # Check for when the asphalt paver has reached all cheese factories and groceries
                
                
                # Check if the asphalt paver has reached all locations
                self.end_game = True

                # Check if the asphalt paver has reached all cheese factories
                for factory in self.cheese_factories_cells:
                    if factory not in self.cells_paved:
                        self.end_game = False
                        break
                
                # Check if the asphalt paver has reached all groceries
                if self.end_game:  
                    for grocery in self.groceries_cells:
                        if grocery not in self.cells_paved:
                            self.end_game = False
                            break
                
                # When the asphalt paver has reached all locations
                if self.end_game == True:
                    self.page = self.pages[2]
                    self.record_of_cells_paved.append(len(self.cells_paved))
                    self.record_of_steps_of_paver.append(len(self.steps_of_paver_cells))
                    self.best_cells_paved = min(self.record_of_cells_paved)
                    self.best_steps_of_paver = min(self.record_of_steps_of_paver)


            
            elif self.page == self.pages[2]: 
                if self.replay_button.is_clicked(mouse_pos, event):
                    self.page = self.pages[1]
                    self.asphalt_paver_cell = [1,1]
                    self.cells_paved = [[1,1]]
                    self.steps_of_paver_cells = [[1,1]]    
                    
                   
    
    def next_page(self):
        current_index = self.pages.index(self.page)
        if current_index < len(self.pages) - 1:
            self.page = self.pages[current_index + 1]
        else:
            self.page = self.pages[0]  # Loop back to first page
    
    def update(self):
        # Update game state here
        pass
    
    def render_wrapped_text(self, text, font, color, x, y, max_width, line_spacing=10):
        """Render text with word wrapping.
        
        Args:
            text: The text to render
            font: The font to use
            color: Text color
            x, y: Top-left position of the text block
            max_width: Maximum width of the text block
            line_spacing: Space between lines
        """
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            # Test if adding the word would exceed max_width
            test_line = ' '.join(current_line + [word])
            test_width = font.size(test_line)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        
        # Add the last line
        if current_line:
            lines.append(' '.join(current_line))
        
        # Render each line
        y_offset = 0
        for line in lines:
            line_surface = font.render(line, True, color)
            self.window.blit(line_surface, (x, y + y_offset))
            y_offset += font.get_height() + line_spacing
    
    def render_title(self):
        # Show the title page
        pygame.display.set_caption("Wisconsin Road Paver Challenge")
        title = "Welcome to Wisconsin, America's Dairyland!"
        description = "Here, you'll build roads to help deliver fresh cheese from cheese factories to grocery stores. Use as few road tiles as possible to save materials and protect the Earth."
             
        

        # Update button hover state
        mouse_pos = pygame.mouse.get_pos()
        self.next_button.check_hover(mouse_pos)
        
        # Draw the button
        self.next_button.draw(self.window)
        
        
        
        # Render title
        title_surface = self.font.render(title, True, self.BLACK)
        title_rect = title_surface.get_rect(centerx=self.WINDOW_WIDTH//2, top=100)
        self.window.blit(title_surface, title_rect)
        
        # Render wrapped description
        self.render_wrapped_text(
            text=description,
            font=self.font,
            color=self.BLACK,
            x=self.WINDOW_WIDTH // 8,  # Start at 1/8th of screen width
            y=title_rect.bottom + 50,  # Below the title
            max_width=self.WINDOW_WIDTH * 3 // 4  # 3/4 of screen width
        )

    def render_game(self):
        # Render vertical grid lines
        for i in range(self.COLS + 1):
            x_position = i * self.CELL_SIDE  # Calculate x position for each line
            pygame.draw.line(self.window, self.BLACK, (x_position, 0), (x_position, self.PLAYZONE_HEIGHT), 2)
        
        # Render horizontal grid lines
        for i in range(self.ROWS + 1):
            y_position = i * self.CELL_SIDE  # Calculate y position for each line
            pygame.draw.line(self.window, self.BLACK, (0, y_position), (self.WINDOW_WIDTH, y_position), 2)
        
        # Render paved cells
        for cell in self.cells_paved:
            x_cell = cell[0]
            y_cell = cell[1]
            x_coord, y_coord = self.find_coords_from_cell(x_cell, y_cell)
            pygame.draw.rect(self.window, (64,64,64), (x_coord, y_coord, self.CELL_SIDE, self.CELL_SIDE))
        
        # Render the cheese factories
        for cell in self.cheese_factories_cells:
            x_cell = cell[0]
            y_cell = cell[1]
            x_coord, y_coord = self.find_coords_from_cell(x_cell, y_cell)            
            self.window.blit(self.scaled_cheese, (x_coord, y_coord))
        
        # Render the groceries
        for pos in self.groceries_cells:
            x_pos = pos[0]
            y_pos = pos[1]
            x_coord, y_coord = self.find_coords_from_cell(x_pos, y_pos)
            self.window.blit(self.scaled_store, (x_coord, y_coord))
        
        # Render the road blocked sign
        for cell in self.road_blocked_cells:
            x_cell = cell[0]
            y_cell = cell[1]
            x_coord, y_coord = self.find_coords_from_cell(x_cell, y_cell)
            self.window.blit(self.scaled_road_blocked_sign, (x_coord, y_coord))
        
        # Render the asphalt paver if it is visible
        if len(self.steps_of_paver_cells) > 1:
            self.is_paver_visible = True
        else:                                                                     
            current_time = pygame.time.get_ticks()         
            if current_time - self.last_blink_time >= 500:
                self.is_paver_visible = not self.is_paver_visible
                self.last_blink_time = current_time
                
        if self.is_paver_visible == True:
            x_coord, y_coord = self.find_coords_from_cell(self.asphalt_paver_cell[0], self.asphalt_paver_cell[1])
            self.scaled_paver.move_to(x_coord, y_coord)
            self.window.blit(self.scaled_paver.image, self.scaled_paver.rect)


            
     
            
    def banner_text(self):
        text_banner = f"The # of cells paved:" 
        cells_paved = len(self.cells_paved)
        text_2nd_line = "Use the arrow keys to move the asphalt paver."        
        text_3rd_line = "The # of steps of the asphalt paver:"
        paver_steps = len(self.steps_of_paver_cells)

        text_banner_surface = self.font.render(text_banner, True, self.BLACK)
        cells_paved_surface = self.font.render(str(cells_paved), True, self.RED) 
        text_2nd_line_surface = self.font.render(text_2nd_line, True, self.BLACK)
        paver_steps_surface = self.font.render(str(paver_steps), True, self.RED)
        text_3rd_line_surface = self.font.render(text_3rd_line, True, self.BLACK)

        # This one is the one that renders the # of cells paved
        text_banner_rect = text_banner_surface.get_rect(centerx=self.WINDOW_WIDTH//6 + 67, top=self.FULL_WINDOW_HEIGHT - self.BANNER_HEIGHT + 50)
        cells_paved_rect = cells_paved_surface.get_rect(topleft=(text_banner_rect.right, text_banner_rect.top)) 
        # This one is the one that renders the instructions
        text_2nd_rect = text_2nd_line_surface.get_rect(centerx=self.WINDOW_WIDTH//2, top=self.FULL_WINDOW_HEIGHT - self.BANNER_HEIGHT + 20)
        """This one is the one that renders the # of steps of the asphalt paver and is connected to the # of cells paved"""
        text_3rd_rect = text_3rd_line_surface.get_rect(topleft=(cells_paved_rect.right + 30, cells_paved_rect.top))
        paver_steps_rect = paver_steps_surface.get_rect(topleft=(text_3rd_rect.right, text_3rd_rect.top))

        
        self.window.blit(text_banner_surface, text_banner_rect)#k
        self.window.blit(cells_paved_surface, cells_paved_rect)
        self.window.blit(text_2nd_line_surface, text_2nd_rect)
        self.window.blit(paver_steps_surface, paver_steps_rect)
        self.window.blit(text_3rd_line_surface, text_3rd_rect)


    
    
    def render_end(self):
        
        # Render the end text
        end_text = "You Win!"
        end_paved_score = "The # of cells you paved in this round: " + str(len(self.cells_paved))
        end_steps_score = "The # of steps of the asphalt paver in this round: " + str(len(self.steps_of_paver_cells))
        end_best_paved_steps = "Your best # of asphalt paver steps are: " + str(self.best_steps_of_paver)
        end_best_paved_cells = "Your best # of cells you paved in of all time are: " + str(self.best_cells_paved)

        end_best_paved_steps_surface = self.font.render(f"{end_best_paved_steps}", True, self.BLACK)       
        end_best_paved_cells_surface = self.font.render(f"{end_best_paved_cells}", True, self.BLACK)       
        end_surface_1 = self.font.render(f"{end_text}", True, self.BLACK)
        end_surface_2 = self.font.render(f"{end_paved_score}", True, self.BLACK)
        end_surface_3 = self.font.render(f"{end_steps_score}", True, self.BLACK)
        
        end_best_paved_steps_rect = end_best_paved_steps_surface.get_rect(centerx=self.WINDOW_WIDTH//2, top=self.FULL_WINDOW_HEIGHT//2)       
        end_rect_1 = end_surface_1.get_rect(centerx=self.WINDOW_WIDTH//2, top=self.FULL_WINDOW_HEIGHT//2 - 200)       
        end_rect_2 = end_surface_2.get_rect(centerx=self.WINDOW_WIDTH//2, top=self.FULL_WINDOW_HEIGHT//2 - 50)
        end_rect_3 = end_surface_3.get_rect(centerx=self.WINDOW_WIDTH//2, top=self.FULL_WINDOW_HEIGHT//2 - 100)
        end_rect_4 = end_best_paved_cells_surface.get_rect(centerx=self.WINDOW_WIDTH//2, top=self.FULL_WINDOW_HEIGHT//2 + 50 )
        
        self.window.blit(end_surface_1, end_rect_1)
        self.window.blit(end_surface_2, end_rect_2)
        self.window.blit(end_surface_3, end_rect_3)
        self.window.blit(end_best_paved_cells_surface, end_rect_4)
        self.window.blit(end_best_paved_steps_surface, end_best_paved_steps_rect)
        
        # Draw replay button
        mouse_pos = pygame.mouse.get_pos()  
        self.replay_button.check_hover(mouse_pos)
        self.replay_button.draw(self.window)  

        # Draw the exit button
        mouse_pos = pygame.mouse.get_pos()
        self.exit_button.check_hover(mouse_pos)
        self.exit_button.draw(self.window) 
        
        
        

    def render(self):
        # Clear the screen
        self.window.fill(self.WHITE)
        
        # Render the current page
        if self.page == self.pages[0]:  # Title page
            self.render_title()
        elif self.page == self.pages[1]:  # Game page
            self.render_game()
            self.banner_text()
        elif self.page == self.pages[2]:
            self.render_end()
        # Update the display
        pygame.display.flip()
                  
    def run(self):
        # Main game loop
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)#y
        
        # Clean up
        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()