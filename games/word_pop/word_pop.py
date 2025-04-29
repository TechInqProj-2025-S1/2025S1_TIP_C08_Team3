import pygame
import random
import os
import json
import math

class WordPop:
    def __init__(self, difficulty="medium"):
        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Word Pop")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game settings
        self.difficulty = difficulty  # "easy", "medium", "hard"
        self.score = 0
        self.player_name = "Player"
        self.game_over = False
        self.time_left = 60  # 60 seconds game time
        self.last_time_check = pygame.time.get_ticks()
        
        # Balloon settings
        self.balloons = []
        self.balloon_colors = [
            (255, 0, 0),      # Red
            (0, 255, 0),      # Green
            (0, 0, 255),      # Blue
            (255, 255, 0),    # Yellow
            (255, 0, 255),    # Magenta
            (0, 255, 255),    # Cyan
        ]
        
        # Word lists
        self.correct_words = [
            "apple", "banana", "orange", "grape", "school",
            "teacher", "learning", "education", "knowledge", "student",
            "library", "book", "pencil", "paper", "write",
            "read", "learn", "think", "understand", "practice"
        ]
        
        self.incorrect_words = [
            "appel", "banan", "orang", "graep", "skool",
            "techer", "lernin", "edukation", "knwledge", "studnt",
            "librry", "booc", "pensil", "papar", "rite",
            "reed", "lern", "thynk", "understnd", "pracktis"
        ]
        
        # Set up fonts
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Set difficulty parameters
        self.set_difficulty(difficulty)
        
        # Start with initial balloons
        self.spawn_initial_balloons()

    def set_difficulty(self, difficulty):
        if difficulty == "easy":
            self.balloon_speed = 1
            self.spawn_rate = 3000  # milliseconds
            self.max_balloons = 5
            self.incorrect_word_ratio = 0.2  # 20% incorrect words
        elif difficulty == "medium":
            self.balloon_speed = 1.5
            self.spawn_rate = 2000
            self.max_balloons = 8
            self.incorrect_word_ratio = 0.4  # 40% incorrect words
        elif difficulty == "hard":
            self.balloon_speed = 2
            self.spawn_rate = 1500
            self.max_balloons = 12
            self.incorrect_word_ratio = 0.6  # 60% incorrect words
        
        self.last_spawn_time = pygame.time.get_ticks()

    def spawn_initial_balloons(self):
        # Spawn initial balloons
        for _ in range(self.max_balloons // 2):
            self.spawn_balloon()

    def spawn_balloon(self):
        if len(self.balloons) >= self.max_balloons:
            return
            
        # Decide if the word is correct or incorrect
        is_correct = random.random() > self.incorrect_word_ratio
        
        if is_correct:
            word = random.choice(self.correct_words)
        else:
            word = random.choice(self.incorrect_words)
            
        # Generate random position and color
        x = random.randint(50, self.width - 100)
        y = self.height + random.randint(20, 100)  # Start below the screen
        color = random.choice(self.balloon_colors)
        size = random.randint(40, 70)
        
        # Add balloon to list
        self.balloons.append({
            'word': word,
            'correct': is_correct,
            'x': x,
            'y': y,
            'color': color,
            'size': size,
            'speed': self.balloon_speed * (0.8 + random.random() * 0.4)  # Some variation in speed
        })

    def run(self):
        # Show start menu before the game
        self.show_start_menu()
        
        # Main game loop
        while self.running:
            self.handle_events()
            
            if not self.game_over:
                self.update()
            
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        
    def show_start_menu(self):
        menu_running = True
        difficulty_options = ["easy", "medium", "hard"]
        selected_difficulty = 1  # Default to medium
        
        # Input box for player name
        name_input = ""
        name_input_active = True
        
        while menu_running:
            self.screen.fill((135, 206, 235))  # Sky blue background
            
            # Title
            title = self.font.render("Word Pop", True, (0, 0, 0))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))
            
            # Name input box
            name_prompt = self.font.render("Enter your name:", True, (0, 0, 0))
            self.screen.blit(name_prompt, (self.width // 2 - name_prompt.get_width() // 2, 200))
            
            # Draw input box
            input_box = pygame.Rect(self.width // 2 - 100, 250, 200, 40)
            color = (100, 100, 200) if name_input_active else (70, 70, 70)
            pygame.draw.rect(self.screen, color, input_box, 2)
            
            # Render current name input
            name_surface = self.font.render(name_input, True, (0, 0, 0))
            self.screen.blit(name_surface, (input_box.x + 5, input_box.y + 5))
            
            # Difficulty selection
            diff_text = self.font.render("Select Difficulty:", True, (0, 0, 0))
            self.screen.blit(diff_text, (self.width // 2 - diff_text.get_width() // 2, 330))
            
            for i, diff in enumerate(difficulty_options):
                color = (255, 0, 0) if i == selected_difficulty else (0, 0, 0)
                diff_option = self.font.render(diff.title(), True, color)
                self.screen.blit(diff_option, (self.width // 2 - diff_option.get_width() // 2, 380 + i * 40))
            
            # Start button
            start_text = self.font.render("Start Game", True, (255, 255, 255))
            start_rect = start_text.get_rect(center=(self.width // 2, 520))
            pygame.draw.rect(self.screen, (0, 128, 0), (start_rect.x - 10, start_rect.y - 10, 
                                                       start_rect.width + 20, start_rect.height + 20))
            self.screen.blit(start_text, start_rect)
            
            # Game instructions
            instructions = [
                "Click on balloons with correctly spelled words!",
                "Avoid clicking on misspelled words."
            ]
            
            for i, instruction in enumerate(instructions):
                instr_text = self.small_font.render(instruction, True, (0, 0, 0))
                self.screen.blit(instr_text, (self.width // 2 - instr_text.get_width() // 2, 570 + i * 25))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    menu_running = False
                    self.running = False
                    return
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if input box was clicked
                    if input_box.collidepoint(event.pos):
                        name_input_active = True
                    else:
                        name_input_active = False
                        
                    # Check if difficulty options were clicked
                    for i, _ in enumerate(difficulty_options):
                        option_rect = pygame.Rect(self.width // 2 - 50, 380 + i * 40, 100, 30)
                        if option_rect.collidepoint(event.pos):
                            selected_difficulty = i
                            
                    # Check if start button was clicked
                    if start_rect.collidepoint(event.pos) and name_input:
                        self.player_name = name_input
                        self.difficulty = difficulty_options[selected_difficulty]
                        self.set_difficulty(self.difficulty)
                        self.time_left = 60  # Reset timer
                        self.score = 0       # Reset score
                        self.last_time_check = pygame.time.get_ticks()
                        menu_running = False
                        
                elif event.type == pygame.KEYDOWN:
                    if name_input_active:
                        if event.key == pygame.K_RETURN:
                            name_input_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            name_input = name_input[:-1]
                        else:
                            # Limit name length to 10 characters
                            if len(name_input) < 10:
                                name_input += event.unicode
                                
                    # Navigate difficulty with arrow keys
                    if event.key == pygame.K_UP:
                        selected_difficulty = max(0, selected_difficulty - 1)
                    elif event.key == pygame.K_DOWN:
                        selected_difficulty = min(len(difficulty_options) - 1, selected_difficulty + 1)
                    elif event.key == pygame.K_RETURN:
                        if name_input:
                            self.player_name = name_input
                            self.difficulty = difficulty_options[selected_difficulty]
                            self.set_difficulty(self.difficulty)
                            self.time_left = 60  # Reset timer
                            self.score = 0       # Reset score
                            self.last_time_check = pygame.time.get_ticks()
                            menu_running = False
                        
            pygame.display.flip()
            self.clock.tick(30)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                self.check_balloon_click(event.pos)
                
            elif event.type == pygame.KEYDOWN:
                if self.game_over and event.key == pygame.K_RETURN:
                    self.reset_game()

    def check_balloon_click(self, pos):
        for i, balloon in enumerate(self.balloons):
            # Check if the click is within the balloon
            distance = math.sqrt((pos[0] - balloon['x'])**2 + (pos[1] - balloon['y'])**2)
            if distance <= balloon['size'] // 2:
                # If clicked, check if word is correct
                if balloon['correct']:
                    self.score += 10
                else:
                    self.score -= 5
                    if self.score < 0:
                        self.score = 0
                
                # Remove the balloon
                self.balloons.pop(i)
                break

    def update(self):
        current_time = pygame.time.get_ticks()
        
        # Update timer
        if current_time - self.last_time_check >= 1000:  # 1 second has passed
            self.time_left -= 1
            self.last_time_check = current_time
            
            if self.time_left <= 0:
                self.game_over = True
                self.save_score()
        
        # Spawn new balloons
        if current_time - self.last_spawn_time >= self.spawn_rate:
            self.spawn_balloon()
            self.last_spawn_time = current_time
            
        # Update balloon positions
        for balloon in self.balloons:
            balloon['y'] -= balloon['speed']
            
            # If balloon goes off the top of the screen, remove it
            if balloon['y'] + balloon['size'] < 0:
                self.balloons.remove(balloon)
                # If it was a correct word that was missed, penalize
                if balloon['correct']:
                    self.score -= 2
                    if self.score < 0:
                        self.score = 0

    def draw(self):
        # Draw sky background
        self.screen.fill((135, 206, 235))  # Sky blue
        
        # Draw clouds (simple white circles)
        cloud_positions = [(100, 80), (300, 50), (500, 120), (700, 70)]
        for pos in cloud_positions:
            pygame.draw.circle(self.screen, (255, 255, 255), pos, 40)
            pygame.draw.circle(self.screen, (255, 255, 255), (pos[0]-30, pos[1]), 30)
            pygame.draw.circle(self.screen, (255, 255, 255), (pos[0]+30, pos[1]), 30)
        
        # Draw balloons
        for balloon in self.balloons:
            # Draw balloon (circle)
            pygame.draw.circle(self.screen, balloon['color'], (balloon['x'], balloon['y']), balloon['size'] // 2)
            
            # Draw balloon string
            pygame.draw.line(self.screen, (0, 0, 0), 
                             (balloon['x'], balloon['y'] + balloon['size'] // 2),
                             (balloon['x'], balloon['y'] + balloon['size']), 2)
            
            # Draw word on balloon
            word_surface = self.small_font.render(balloon['word'], True, (0, 0, 0))
            word_rect = word_surface.get_rect(center=(balloon['x'], balloon['y']))
            self.screen.blit(word_surface, word_rect)
        
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        self.screen.blit(score_text, (20, 20))
        
        # Draw time left
        time_text = self.font.render(f"Time: {self.time_left}", True, (0, 0, 0))
        self.screen.blit(time_text, (self.width - time_text.get_width() - 20, 20))
        
        # Draw player name and difficulty
        info_text = self.small_font.render(f"Player: {self.player_name} | Difficulty: {self.difficulty.title()}", True, (0, 0, 0))
        self.screen.blit(info_text, (20, self.height - 30))
        
        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
            self.screen.blit(game_over_text, (self.width // 2 - game_over_text.get_width() // 2, self.height // 2 - 50))
            
            final_score = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(final_score, (self.width // 2 - final_score.get_width() // 2, self.height // 2))
            
            restart_text = self.font.render("Press ENTER to play again", True, (255, 255, 255))
            self.screen.blit(restart_text, (self.width // 2 - restart_text.get_width() // 2, self.height // 2 + 50))
        
        pygame.display.flip()

    def reset_game(self):
        self.score = 0
        self.game_over = False
        self.time_left = 60
        self.last_time_check = pygame.time.get_ticks()
        self.last_spawn_time = pygame.time.get_ticks()
        self.balloons = []
        self.spawn_initial_balloons()

    def save_score(self):
        # Create scores directory if it doesn't exist
        if not os.path.exists("scores"):
            os.makedirs("scores")
            
        # Score file path - match the launcher's expected format
        score_file = "scores/word_pop_scores.json"
        
        # Load existing scores
        scores = []
        if os.path.exists(score_file):
            try:
                with open(score_file, 'r') as f:
                    scores = json.load(f)
            except:
                scores = []
                
        # Add current score
        scores.append({
            "name": self.player_name,
            "score": self.score,
            "difficulty": self.difficulty
        })
        
        # Save scores
        with open(score_file, 'w') as f:
            json.dump(scores, f)

if __name__ == "__main__":
    game = WordPop()
    game.run()
