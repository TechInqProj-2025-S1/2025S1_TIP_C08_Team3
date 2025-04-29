class GameManager:
    def __init__(self, screen):
        self.screen = screen
        self.games = {
            "Game 1": "games.game1.game1",
            "Game 2": "games.game2.game2",
            "Game 3": "games.game3.game3",
            "Game 4": "games.game4.game4",
            "Game 5": "games.game5.game5",
            "Game 6": "games.game6.game6"
        }
        self.current_game = None

    def launch_game(self, game_name):
        if game_name in self.games:
            game_module = __import__(self.games[game_name], fromlist=[''])
            game_module.run(self.screen)

    def get_game_list(self):
        return list(self.games.keys())