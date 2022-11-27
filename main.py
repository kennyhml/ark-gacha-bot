from bot.gacha_bot import GachaBot

if __name__ == "__main__":
    bot = GachaBot()
    while True:
        bot.do_next_task()