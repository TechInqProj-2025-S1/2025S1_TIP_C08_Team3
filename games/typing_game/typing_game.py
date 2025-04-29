import pygame
import random
import os
import json
import time
import math

class TypingGame:
    def __init__(self, difficulty="medium"):
        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Typing Game")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game settings
        self.difficulty = difficulty  # "easy", "medium", "hard"
        self.score = 0
        self.player_name = "Player"
        self.game_time = 60  # seconds
        self.time_left = self.game_time
        self.last_time_check = time.time()
        self.game_over = False
        
        # Words settings
        self.word_lists = {
            "easy": ["cat", "dog", "run", "jump", "play", "fast", "book", "game", "fish", "bird", 
                    "tree", "ball", "home", "food", "time", "blue", "red", "car", "star", "pen"],
            "medium": ["computer", "keyboard", "monitor", "window", "yellow", "purple", "orange", 
                      "teacher", "student", "question", "answer", "picture", "learning", "system", 
                      "machine", "software", "problem", "solution", "mountain", "library"],
            "hard": ["algorithm", "education", "programming", "development", "university", 
                    "technology", "application", "mathematics", "dictionary", "government", 
                    "encyclopedia", "environment", "performance", "opportunity", "understanding",
                    "information", "communication", "relationship", "organization", "responsibility"]
        }
        
        self.falling_words = []
        self.current_input = ""
        self.combo = 0
        self.typed_words = 0
        self.mistyped_words = 0
        self.last_spawn_time = time.time()
        
        # Set up fonts
        self.title_font = pygame.font.SysFont(None, 48)
        self.word_font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Set difficulty parameters
        self.set_difficulty(difficulty)

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        
        if difficulty == "easy":
            self.word_list = self.word_lists["easy"]
            self.fall_speed = 1.0  # pixels per frame
            self.spawn_interval = 2.0  # seconds
            self.words_on_screen = 5
        elif difficulty == "medium":
            self.word_list = self.word_lists["medium"]
            self.fall_speed = 1.5
            self.spawn_interval = 1.5
            self.words_on_screen = 7
        elif difficulty == "hard":
            self.word_list = self.word_lists["hard"]
            self.fall_speed = 2.0
            self.spawn_interval = 1.0
            self.words_on_screen = 10
            
        # Speed increases over time in all difficulties
        self.speed_increase_rate = 0.1  # increase fall speed every 10 seconds

    def spawn_word(self):
        if len(self.falling_words) >= self.words_on_screen:
            return
            
        word = random.choice(self.word_list)
        text_surface = self.word_font.render(word, True, (255, 255, 255))
        text_width = text_surface.get_width()
        
        # Generate random position for the word
        x = random.randint(text_width // 2, self.width - text_width // 2)
        
        self.falling_words.append({
            'word': word,
            'x': x,
            'y': 0,
            'color': (255, 255, 255),
            'typed_chars': 0  # Number of correctly typed characters
        })
        
        self.last_spawn_time = time.time()

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
            self.screen.fill((30, 30, 50))  # Dark blue/purple background
            
            # Title
            title = self.title_font.render("Typing Game", True, (255, 255, 255))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))
            
            # Name input box
            name_prompt = self.word_font.render("Enter your name:", True, (255, 255, 255))
            self.screen.blit(name_prompt, (self.width // 2 - name_prompt.get_width() // 2, 200))
            
            # Draw input box
            input_box = pygame.Rect(self.width // 2 - 100, 250, 200, 40)
            color = (100, 100, 200) if name_input_active else (70, 70, 70)
            pygame.draw.rect(self.screen, color, input_box, 2)
            
            # Render current name input
            name_surface = self.word_font.render(name_input, True, (255, 255, 255))
            self.screen.blit(name_surface, (input_box.x + 5, input_box.y + 5))
            
            # Difficulty selection
            diff_text = self.word_font.render("Select Difficulty:", True, (255, 255, 255))
            self.screen.blit(diff_text, (self.width // 2 - diff_text.get_width() // 2, 330))
            
            for i, diff in enumerate(difficulty_options):
                color = (255, 215, 0) if i == selected_difficulty else (255, 255, 255)
                diff_option = self.word_font.render(diff.title(), True, color)
                self.screen.blit(diff_option, (self.width // 2 - diff_option.get_width() // 2, 380 + i * 40))
            
            # Start button
            start_text = self.word_font.render("Start Game", True, (0, 0, 0))
            start_rect = start_text.get_rect(center=(self.width // 2, 520))
            pygame.draw.rect(self.screen, (0, 255, 0), (start_rect.x - 10, start_rect.y - 10, 
                                                      start_rect.width + 20, start_rect.height + 20))
            self.screen.blit(start_text, start_rect)
            
            # Game instructions
            instructions = [
                "Type the falling words before they hit the ground!",
                "Type faster to get a higher score.",
                "Words will fall faster over time."
            ]
            
            for i, instruction in enumerate(instructions):
                instr_text = self.small_font.render(instruction, True, (200, 200, 200))
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
                        self.time_left = self.game_time
                        self.last_time_check = time.time()
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
                            self.time_left = self.game_time
                            self.last_time_check = time.time()
                            menu_running = False
                        
            pygame.display.flip()
            self.clock.tick(30)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                else:
                    if event.key == pygame.K_RETURN:
                        # Check if current input matches any word
                        self.check_word()
                    elif event.key == pygame.K_BACKSPACE:
                        # Remove the last character
                        if self.current_input:
                            self.current_input = self.current_input[:-1]
                            # Update the highlighting on falling words
                            self.update_word_highlighting()
                    elif event.unicode.isalpha() or event.unicode.isspace():
                        # Add character to current input
                        self.current_input += event.unicode
                        # Update the highlighting on falling words
                        self.update_word_highlighting()

    def update_word_highlighting(self):
        # Reset all highlighting
        for word in self.falling_words:
            word['typed_chars'] = 0
            word['color'] = (255, 255, 255)  # White
            
        # If no input, return
        if not self.current_input:
            return
            
        # Check each falling word
        for word in self.falling_words:
            if word['word'].startswith(self.current_input):
                # Highlight the part that matches
                word['typed_chars'] = len(self.current_input)
                word['color'] = (0, 255, 0)  # Green
                # If there's one exact match, we don't need to check further
                if word['word'] == self.current_input:
                    break

    def check_word(self):
        # Check if the current input matches any falling word
        for i, word in enumerate(self.falling_words):
            if self.current_input.lower() == word['word'].lower():
                # Award points based on word length and difficulty
                word_points = len(word['word']) * {"easy": 1, "medium": 2, "hard": 3}[self.difficulty]
                self.score += word_points
                
                # Combo bonus
                self.combo += 1
                if self.combo > 1:
                    combo_bonus = self.combo * 5
                    self.score += combo_bonus
                
                # Remove the word
                self.falling_words.pop(i)
                
                # Increment typed words counter
                self.typed_words += 1
                
                # Clear input
                self.current_input = ""
                return
                
        # If no match was found, reset combo and clear input
        self.combo = 0
        self.current_input = ""
        self.mistyped_words += 1

    def update(self):
        current_time = time.time()
        
        # Update timer
        time_delta = current_time - self.last_time_check
        self.time_left -= time_delta
        self.last_time_check = current_time
        
        # Check if game over
        if self.time_left <= 0:
            self.time_left = 0
            self.game_over = True
            self.save_score()
            return
            
        # Spawn new words
        if current_time - self.last_spawn_time >= self.spawn_interval:
            self.spawn_word()
            
        # Update fall speed based on elapsed time
        elapsed_time = self.game_time - self.time_left
        speed_multiplier = 1 + (elapsed_time / 10) * self.speed_increase_rate
        current_fall_speed = self.fall_speed * speed_multiplier
        
        # Update word positions
        for i, word in enumerate(self.falling_words[:]):
            word['y'] += current_fall_speed
            
            # Check if word hit the ground
            if word['y'] > self.height:
                self.falling_words.pop(i)
                self.combo = 0
                self.mistyped_words += 1
                
                # Penalty for missed words
                self.score = max(0, self.score - 5)

    def draw(self):
        # Draw starry background
        self.screen.fill((0, 0, 20))  # Very dark blue
        
        # Draw stars
        for i in range(50):
            x = (i * 29) % self.width
            y = (i * 37) % self.height
            brightness = (math.sin(time.time() + i) + 1) * 127
            pygame.draw.circle(self.screen, (brightness, brightness, brightness), (x, y), 1)
        
        if not self.game_over:
            # Draw falling words
            for word in self.falling_words:
                # Draw the typed part in green
                if word['typed_chars'] > 0:
                    typed_part = word['word'][:word['typed_chars']]
                    typed_surface = self.word_font.render(typed_part, True, (0, 255, 0))
                    typed_rect = typed_surface.get_rect(center=(word['x'], word['y']))
                    self.screen.blit(typed_surface, typed_rect)
                    
                    # Draw the remaining part in white
                    remaining_part = word['word'][word['typed_chars']:]
                    if remaining_part:
                        remaining_surface = self.word_font.render(remaining_part, True, (255, 255, 255))
                        remaining_rect = remaining_surface.get_rect(
                            midleft=(typed_rect.right, typed_rect.centery))
                        self.screen.blit(remaining_surface, remaining_rect)
                else:
                    # Draw the whole word in white or its specified color
                    word_surface = self.word_font.render(word['word'], True, word['color'])
                    word_rect = word_surface.get_rect(center=(word['x'], word['y']))
                    self.screen.blit(word_surface, word_rect)
            
            # Draw input area
            pygame.draw.rect(self.screen, (50, 50, 70), (0, self.height - 50, self.width, 50))
            pygame.draw.line(self.screen, (200, 200, 200), (0, self.height - 50), (self.width, self.height - 50), 2)
            
            # Draw current input
            input_text = self.word_font.render(self.current_input, True, (255, 255, 255))
            self.screen.blit(input_text, (20, self.height - 40))
            
            # Draw combo
            if self.combo > 1:
                combo_text = self.small_font.render(f"Combo: x{self.combo}", True, (255, 255, 0))
                self.screen.blit(combo_text, (self.width - combo_text.get_width() - 20, self.height - 40))
            
            # Draw score
            score_text = self.word_font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (20, 20))
            
            # Draw time left
            time_text = self.word_font.render(f"Time: {int(self.time_left)}s", True, (255, 255, 255))
            self.screen.blit(time_text, (self.width - time_text.get_width() - 20, 20))
            
            # Draw typed/missed words
            typed_text = self.small_font.render(f"Typed: {self.typed_words}", True, (0, 255, 0))
            self.screen.blit(typed_text, (20, 70))
            missed_text = self.small_font.render(f"Missed: {self.mistyped_words}", True, (255, 0, 0))
            self.screen.blit(missed_text, (20, 100))
            
        else:
            # Game over screen
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            # Draw game over text
            game_over_text = self.title_font.render("GAME OVER", True, (255, 0, 0))
            self.screen.blit(game_over_text, (self.width // 2 - game_over_text.get_width() // 2, self.height // 2 - 100))
            
            # Draw final score
            score_text = self.title_font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (self.width // 2 - score_text.get_width() // 2, self.height // 2 - 40))
            
            # Draw statistics
            stats_text = self.word_font.render(f"Words Typed: {self.typed_words} | Words Missed: {self.mistyped_words}", True, (255, 255, 255))
            self.screen.blit(stats_text, (self.width // 2 - stats_text.get_width() // 2, self.height // 2 + 20))
            
            # Draw accuracy
            total_words = self.typed_words + self.mistyped_words
            accuracy = (self.typed_words / total_words * 100) if total_words > 0 else 0
            accuracy_text = self.word_font.render(f"Accuracy: {accuracy:.1f}%", True, (255, 255, 255))
            self.screen.blit(accuracy_text, (self.width // 2 - accuracy_text.get_width() // 2, self.height // 2 + 60))
            
            # Draw restart prompt
            restart_text = self.word_font.render("Press ENTER to play again", True, (255, 255, 255))
            self.screen.blit(restart_text, (self.width // 2 - restart_text.get_width() // 2, self.height // 2 + 120))
        
        # Draw player name and difficulty
        info_text = self.small_font.render(f"Player: {self.player_name} | Difficulty: {self.difficulty.title()}", True, (200, 200, 200))
        self.screen.blit(info_text, (20, self.height - 20))
        
        pygame.display.flip()

    def reset_game(self):
        self.score = 0
        self.game_over = False
        self.time_left = self.game_time
        self.last_time_check = time.time()
        self.last_spawn_time = time.time()
        self.current_input = ""
        self.falling_words = []
        self.combo = 0
        self.typed_words = 0
        self.mistyped_words = 0
        # Re-apply difficulty settings
        self.set_difficulty(self.difficulty)

    def save_score(self):
        # Create scores directory if it doesn't exist
        if not os.path.exists("scores"):
            os.makedirs("scores")
            
        # Score file path - match the launcher's expected format
        score_file = "scores/typing_game_scores.json"
        
        # Load existing scores
        scores = []
        if os.path.exists(score_file):
            try:
                with open(score_file, 'r') as f:
                    scores = json.load(f)
            except:
                scores = []
                
        # Add current score
        total_words = self.typed_words + self.mistyped_words
        accuracy = (self.typed_words / total_words * 100) if total_words > 0 else 0
        
        scores.append({
            "name": self.player_name,
            "score": self.score,
            "difficulty": self.difficulty,
            "words_typed": self.typed_words,
            "words_missed": self.mistyped_words,
            "accuracy": round(accuracy, 1)
        })
        
        # Save scores
        with open(score_file, 'w') as f:
            json.dump(scores, f)

if __name__ == "__main__":
    game = TypingGame()
    game.run()
