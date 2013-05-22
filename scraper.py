import urllib2
import argparse

from bs4 import BeautifulSoup, element


# Gets the content from a URL
def get_html(url):
    response = urllib2.urlopen(url)
    return response.read()


# Gets the tables on a page as a list of lists where each list 
# is a row and each element in that row is a column (skips headings)
def generic_table_parse(url, skip_header=True, table_no=None):
    html = get_html(url)
    soup = BeautifulSoup(html)
    tables = soup.find_all('table')

    # create a list of one table if we're targetting a table
    if table_no:
        tables = [tables[table_no-1]]
    rows = []
    for table in tables:
        trs = table.find_all('tr')

        # pop header if need be
        if skip_header:
            trs.pop(0)
        
        for tr in trs:
            tds = tr.find_all('td')
            columns = []
            for td in tds:
                s = ''
                # filter out string descendants
                str_descendants = [x for x in td.descendants if isinstance(x, element.NavigableString)]

                # append strings together
                for idx, x in enumerate(str_descendants):
                    s = s + x
                    if idx != len(str_descendants) - 1:
                        s = s + " "
                columns.append(s)
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


# pulls the Fenwick-Corsi stats
def fenwick_corsi(start_id, end_id):
    url = 'http://www.timeonice.com/shots1213.php?gamenumber='
    for x in range (start_id, end_id + 1):
        urlx = url + str(x)
        rows = generic_table_parse(urlx)
        print_rows(rows)


# Gets the zone starts as a list of lists (each list is a row and each element in that row is a column)
def zone_starts(start_id, end_id):
    url = 'http://www.timeonice.com/faceoffs1213.php?gamenumber='
    for x in range (start_id, end_id + 1):
        urlx = url + str(x)
        rows = generic_table_parse(urlx)
    
        prepend_column(rows, x)
        print_rows(rows)


# Gets the head-to-heads as:
#   row_player, column_player, stat
def head_to_head(start_id, end_id):
    url = 'http://timeonice.com/H2H1213.html?submit=Go&GameNumber='
    for x in range (start_id, end_id + 1):
        urlx = url + str(x)
        rows = generic_table_parse(urlx, False, 1)
        rows = simplify_head_to_head(rows)
        prepend_column(rows, x)
        print_rows(rows)

        rows = generic_table_parse(urlx, False, 2)
        rows = simplify_head_to_head(rows)
        prepend_column(rows, x)
        print_rows(rows)


def prepend_column(rows, col_value):
    # append game id at the start of each row
    for r in rows:
        r.insert(0, col_value)

    

def simplify_head_to_head(rows):
    # first three tds of header row are blank
    col_player_names = rows[0][3:]

    # get rid of player names header now that we got the names out
    rows.pop(0)
    simple_rows = []
    for idx, r in enumerate(rows):
        # delete blank column
        del r[2]

        for col_idx, p in enumerate(col_player_names):
            one_row = []
            # add row player
            one_row.append(r[0] + " " + r[1])
            # add column player
            one_row.append(p)
            # add stat value
            one_row.append(r[2 + col_idx])
            simple_rows.append(one_row)
    return simple_rows        


def main():
    # command line parser
    p = argparse.ArgumentParser(description='NHL Stats Puller.')
    p.add_argument('-p', '--page', help='Page type to read from ', choices=['fenwick-corsi', 'zone-starts', 'head-to-head'], required=True)
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
    elif page == 'head-to-head':
        head_to_head(start_game_id, end_game_id)

if __name__ == '__main__':
    main()

