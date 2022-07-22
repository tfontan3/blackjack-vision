import main

def compute(player,dealer):
    if player <= 8:
        main.hit()
        player, dealer = main.scan()
    if player == 9 and dealer >= 3 and dealer <= 6:
        main.main.double()
        player, dealer = main.scan()
    if player == 9 and dealer == 2 or dealer >= 7:
        main.hit()
        player, dealer = main.scan()
    if player == 10 and dealer <= 9:
        main.double()
        player, dealer = main.scan()
    if player == 11 and dealer != 11:
        main.double()
        player, dealer = main.scan()
    if player == 12 and dealer <= 3 or dealer >= 7:
        main.hit()
        player, dealer = main.scan()
    if player == 12 and dealer >= 4 and dealer <= 6:
        main.stand()
    if player >= 13:
        main.hit()
        player, dealer = main.scan()