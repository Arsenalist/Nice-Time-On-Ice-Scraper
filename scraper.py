import urllib2
import argparse

from bs4 import BeautifulSoup

# Gets the content from a URL
def get_html(url):
    response = urllib2.urlopen(url)
    r = response.read()
    return r


# Gets the tables on a page as a list of lists where each list 
# is a row and each element in that row is a column (skips headings)
def generic_table_parse(url):
    html = get_html(url)
    soup = BeautifulSoup(html)
    tables = soup.find_all('table')
    rows = []
    for table in tables:
        trs = table.find_all('tr')
        trs.pop(0)
        for tr in trs:
            tds = tr.find_all('td')
            columns = []
            for td in tds:
                if td.b:
                    td.b.unwrap()
                if td.center:
                    td.center.unwrap()
                columns.append(td.string)
            rows.append(columns)
    return rows

# Print rows to sandard out as comma-delimited, double-quote enclosed fields
def print_rows(rows):
    for row in rows:
        s = ''
        for idx, col in enumerate(row):
            s += "\"%s\"" % col
            if idx != len(row) - 1:
                s += ","
        print s



def fenwick_corsi(start_id, end_id):
    url = 'http://www.timeonice.com/shots1213.php?gamenumber='
    for x in range (start_id, end_id + 1):
        urlx = url + str(x)
        rows = generic_table_parse(urlx)
        print_rows(rows)


# gets the zone starts as a list of lists (each list is a row and each element in that row is a column)
def zone_starts(start_id, end_id):
    url = 'http://www.timeonice.com/faceoffs1213.php?gamenumber='
    for x in range (start_id, end_id + 1):
        urlx = url + str(x)
        rows = generic_table_parse(urlx)
    
        # append game id at the start of each row
        for r in rows:
            r.insert(0, x)
        
        print_rows(rows)

            
def main():
    # command line parser
    p = argparse.ArgumentParser(description='NHL Stats Puller.')
    p.add_argument('-p', '--page', help='Page type to read from ', choices=['fenwick-corsi', 'zone-starts'], required=True)
    p.add_argument('-s', '--start-game-id', type=int, required=True)
    p.add_argument('-e', '--end-game-id', type=int, required=True)
    args = vars(p.parse_args())
    
    # call one of the methods using the game ids
    page = args['page']
    start_game_id = args['start_game_id']
    end_game_id = args['end_game_id']
    if page == 'fenwick-corsi':
        fenwick_corsi(start_game_id, end_game_id)
    elif page == 'zone-starts':
        zone_starts(start_game_id, end_game_id)

if __name__ == '__main__':
    main()

