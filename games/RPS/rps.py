import random, time

comp_turn = ['k','n','b']
count = [0,0]

def reset_score():
    global count
    count = [0,0]

def knb_choice(t):
    if t == 'k':
        return 'камень'
    elif t == 'b':
        return 'бумага'
    elif t == 'n':
        return 'ножницы'

def determine_winner(turn, c_turn):
    if (turn == 'k' and c_turn == 'n') or (turn == 'n' and c_turn == 'b') or (turn == 'b' and c_turn == 'k'):
        count[0] += 1
        return 'Ты выиграл'
    if (turn == 'n' and c_turn == 'k') or (turn == 'b' and c_turn == 'n') or (turn == 'k' and c_turn == 'b'):
        count[1] += 1
        return 'Я выиграл'

def bot_choice():
    time.sleep(0.5)
    return random.choice(comp_turn)

def player_choice(choice):
    return choice

def main():
    gameloop = True
    while gameloop:
        choice = input('k - камень, n - ножницы, b - бумага, exit - выход')
        p_turn = player_choice(choice)
        print()

        if p_turn == 'exit':
            print('выход')
            gameloop = False
        else:
            c_turn = bot_choice()
            print(knb_choice(p_turn))
            print(knb_choice(c_turn))
            print(determine_winner(p_turn, c_turn))
            
if __name__ == '__main__':
    main()