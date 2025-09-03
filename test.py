from modules.get_data.getPremierLeagueTable import get_premier_league_table

def main():
    html = 'https://www.premierleague.com/tables'
    table = get_premier_league_table(html)
    print(table)

if __name__ == "__main__":
    main()