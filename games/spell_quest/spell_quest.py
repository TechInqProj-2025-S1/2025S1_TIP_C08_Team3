import pygame
import random
import os
import json
import time

class SpellQuest:
    def __init__(self, difficulty="medium"):
        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Spell Quest")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game settings
        self.difficulty = difficulty  # "easy", "medium", "hard"
        self.score = 0
        self.player_name = "Player"
        self.hint_time = 5  # seconds before hint appears
        
        # Word categories and lists
        self.categories = {
            "Animals": ["elephant", "giraffe", "dolphin", "penguin", "tiger", "kangaroo", "rhinoceros", "squirrel", "chameleon", "crocodile"],
            "Countries": ["australia", "brazil", "canada", "denmark", "egypt", "france", "germany", "india", "japan", "mexico"],
            "Fruits": ["apple", "banana", "strawberry", "pineapple", "watermelon", "kiwi", "orange", "mango", "grapefruit", "blueberry"],
            "Occupations": ["teacher", "doctor", "engineer", "scientist", "architect", "journalist", "programmer", "musician", "astronaut", "detective"]
        }
        
        # Game state variables
        self.current_category = None
        self.current_word = None
        self.masked_word = None
        self.hint_shown = False
        self.hint_start_time = 0
        self.guessed_letters = set()
        self.remaining_attempts = 5
        self.game_over = False
        self.game_won = False
        self.words_completed = 0
        
        # Set up fonts
        self.font = pygame.font.SysFont(None, 48)
        self.small_font = pygame.font.SysFont(None, 36)
        self.tiny_font = pygame.font.SysFont(None, 24)
        
        # Set difficulty parameters
        self.set_difficulty(difficulty)
        
        # Start with first word
        self.select_new_word()

    def set_difficulty(self, difficulty):
        if difficulty == "easy":
            self.mask_percentage = 0.3  # 30% of letters masked
            self.hint_time = 7  # seconds before hint appears
            self.remaining_attempts = 7
        elif difficulty == "medium":
            self.mask_percentage = 0.5  # 50% of letters masked
            self.hint_time = 10
            self.remaining_attempts = 5
        elif difficulty == "hard":
            self.mask_percentage = 0.7  # 70% of letters masked
            self.hint_time = 15
            self.remaining_attempts = 3

    def select_new_word(self):
        # Choose a random category and word
        self.current_category = random.choice(list(self.categories.keys()))
        self.current_word = random.choice(self.categories[self.current_category])
        
        # Create masked version of the word
        self.mask_word()
        
        # Reset other game state variables
        self.hint_shown = False
        self.hint_start_time = time.time()
        self.guessed_letters = set()

    def mask_word(self):
        word = self.current_word
        num_to_mask = int(len(word) * self.mask_percentage)
        positions_to_mask = random.sample(range(len(word)), num_to_mask)
        
        masked_word = ""
        for i in range(len(word)):
            if i in positions_to_mask and word[i] not in self.guessed_letters:
                masked_word += "_"
            else:
                masked_word += word[i]
                
        self.masked_word = masked_word

    def update_masked_word(self, guessed_letter):
        word = self.current_word
        
        # Add the guessed letter to the set
        self.guessed_letters.add(guessed_letter)
        
        # Check if the letter is in the word
        if guessed_letter in word:
            # Update the masked word
            self.mask_word()
            return True
        else:
            self.remaining_attempts -= 1
            return False

    def is_word_complete(self):
        return "_" not in self.masked_word

    def run(self):
        # Show start menu before the game
        self.show_start_menu()
        
        # Main game loop
        while self.running:
            self.handle_events()
            
            if not self.game_over and not self.game_won:
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
            self.screen.fill((50, 50, 100))  # Dark blue background
            
            # Title
            title = self.font.render("Spell Quest", True, (255, 255, 255))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))
            
            # Name input box
            name_prompt = self.small_font.render("Enter your name:", True, (255, 255, 255))
            self.screen.blit(name_prompt, (self.width // 2 - name_prompt.get_width() // 2, 200))
            
            # Draw input box
            input_box = pygame.Rect(self.width // 2 - 100, 250, 200, 40)
            color = (100, 100, 200) if name_input_active else (70, 70, 70)
            pygame.draw.rect(self.screen, color, input_box, 2)
            
            # Render current name input
            name_surface = self.small_font.render(name_input, True, (255, 255, 255))
            self.screen.blit(name_surface, (input_box.x + 5, input_box.y + 5))
            
            # Difficulty selection
            diff_text = self.small_font.render("Select Difficulty:", True, (255, 255, 255))
            self.screen.blit(diff_text, (self.width // 2 - diff_text.get_width() // 2, 330))
            
            for i, diff in enumerate(difficulty_options):
                color = (255, 215, 0) if i == selected_difficulty else (255, 255, 255)
                diff_option = self.small_font.render(diff.title(), True, color)
                self.screen.blit(diff_option, (self.width // 2 - diff_option.get_width() // 2, 380 + i * 40))
            
            # Start button
            start_text = self.small_font.render("Start Game", True, (0, 0, 0))
            start_rect = start_text.get_rect(center=(self.width // 2, 520))
            pygame.draw.rect(self.screen, (255, 215, 0), (start_rect.x - 10, start_rect.y - 10, 
                                                       start_rect.width + 20, start_rect.height + 20))
            self.screen.blit(start_text, start_rect)
            
            # Game instructions
            instructions = [
                "Guess the masked letters in words from different categories.",
                "Hints will appear after a while to help you.",
                "Complete as many words as you can!"
            ]
            
            for i, instruction in enumerate(instructions):
                instr_text = self.tiny_font.render(instruction, True, (255, 255, 255))
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
                            menu_running = False
                        
            pygame.display.flip()
            self.clock.tick(30)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if self.game_over or self.game_won:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                else:
                    # Check if a letter key was pressed
                    if event.unicode.isalpha():
                        letter = event.unicode.lower()
                        
                        # Only process if letter hasn't been guessed yet
                        if letter not in self.guessed_letters:
                            correct = self.update_masked_word(letter)
                            
                            if correct:
                                # Award points for correct guess
                                self.score += 10
                                
                                # Check if word is complete
                                if self.is_word_complete():
                                    # Award bonus points for completing the word
                                    self.score += 50
                                    self.words_completed += 1
                                    
                                    # Check if player has won
                                    if self.words_completed >= 10:
                                        self.game_won = True
                                        self.save_score()
                                    else:
                                        # Select a new word
                                        self.select_new_word()
                            
                            # Check if player has lost
                            if self.remaining_attempts <= 0:
                                self.game_over = True
                                self.save_score()

    def update(self):
        # Check if it's time to show a hint
        if not self.hint_shown and time.time() - self.hint_start_time >= self.hint_time:
            self.hint_shown = True

    def draw(self):
        # Draw background
        self.screen.fill((50, 50, 100))  # Dark blue
        
        # Draw scroll-like background for the word
        scroll_rect = pygame.Rect(self.width // 2 - 300, self.height // 2 - 120, 600, 240)
        pygame.draw.rect(self.screen, (245, 222, 179), scroll_rect)  # Beige color
        pygame.draw.rect(self.screen, (139, 69, 19), scroll_rect, 5)  # Brown border
        
        # Draw curly ends of scroll
        pygame.draw.circle(self.screen, (245, 222, 179), (scroll_rect.left, scroll_rect.top), 20)
        pygame.draw.circle(self.screen, (245, 222, 179), (scroll_rect.left, scroll_rect.bottom), 20)
        pygame.draw.circle(self.screen, (245, 222, 179), (scroll_rect.right, scroll_rect.top), 20)
        pygame.draw.circle(self.screen, (245, 222, 179), (scroll_rect.right, scroll_rect.bottom), 20)
        
        # Draw category
        category_text = self.small_font.render(f"Category: {self.current_category}", True, (139, 69, 19))
        self.screen.blit(category_text, (self.width // 2 - category_text.get_width() // 2, self.height // 2 - 100))
        
        # Draw masked word
        word_text = self.font.render(self.masked_word, True, (139, 69, 19))
        self.screen.blit(word_text, (self.width // 2 - word_text.get_width() // 2, self.height // 2 - 20))
        
        # Draw hint if shown
        if self.hint_shown:
            hint = self.current_word[0] + self.current_word[-1]  # First and last letter as hint
            hint_text = self.small_font.render(f"Hint: First and last letters are '{hint}'", True, (139, 69, 19))
            self.screen.blit(hint_text, (self.width // 2 - hint_text.get_width() // 2, self.height // 2 + 40))
        else:
            # Draw hint countdown
            time_to_hint = max(0, self.hint_time - (time.time() - self.hint_start_time))
            hint_countdown = self.small_font.render(f"Hint in: {int(time_to_hint)} seconds", True, (139, 69, 19))
            self.screen.blit(hint_countdown, (self.width // 2 - hint_countdown.get_width() // 2, self.height // 2 + 40))
        
        # Draw guessed letters
        guessed_text = self.small_font.render(f"Guessed: {', '.join(sorted(self.guessed_letters))}", True, (255, 255, 255))
        self.screen.blit(guessed_text, (self.width // 2 - guessed_text.get_width() // 2, self.height // 2 + 100))
        
        # Draw remaining attempts
        attempts_text = self.small_font.render(f"Attempts left: {self.remaining_attempts}", True, (255, 255, 255))
        self.screen.blit(attempts_text, (20, 20))
        
        # Draw score
        score_text = self.small_font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, 60))
        
        # Draw words completed
        words_text = self.small_font.render(f"Words: {self.words_completed}/10", True, (255, 255, 255))
        self.screen.blit(words_text, (self.width - words_text.get_width() - 20, 20))
        
        # Draw player name and difficulty
        info_text = self.tiny_font.render(f"Player: {self.player_name} | Difficulty: {self.difficulty.title()}", True, (200, 200, 200))
        self.screen.blit(info_text, (20, self.height - 30))
        
        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
            self.screen.blit(game_over_text, (self.width // 2 - game_over_text.get_width() // 2, self.height // 2 - 80))
            
            word_reveal = self.small_font.render(f"The word was: {self.current_word}", True, (255, 255, 255))
            self.screen.blit(word_reveal, (self.width // 2 - word_reveal.get_width() // 2, self.height // 2 - 30))
            
            final_score = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(final_score, (self.width // 2 - final_score.get_width() // 2, self.height // 2 + 20))
            
            restart_text = self.small_font.render("Press ENTER to play again", True, (255, 255, 255))
            self.screen.blit(restart_text, (self.width // 2 - restart_text.get_width() // 2, self.height // 2 + 70))
        
        # Game won screen
        if self.game_won:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            
            victory_text = self.font.render("YOU WIN!", True, (0, 255, 0))
            self.screen.blit(victory_text, (self.width // 2 - victory_text.get_width() // 2, self.height // 2 - 80))
            
            final_score = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(final_score, (self.width // 2 - final_score.get_width() // 2, self.height // 2 - 20))
            
            words_completed = self.small_font.render(f"Words Completed: {self.words_completed}", True, (255, 255, 255))
            self.screen.blit(words_completed, (self.width // 2 - words_completed.get_width() // 2, self.height // 2 + 20))
            
            restart_text = self.small_font.render("Press ENTER to play again", True, (255, 255, 255))
            self.screen.blit(restart_text, (self.width // 2 - restart_text.get_width() // 2, self.height // 2 + 70))
        
        pygame.display.flip()

    def reset_game(self):
        self.score = 0
        self.words_completed = 0
        self.game_over = False
        self.game_won = False
        self.set_difficulty(self.difficulty)  # Reset difficulty parameters
        self.select_new_word()

    def save_score(self):
        # Create scores directory if it doesn't exist
        if not os.path.exists("scores"):
            os.makedirs("scores")
            
        # Score file path - match the launcher's expected format
        score_file = "scores/spell_quest_scores.json"
        
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
            "difficulty": self.difficulty,
            "words_completed": self.words_completed
        })
        
        # Save scores
        with open(score_file, 'w') as f:
            json.dump(scores, f)

if __name__ == "__main__":
    game = SpellQuest()
    game.run()
