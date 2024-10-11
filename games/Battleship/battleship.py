import random

class BattleshipSession:
    def __init__(self, player1_name, player2_name, board_size, ship_limits):
        self.player1 = BattleshipPlayer(player1_name, board_size, ship_limits)
        self.player2 = BattleshipPlayer(player2_name, board_size, ship_limits)
        self.current_player = self.player1
        self.opponent = self.player2
        self.attempts = 0
        self.max_attempts = 20  # Общее количество попыток

    def validate_input(self, x, y):
        try:
            x = int(x)
            y = int(y)
        except ValueError:
            return "Пожалуйста, введите целые числа."
        if (0 <= x < self.current_player.size) and (0 <= y < self.current_player.size):
            return None # Отсутствие сообщения об ошибке
        else:
            return "Координаты вне диапазона. Попробуйте снова."

    def process_turn(self, x, y):
        x, y = int(x), int(y)
        hit, hit_text = self.opponent.make_guess(x, y, self.current_player)
        # Передаем ход другому игроку
        self.current_player, self.opponent = self.opponent, self.current_player
        self.attempts += 1
        return hit, hit_text

    def is_game_over(self):
        if self.attempts < self.max_attempts:
            if self.player1.ship_positions and self.player2.ship_positions:
                return False
        return True


class BattleshipPlayer:
    def __init__(self, name, board_size, ship_limits):
        self.name = name
        self.size = board_size
        self.board = [['~'] * self.size for _ in range(self.size)]
        self.ship_positions = set()
        self.ship_limits = ship_limits
        self.place_ships()

    def place_ships(self):
        # Размещение кораблей с учетом ограничений
        for ship_size in [4, 2, 1]:  # Сначала размещаем большие корабли
            for _ in range(self.ship_limits[ship_size]):
                placed = False
                while not placed:
                    orientation = random.choice(['horizontal', 'vertical'])
                    if orientation == 'horizontal':
                        x = random.randint(0, self.size - 1)
                        y = random.randint(0, self.size - ship_size)
                        if self.can_place_ship(x, y, ship_size, orientation):
                            for i in range(ship_size):
                                self.ship_positions.add((x, y + i))
                            placed = True
                    else:
                        x = random.randint(0, self.size - ship_size)
                        y = random.randint(0, self.size - 1)
                        if self.can_place_ship(x, y, ship_size, orientation):
                            for i in range(ship_size):
                                self.ship_positions.add((x + i, y))
                            placed = True

    def can_place_ship(self, x, y, ship_size, orientation):
        # Проверка возможности размещения корабля с учетом расстояния
        for i in range(ship_size):
            if orientation == 'horizontal':
                if (x, y + i) in self.ship_positions or \
                   (x, y + i - 1) in self.ship_positions or \
                   (x, y + i + 1) in self.ship_positions:
                    return False
            else:
                if (x + i, y) in self.ship_positions or \
                   (x + i - 1, y) in self.ship_positions or \
                   (x + i + 1, y) in self.ship_positions:
                    return False
        return True

    def render_board(self):
        lines = []
        for row in self.board:
            lines.append(' '.join(row))
        board = '\n'.join(lines)
        return f"Доска игрока {self.name}:\n{board}"

    def make_guess(self, x, y, attacker):
        result_message = ''
        if (x, y) in self.ship_positions:
            result_message += f"{attacker.name} попал!\n"
            self.board[x][y] = 'X'  # Замена на 'X' при попадании
            self.ship_positions.remove((x, y))
            if not any(pos[0] == x and pos[1] == y for pos in self.ship_positions):  # Проверка на уничтожение корабля
                result_message += f"Корабль игрока {self.name} уничтожен!\n"
            return True, result_message  # Попадание
        else:
            result_message += "Мимо!\n"
            self.board[x][y] = 'O'  # Замена на 'O' при промахе
            return False, result_message  # Мимо

def main():
    player1_name = input("Введите имя Игрока 1: ")
    player2_name = input("Введите имя Игрока 2: ")

    while True:
        board_size_option = input("Выберите размер карты (5x5 или 10x10): ")
        if board_size_option == "5x5":
            board_size = 5
            ship_limits = {4: 0, 2: 1, 1: 3}  # Максимальное количество кораблей
            break
        elif board_size_option == "10x10":
            board_size = 10
            ship_limits = {4: 1, 2: 3, 1: 5}
            break
        else:
            print("Неверный выбор. Пожалуйста, выберите '5x5' или '10x10'.")

    session = BattleshipSession(player1_name, player2_name, board_size, ship_limits)

    while not session.is_game_over():
        print(f"\nХод {session.current_player}:\n")
        print(session.opponent.render_board())

        while True:
            x = input("Введите координату X (0-4 или 0-9): ")
            y = input("Введите координату Y (0-4 или 0-9): ")
            error_message = session.validate_input(x, y)
            print(error_message)
            if error_message is None:
                break

        hit, hit_text = session.process_turn(x, y)
        print(hit_text)
    
    print(f"{session.opponent.name} выиграл! Все корабли противника уничтожены!")

if __name__ == "__main__":
    main()
