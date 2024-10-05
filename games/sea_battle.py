import random

class Battleship:
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

    def make_guess(self, x, y):
        if (x, y) in self.ship_positions:
            print(f"{self.player_name} попал!")
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

    player1 = Battleship(player1_name, board_size, ship_limits)
    player2 = Battleship(player2_name, board_size, ship_limits)

    current_player = player1
    opponent = player2
    attempts = 0
    max_attempts = 20  # Общее количество попыток

    while attempts < max_attempts and (player1.ship_positions or player2.ship_positions):
        print(f"\nХод {current_player.player_name}:")
        current_player.print_board()

        while True:
            try:
                x = int(input("Введите координату X (0-4 или 0-9): "))
                y = int(input("Введите координату Y (0-4 или 0-9): "))
            except ValueError:
                print("Пожалуйста, введите целые числа.")
                continue

            if 0 <= x < current_player.size and 0 <= y < current_player.size:
                hit = opponent.make_guess(x, y)
                if hit:
                    if not opponent.ship_positions:
                        print(f"{current_player.player_name} выиграл! Все корабли противника уничтожены!")
                        return
                break
            else:
                print("Координаты вне диапазона. Попробуйте снова.")

        current_player, opponent = opponent, current_player  # Передаем ход другому игроку
        attempts += 1

if __name__ == "__main__":
    main()
