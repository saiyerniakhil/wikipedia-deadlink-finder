from flask import render_template, Flask, request
import requests,re, csv, time
from bs4 import BeautifulSoup

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

app = Flask(__name__)

def listify(filename):
    input_wikilink_list = []
    firstColumn = []
    with open(filename) as f:
        for line in f:
            #if line.split(',')[0] != '\n':
            firstColumn.append(line.split(',')[0])
    return firstColumn


def url_validation(link):
    urlregex = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    return re.match(urlregex, str(link)) is not None

def deadLinkFinder(url):

    linkset = []
    first_column = []
    urls = []
    valid_urls = []
    dead_links = []
    conn_refused = []
    forbidden_urls = []

    first_column = listify('links.csv')
    if(str(url) in first_column):
        pos = first_column.index(str(url))

        with open('links.csv','r') as f:
            readcsv = list(csv.reader(f,delimiter=','))
            req_row = readcsv[pos]
        #print('Dead links:')
        try:
            for k in range(1,len(req_row) + 1):
                #print("* ",req_row[k])
                dead_links.append(req_row[k])
        except IndexError:
            print("")
    else:
        page = requests.get(str(url))  # The URL is of our choice
        
        soup = BeautifulSoup(page.content, 'html.parser')
        linkset = soup.find_all('a')

        # To get the href from the collected Hyperlinks
        for i in linkset:
            urls.append(i.get('href'))

        # Applying URL validation and Holding together all the valid URLs in a list.
        for i in urls:
            if url_validation(i):
                valid_urls.append(i)
        """
        Making request to all the valid URLs.
        If the URL gives us a status-code, 200. Then it's a Dead Link. 
        If the URL gives us a status-code, 403. Then its a Forbidden Link.

        """
        #print("Dead Links: ")
        for i in valid_urls:
            try:
                temp_page = requests.get(i, verify=False)
                if (temp_page.status_code == 403):
                    forbidden_urls.append(i)
                elif not (temp_page.status_code == 200):
                #print("* ", i)
                    dead_links.append(i)
            except:
                conn_refused.append(i)
            

        if len(dead_links) != 0:
            with open('links.csv', mode='a') as deadlinks:
                deadlink_writer = csv.writer(deadlinks, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                deadlink_writer.writerow([str(url)]+dead_links)

    return dead_links

        # Finally printing out all the Dead Links,Forbidden Links and the URLs that are taking too long to respond.

#        if len(dead_links) == 0:
#            print("No Dead links found.")
#        else:
#            with open('links.csv',mode='w') as deadlinks:
#                deadlink_writer = csv.writer(deadlinks,delimiter=',',quotechar='"',quoting=csv.QUOTE_MINIMAL)
#                deadlink_writer.writerow([str(url)]+dead_links)

 #           print("Number of Dead links: ", len(dead_links))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/view",methods=['POST', 'GET'])
def view():
    if request.method == 'GET' :
        return "Please submit the form"
    else:
        url = request.form.get('link_to')
        start_time = time.time()
        data = deadLinkFinder(url)
        end_time = time.time() - start_time
        total_number = len(data)
        return render_template('output.html',data = data, time_taken = end_time,total=total_number)


