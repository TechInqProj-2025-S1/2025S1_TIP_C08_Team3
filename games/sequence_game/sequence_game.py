import pygame
import random
import os
import json
import time

class SequenceGame:
    def __init__(self, difficulty="medium"):
        pygame.init()
        self.width, self.height = 800, 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Sequence Game")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Game settings
        self.difficulty = difficulty  # "easy", "medium", "hard"
        self.score = 0
        self.player_name = "Player"
        self.round = 1
        self.max_rounds = 10
        self.time_per_round = 20  # seconds per round
        self.remaining_time = self.time_per_round
        self.last_time_check = time.time()
        
        # Sequence settings
        self.sequence = []
        self.answer_index = -1
        self.player_answer = ""
        self.correct_answer = None
        self.result = None  # "correct" or "incorrect"
        
        # Set up fonts
        self.font = pygame.font.SysFont(None, 48)
        self.medium_font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Set difficulty parameters and generate first sequence
        self.set_difficulty(difficulty)
        self.generate_sequence()

    def set_difficulty(self, difficulty):
        if difficulty == "easy":
            self.sequence_length = 5
            self.max_value = 10
            self.sequence_types = ["arithmetic"]  # Only simple arithmetic progressions
            self.time_per_round = 30
        elif difficulty == "medium":
            self.sequence_length = 7
            self.max_value = 50
            self.sequence_types = ["arithmetic", "geometric"]
            self.time_per_round = 25
        elif difficulty == "hard":
            self.sequence_length = 9
            self.max_value = 100
            self.sequence_types = ["arithmetic", "geometric", "fibonacci"]
            self.time_per_round = 20
            
        self.remaining_time = self.time_per_round

    def generate_sequence(self):
        sequence_type = random.choice(self.sequence_types)
        
        if sequence_type == "arithmetic":
            # Arithmetic progression: a, a+d, a+2d, a+3d, ...
            start = random.randint(1, self.max_value // 2)
            difference = random.randint(1, 10)
            self.sequence = [start + i * difference for i in range(self.sequence_length)]
            
        elif sequence_type == "geometric":
            # Geometric progression: a, ar, ar², ar³, ...
            start = random.randint(1, 10)
            ratio = random.randint(2, 3)  # Using small ratios to avoid huge numbers
            self.sequence = [start * (ratio ** i) for i in range(self.sequence_length)]
            
        elif sequence_type == "fibonacci":
            # Fibonacci-like sequences: Each number is the sum of the two preceding ones
            # Using a randomized starting pair
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            self.sequence = [a, b]
            for i in range(2, self.sequence_length):
                self.sequence.append(self.sequence[i-1] + self.sequence[i-2])
        
        # Choose a random position to hide (not the first or last for simplicity)
        self.answer_index = random.randint(1, self.sequence_length - 2)
        self.correct_answer = str(self.sequence[self.answer_index])
        self.sequence[self.answer_index] = "?"
        self.player_answer = ""

    def run(self):
        # Show start menu before the game
        self.show_start_menu()
        
        # Main game loop
        while self.running:
            self.handle_events()
            
            if self.round <= self.max_rounds:
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
            self.screen.fill((25, 25, 50))  # Dark blue/purple background
            
            # Title
            title = self.font.render("Sequence Game", True, (255, 255, 255))
            self.screen.blit(title, (self.width // 2 - title.get_width() // 2, 100))
            
            # Name input box
            name_prompt = self.medium_font.render("Enter your name:", True, (255, 255, 255))
            self.screen.blit(name_prompt, (self.width // 2 - name_prompt.get_width() // 2, 200))
            
            # Draw input box
            input_box = pygame.Rect(self.width // 2 - 100, 250, 200, 40)
            color = (100, 100, 200) if name_input_active else (70, 70, 70)
            pygame.draw.rect(self.screen, color, input_box, 2)
            
            # Render current name input
            name_surface = self.medium_font.render(name_input, True, (255, 255, 255))
            self.screen.blit(name_surface, (input_box.x + 5, input_box.y + 5))
            
            # Difficulty selection
            diff_text = self.medium_font.render("Select Difficulty:", True, (255, 255, 255))
            self.screen.blit(diff_text, (self.width // 2 - diff_text.get_width() // 2, 330))
            
            for i, diff in enumerate(difficulty_options):
                color = (0, 255, 0) if i == selected_difficulty else (255, 255, 255)
                diff_option = self.medium_font.render(diff.title(), True, color)
                self.screen.blit(diff_option, (self.width // 2 - diff_option.get_width() // 2, 380 + i * 40))
            
            # Start button
            start_text = self.medium_font.render("Start Game", True, (0, 0, 0))
            start_rect = start_text.get_rect(center=(self.width // 2, 520))
            pygame.draw.rect(self.screen, (0, 255, 0), (start_rect.x - 10, start_rect.y - 10, 
                                                     start_rect.width + 20, start_rect.height + 20))
            self.screen.blit(start_text, start_rect)
            
            # Game instructions
            instructions = [
                "Find the missing number in each sequence.",
                "The sequences follow mathematical patterns.",
                "Complete 10 rounds to win!",
                "Higher difficulties include more complex patterns."
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
                if self.round > self.max_rounds:  # Game over state
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                else:
                    if event.key == pygame.K_RETURN:
                        self.check_answer()
                    elif event.key == pygame.K_BACKSPACE:
                        self.player_answer = self.player_answer[:-1]
                    elif event.unicode.isdigit() or event.unicode == '-':
                        # Only allow digits and minus sign
                        self.player_answer += event.unicode

    def check_answer(self):
        if not self.player_answer:  # No answer provided
            return
            
        if self.player_answer == self.correct_answer:
            self.result = "correct"
            
            # Award points based on remaining time and difficulty
            time_bonus = int(self.remaining_time / self.time_per_round * 10)
            difficulty_multiplier = {"easy": 1, "medium": 2, "hard": 3}[self.difficulty]
            points = (10 + time_bonus) * difficulty_multiplier
            self.score += points
            
            # Wait a moment to show the result, then move to next round
            pygame.time.delay(1000)  # 1 second delay
            self.round += 1
            
            if self.round <= self.max_rounds:
                self.generate_sequence()
                self.remaining_time = self.time_per_round
                self.last_time_check = time.time()
            else:
                # Game completed
                self.save_score()
        else:
            self.result = "incorrect"
            # Penalty for wrong answers
            self.score = max(0, self.score - 5)
            
            # Show the error briefly
            pygame.time.delay(1000)  # 1 second delay
            self.result = None

    def update(self):
        current_time = time.time()
        time_passed = current_time - self.last_time_check
        self.remaining_time -= time_passed
        self.last_time_check = current_time
        
        # Check if time ran out
        if self.remaining_time <= 0:
            self.remaining_time = 0
            self.result = "timeout"
            # Apply penalty for timeout
            self.score = max(0, self.score - 3)
            
            # Move to next round after a delay
            pygame.time.delay(1000)  # 1 second delay
            self.round += 1
            
            if self.round <= self.max_rounds:
                self.generate_sequence()
                self.remaining_time = self.time_per_round
                self.last_time_check = time.time()
            else:
                # Game completed
                self.save_score()

    def draw(self):
        # Draw background with a mathematical/logical theme
        self.screen.fill((25, 25, 50))  # Dark blue/purple
        
        # Draw grid lines in background
        for i in range(0, self.width, 40):
            pygame.draw.line(self.screen, (40, 40, 70), (i, 0), (i, self.height), 1)
        for i in range(0, self.height, 40):
            pygame.draw.line(self.screen, (40, 40, 70), (0, i), (self.width, i), 1)
        
        if self.round <= self.max_rounds:
            # Draw round information
            round_text = self.medium_font.render(f"Round: {self.round}/{self.max_rounds}", True, (255, 255, 255))
            self.screen.blit(round_text, (20, 20))
            
            # Draw time remaining
            time_text = self.medium_font.render(f"Time: {int(self.remaining_time)}s", True, (255, 255, 255))
            self.screen.blit(time_text, (self.width - time_text.get_width() - 20, 20))
            
            # Draw score
            score_text = self.medium_font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (20, 70))
            
            # Draw sequence
            sequence_text = self.font.render(" ".join(str(num) for num in self.sequence), True, (255, 255, 0))
            self.screen.blit(sequence_text, (self.width // 2 - sequence_text.get_width() // 2, self.height // 2 - 80))
            
            # Draw prompt
            prompt_text = self.medium_font.render("Find the missing number:", True, (255, 255, 255))
            self.screen.blit(prompt_text, (self.width // 2 - prompt_text.get_width() // 2, self.height // 2 - 20))
            
            # Draw input box
            input_box = pygame.Rect(self.width // 2 - 100, self.height // 2 + 20, 200, 50)
            pygame.draw.rect(self.screen, (50, 50, 70), input_box)
            pygame.draw.rect(self.screen, (200, 200, 200), input_box, 2)
            
            # Draw player's answer
            if self.player_answer:
                answer_text = self.font.render(self.player_answer, True, (255, 255, 255))
                self.screen.blit(answer_text, (input_box.x + 20, input_box.y + 10))
            
            # Draw instruction
            instruction = self.small_font.render("Enter your answer and press Enter", True, (200, 200, 200))
            self.screen.blit(instruction, (self.width // 2 - instruction.get_width() // 2, self.height // 2 + 90))
            
            # Draw result feedback
            if self.result == "correct":
                result_text = self.medium_font.render("Correct!", True, (0, 255, 0))
                self.screen.blit(result_text, (self.width // 2 - result_text.get_width() // 2, self.height // 2 + 130))
            elif self.result == "incorrect":
                result_text = self.medium_font.render(f"Incorrect! The answer was {self.correct_answer}", True, (255, 0, 0))
                self.screen.blit(result_text, (self.width // 2 - result_text.get_width() // 2, self.height // 2 + 130))
            elif self.result == "timeout":
                result_text = self.medium_font.render(f"Time's up! The answer was {self.correct_answer}", True, (255, 165, 0))
                self.screen.blit(result_text, (self.width // 2 - result_text.get_width() // 2, self.height // 2 + 130))
        else:
            # Game over screen - all rounds completed
            game_over_text = self.font.render("Game Complete!", True, (0, 255, 0))
            self.screen.blit(game_over_text, (self.width // 2 - game_over_text.get_width() // 2, self.height // 2 - 100))
            
            final_score = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(final_score, (self.width // 2 - final_score.get_width() // 2, self.height // 2 - 40))
            
            difficulty_text = self.medium_font.render(f"Difficulty: {self.difficulty.title()}", True, (255, 255, 255))
            self.screen.blit(difficulty_text, (self.width // 2 - difficulty_text.get_width() // 2, self.height // 2 + 20))
            
            restart_text = self.medium_font.render("Press ENTER to play again", True, (255, 255, 255))
            self.screen.blit(restart_text, (self.width // 2 - restart_text.get_width() // 2, self.height // 2 + 80))
        
        # Draw player name and difficulty
        info_text = self.small_font.render(f"Player: {self.player_name} | Difficulty: {self.difficulty.title()}", True, (200, 200, 200))
        self.screen.blit(info_text, (20, self.height - 30))
        
        pygame.display.flip()

    def reset_game(self):
        self.score = 0
        self.round = 1
        self.set_difficulty(self.difficulty)
        self.generate_sequence()
        self.result = None

    def save_score(self):
        # Create scores directory if it doesn't exist
        if not os.path.exists("scores"):
            os.makedirs("scores")
            
        # Score file path - match the launcher's expected format
        score_file = "scores/sequence_game_scores.json"
        
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
            "rounds_completed": self.round - 1
        })
        
        # Save scores
        with open(score_file, 'w') as f:
            json.dump(scores, f)

if __name__ == "__main__":
    game = SequenceGame()
    game.run()
