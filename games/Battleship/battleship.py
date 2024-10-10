import random

class BattleshipSession:
    def __init__(self, player1_name, player2_name, board_size, ship_limits):
        self.player1 = BattleshipBoard(player1_name, board_size, ship_limits)
        self.player2 = BattleshipBoard(player2_name, board_size, ship_limits)
        self.current_player = self.player1
        self.opponent = self.player2
        self.attempts = 0
        self.max_attempts = 20  # Общее количество попыток

    def process_turn(self, x, y):
        hit = self.opponent.make_guess(x, y, self.current_player)

        # Передаем ход другому игроку
        self.current_player, self.opponent = self.opponent, self.current_player
        self.attempts += 1

        return hit

    def is_game_over(self):
        if self.attempts < self.max_attempts:
            if self.player1.ship_positions and self.player2.ship_positions:
                return False
        return True


class BattleshipBoard:
    def __init__(self, player_name, board_size, ship_limits):
        self.player_name = player_name
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

    def print_board(self):
        print(f"Доска игрока {self.player_name}:")
        for row in self.board:
            print(' '.join(row))
        print()

    def make_guess(self, x, y, attacker):
        if (x, y) in self.ship_positions:
            print(f"{attacker.player_name} попал!")
            self.board[x][y] = 'X'  # Замена на 'X' при попадании
            self.ship_positions.remove((x, y))
            if not any(pos[0] == x and pos[1] == y for pos in self.ship_positions):  # Проверка на уничтожение корабля
                print(f"Корабль игрока {self.player_name} уничтожен!")
            return True  # Попадание
        else:
            print("Мимо!")
            self.board[x][y] = 'O'  # Замена на 'O' при промахе
            return False  # Мимо

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
        current_player = session.current_player
        print(session.player1.ship_positions, session.player2.ship_positions)
        print(f"\nХод {current_player.player_name}:")
        current_player.print_board()

        while True:
            try:
                x = int(input("Введите координату X (0-4 или 0-9): "))
                y = int(input("Введите координату Y (0-4 или 0-9): "))
            except ValueError:
                print("Пожалуйста, введите целые числа.")
                continue
            if (0 <= x < current_player.size) and (0 <= y < current_player.size):
                break
            else:
                print("Координаты вне диапазона. Попробуйте снова.")

        session.process_turn(x, y)
    
    print(f"{current_player.player_name} выиграл! Все корабли противника уничтожены!")

if __name__ == "__main__":
    main()
