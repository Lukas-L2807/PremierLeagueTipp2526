from modules.calc_tables.CalcTable import calc_table
from modules.create_html.CreateHtml import make_html_from_json

def main():
    calc_table()
    make_html_from_json()

if __name__ == "__main__":
    main()