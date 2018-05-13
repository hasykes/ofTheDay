#Word of the Day (WOTD) + Friends Data Puller
# -*- coding: utf-8 -*-
import sys
import urllib.request as ul
from bs4 import BeautifulSoup as bs
import datetime as dt
import spotipy as spot
import spotipy.util as util
import webbrowser as webb


import os
from jinja2 import Environment, FileSystemLoader
 
PATH = os.path.dirname(os.path.abspath(__file__)) #set path to current directory
TEMPLATE_ENVIRONMENT = Environment( 
    autoescape=False,
    loader=FileSystemLoader(os.path.join(PATH, 'templates')),
    trim_blocks=False) #initialize jinja2 environment for template parsing

now = dt.datetime.now()

def replace_all(text, dic): #replace all function for formatting help
    for i, j in dic.items():
        text = text.replace(i, j)
    return text
    
def find_between( s, first, last ):
    try:
        start = s.rindex( first ) + len( first )
        end = s.rindex( last, start )
        return s[start:end]
    except ValueError:
        return ""
        
def webReq(src): #general function for web Requests
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'}
    req = ul.Request(src,data=None,headers=hdr)
    
    htmlRequest = ul.urlopen(req)

    soup = bs(htmlRequest,'html.parser')
    return soup
        
def wotd(): #WOTD function
    src = 'http://www.dictionary.com/wordoftheday/'
    soup = webReq(src)
    
    #dictLogoSrc = 'http://www.dictionary.com/drc/img/responsive/dcom-logo-8f31c.png' #requires blue background hex #428bca

    defWrap = soup.find(attrs={"class":"definition-box"}) #definition Wrapper
    citWrap = soup.find(attrs={"class":"citation-context"})#citation Wrapper
    
    wotd = defWrap.find('strong').contents[0] # Pull WOTD from strong tag
    
    defRawList = defWrap.find_all('span')#pull content from spans within definition list
    defEmText = defWrap.find_all('em')#pull origin from emphasis tags
    
    defList = [] # initialize blank definition list
    defDict= {} # initialize blank dictionary
    
    #create a dictionary for custom replace_all function -> 
    for emText in defEmText:
            defDict[emText.text] = ('<em>'+emText.text+'</em>')
            
    for definition in defRawList: #Pull definitions to list
            definition = replace_all(definition.text, defDict)
            defList.append(definition)
            
    blockRawList = citWrap.find('blockquote')
    quoteSpanList = blockRawList.find_all('span')
    quoteRawText = quoteSpanList[0].text #pull raw text from Span List
    quoteHtmlText = quoteRawText.replace(wotd,'<strong>'+wotd+'</strong>') #add strong tag for WOTD Emphasis
    
    citList = '-- ' + blockRawList.find(attrs={"class":"author"}).text #.split(',') -> if needed to split text into Commas

    #----------------------------------Get more info on the word------------------------------------------------------
    
    src='http://www.dictionary.com/browse/'+ wotd.replace(' ','%20')
    soup = webReq(src)
    
    pronounce = soup.find(attrs={"class":"ipapron"}).text
    partOS = soup.find(attrs={"class":"dbox-pg"}).text

    todaysWordDict = {'wotdWord':wotd,'wotdDefines':defList,'wotdQuote':quoteHtmlText,'wotdCite':citList,'wotdPos':partOS,'wotdPronounce':pronounce}		

    # print('WOTD:')
    # print(wotd)
    # print(pronounce)
    # print(partOS)
    # print(defList)
    # print(quoteHtmlText)
    # print(citList)
    # print(todaysWordDict)
    # print('----------------------------------------------------------------')

    return todaysWordDict
    #Wordnik API for future definitions????
    #https://github.com/wordnik/wordnik-python

def apod(): # pull info from NASA astronomy photo of the Day
    src = 'https://apod.nasa.gov/apod/astropix.html'
    soup = webReq(src)
    
    img = soup.find('img')
    if img is None:
        cType = 'Video'
        vid = soup.find('iframe')
        imgSrc = vid['src']
        imgID = find_between(imgSrc,'/','?')
        imgLink = 'https://img.youtube.com/vi/' + imgID + '/hqdefault.jpg'
    else:  
        cType = 'Photo'
        imgSrc = 'https://apod.nasa.gov/apod/' + img['src']
        imgLink =  'https://apod.nasa.gov/apod/' + img['src']
    
    centerTags = soup.find_all('center')
    title = centerTags[1].b.text #need to figure out formatting as of 2018/03/30
    citeRawText = centerTags[1].text
    citeLinks = centerTags[1].find_all('a')
    
    citeDict = {'\n':'',title:''} #create dictionary for replace_all function. initialize \n to remove new space characters
    
    
    for link in citeLinks: #build dictionary of citations and their tags
            citeDict[link.text] = (str(link))
            
    citeText = replace_all(citeRawText, citeDict) #replace text in string based on dictionary
    
    apod = {'apodSrc':imgSrc,'apodLink':imgLink,'apodTitle':title,'apodCite':citeText,'apodType':cType}
    return apod
    
    # print(imgSrc)
    # print(title)
    # print(citeText)
    # print('-----------------------------------------------------------')

def sotd(): #Song of the Day using Spotipy API -- http://spotipy.readthedocs.io/en/latest/
    import json
    import configparser

    config = configparser.ConfigParser()
    config.read(PATH+'/config/config.ini')


    sotdConfig = config['sotd']
    username = sotdConfig['username']
    playlist1 = sotdConfig['playlist1']
    playlist2 = sotdConfig['playlist2']

    scope = 'user-library-read'
    token = util.prompt_for_user_token(username,scope,client_id=sotdConfig['client_id'],client_secret=sotdConfig['client_secret'],redirect_uri=sotdConfig['redirect_uri'])
    
    playList = [playlist1,playlist2] #hahahahahaha
    
    if token: #Check if I get a valid token from Spotify. Not really valid for my needs but might as well.
        sotdUser = 0
        sotdDict = {}
        for playID in playList:
            sp = spot.Spotify(auth=token)
            #-------------------------------------Actual Queries Executed here-----------------------------------------
            results = sp.user_playlist(username,playlist_id=playID)#returns JSON structured data
        
            #print(json.dumps(results['tracks']['items'][1]['track'],indent=4))
            
            trackNames = []
            trackLinks = []
            albumList = []
            albumArts = []
            albumLinks = []
            artistList = []
            artistLinks = []
            explicitList = []
            
            
           # for i in range(0,len(results['tracks']['items'])):
            trackNames.append(results['tracks']['items'][-1]['track']['name']) # create Track Name list
            trackLinks.append(results['tracks']['items'][-1]['track']['external_urls']['spotify']) #create Track Link List
            
            artistList.append(results['tracks']['items'][-1]['track']['album']['artists'][0]['name'])  #create Album Art List
            artistLinks.append(results['tracks']['items'][-1]['track']['album']['artists'][0]['external_urls']['spotify'])  #create Album Art List
            
            albumList.append(results['tracks']['items'][-1]['track']['album']['name'])  #create Album Names List
            albumArts.append(results['tracks']['items'][-1]['track']['album']['images'][1]['url'])  #create Album Art List
            albumLinks.append(results['tracks']['items'][-1]['track']['album']['external_urls']['spotify']) #create Album Link List
           
            if results['tracks']['items'][-1]['track']['explicit'] == True: 
                explicitList.append('EXPLICIT') # create Explicit List
            else:
                explicitList.append('')
            
            userDict = {
                'sotdTrack'+str(sotdUser):trackNames[-1],
                'sotdTrackLink'+str(sotdUser):trackLinks[-1],
                'sotdAlbum'+str(sotdUser):albumList[-1],
                'sotdAlbumArt'+str(sotdUser):albumArts[-1],
                'sotdAlbumLink'+str(sotdUser):albumLinks[-1],
                'sotdArtist'+str(sotdUser):artistList[-1],
                'sotdArtistLink'+str(sotdUser):artistLinks[-1],
                'sotdExplicit'+str(sotdUser):explicitList[-1],
            }
            
            sotdDict.update(userDict)
            
            sotdUser = sotdUser + 1            
                
        # print(trackNames)
        # print(trackLinks)
        # print(albumList)
        # print(albumLinks)
        # print(albumArts)
        # print(artistList)
        # print(artistLinks)
        # print(explicitList)
        # print('----------------------------------------------------------------')
        
        # print(sotdDict)
        return sotdDict
        #----------------------------------------------------------------------------------------------------------
    else:
        print("Can't get token for", username)
        
def mornBrew(): # Pull info from the daily morning brew
    
    src = 'https://www.morningbrew.com/latest/'
    soup = webReq(src)
   
    #mornBrewLogoSrc = 'https://www.morningbrew.com/latest/wp-content/uploads/2018/02/morning-brew-2018.png'
    
    tickerTableHeaders = soup.find_all(attrs={"class":'ticker'}) # find <th> tags with class "ticker"
    tickerTableList = [] 
    
    tickerTableList.append(tickerTableHeaders[0].find_parents('table')[0]) # pull first parent 'table' and add to list for each <th> class 'ticker'
    
    tickerTablePs = tickerTableList[0].find_all('p') #find all p tags which have the data
    tickerTableImg = tickerTableList[0].find_all('img') #find all image tags which have the green or red arrows
    tickImgSrc = []
    tickTxt = []
    tickClr = []    
    
    for tickSrc in tickerTableImg:
        tickImgSrc.append(tickSrc['src'])#create the img src list
        if 'green' in tickSrc['src']: #use mornBrew img source to determine the class...
            tickClr.append('green')
        elif 'red' in tickSrc['src']:
            tickClr.append('red') 
    
    for tick in tickerTablePs:
        tickTxt.append(tick.text)#create the data list

    # print(tickTxt)
    # print(tickClr)
    mornBrewDict = {'mBrewTickImg':tickImgSrc, 'mBrewTickTxt': tickTxt, 'mBrewTickClr': tickClr}
    #print(mornBrewDict)
    #print(tickerTablePs)
 
    
    return mornBrewDict  

def btcPrc():
    from coinmarketcap import Market

    cmc = Market()
    btc = cmc.ticker('bitcoin')
    btcUSD = btc[0]['price_usd']#this is silly...
    btc24Delta = btc[0]['percent_change_24h']

    if '-' in btc24Delta:
        btc24Delta = str(btc24Delta) + '%'
        btcColor = 'red'
        btcArrow = 'https://img.createsend1.com/ei/j/22/063/D9D/csimport/red_arrow.png'
    else:
        btc24Delta = '+' + str(btc24Delta)+ '%'
        btcColor = 'green'
        btcArrow = 'https://img.createsend1.com/ei/j/22/063/D9D/csimport/green_arrow.png'

    btcTick = {'btcUSD':str(btcUSD),'btc24Delta':btc24Delta,'btcArrow':btcArrow,'btcColor':btcColor}
    return btcTick 

def manhPrc():

    import re

    src = 'https://www.google.com/search?q=manh+ticker'
    manhSoup = webReq(src)
    manhSpan = manhSoup.find_all('span')

    badCoding = 0 #Im sorry to anyone that sees this...
    for span in manhSpan:
        if 'USD' in span.text:
            if badCoding == 0:
                usdSpan = span
                badCoding = 1
        elif badCoding > 0:
            if badCoding == 4:
                delta24 = span
                break

            badCoding += 1

    manhUSD = re.sub('[^0-9.]','',usdSpan.text)
    manh24Delta = re.sub('[^0-9.-]','',delta24.text)
    #print(manhUSD)

    if '-' in manh24Delta:
        manhColor = 'red'
        manhArrow = 'https://img.createsend1.com/ei/j/22/063/D9D/csimport/red_arrow.png'
    else:
        manh24Delta = '+' + manh24Delta + '%'
        manhColor = 'green'
        manhArrow = 'https://img.createsend1.com/ei/j/22/063/D9D/csimport/green_arrow.png'

    manhTick = {'manhUSD':manhUSD,'manh24Delta':manh24Delta,'manhColor':manhColor,'manhArrow':manhArrow}

    return manhTick

    
def render_template(template_filename, context):
    return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)
 
 
def create_index_html(otdDict):
    html = render_template('otdTemplateWIP.html', otdDict)
    #print(html)
    #save the results
    c = 0
    while True:
        try:
            cstr = str(c)
            with open(PATH+"/otdHTML/otd"+now.strftime("%Y_%m_%d")+cstr+".html", "x",encoding="utf-8") as fh:
                fh.write(html)
                fh.close()
            webb.open("file://"+PATH+"/otdHTML/otd"+now.strftime("%Y_%m_%d")+cstr+".html",new=2) #open html document
                           
            break
        except FileExistsError:
            c += 1
            continue
    return html 
    
def sendNewsletter(html):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    import configparser

    config = configparser.ConfigParser()
    config.read(PATH+'/config/config.ini')


    emailConfig = config['email']

    user = emailConfig['user']
    password = emailConfig['pass']
    
    #move to a txt file
    FROM = emailConfig['from']#from Email
    TO = emailConfig['to'] #list of recipients
    
    try:  
        
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(user, password)

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'of the day Newsletter' + now.strftime("%Y_%m_%d")+ ' TRIAL RUN'
        msg['From'] = FROM
        msg['To'] = ', '.join(TO)

        # Create the body of the message (a plain-text and an HTML version).
        text = "Looks like your Email Client doesn't allow HTML emails :("

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg.attach(part1)   
        msg.attach(part2)

        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        server.sendmail(FROM, TO, msg.as_string())
        server.quit()    
        
    except:  
        print('Something went wrong...')
    


wotd = wotd()
# print('wotd')
apod = apod()
# print('aotd')
sotd = sotd()
# print('sotd')
mornBrew = mornBrew()
#print('mornBrew')
btcPrc = btcPrc()
#print('btcPrc')
manhPrc = manhPrc()
#print('manhPrc')

otdDict = {'wotdWord': 'feint', 'wotdDefines': ['a movement made in order to deceive an adversary; an attack aimed at one place or point merely as a distraction from the real place or point of attack: <em>military feints; the feints of a skilled fencer</em>.', 'a feigned or assumed appearance: <em>His air of approval was a feint to conceal his real motives</em>.', 'to make a feint.'], 'wotdQuote': 'Antagonism in my family comes wrapped in layers of code, sideways <strong>feint</strong>s, full deniability.', 'wotdCite': '-- Karen Joy Fowler, We Are All Completely Besides Ourselves, 2013', 'wotdPos': 'noun', 'wotdPronounce': '/feɪnt/ ', 'apodSrc': 'https://apod.nasa.gov/apod/image/1804/FairbairnMagellanicCloudsAtacamaDesert1024.jpg', 'apodLink': 'https://apod.nasa.gov/apod/image/1804/FairbairnMagellanicCloudsAtacamaDesert1024.jpg', 'apodTitle': ' Magellanic Mountain ', 'apodCite': ' Image Credit &<a href="lib/about_apod.html#srapply">Copyright</a>: CarlosFairbairn', 'apodType': 'Photo', 'sotdTrack0': 'Hold On (I Was Wrong)', 'sotdTrackLink0': 'https://open.spotify.com/track/1bTzErckylA7bBIrBfOgRI', 'sotdAlbum0': 'Hold On (I Was Wrong)', 'sotdAlbumArt0': 'https://i.scdn.co/image/f88a229c73a9fdbf582d10a922221f4f0ead3d78', 'sotdAlbumLink0': 'https://open.spotify.com/album/1sGQGH1CSRn0888zYxz8EB', 'sotdArtist0': 'Video Age', 'sotdArtistLink0': 'https://open.spotify.com/artist/4aTQ05Ddh21E2CJFSZy7ZW', 'sotdExplicit0': '', 'sotdTrack1': 'Journal of Ardency', 'sotdTrackLink1': 'https://open.spotify.com/track/6sbOGldEofWsQlq1GjdHJK', 'sotdAlbum1': 'Journal of Ardency', 'sotdAlbumArt1': 'https://i.scdn.co/image/371f6ac07bf1f8d6b0df2560fe92c06a8e655751', 'sotdAlbumLink1': 'https://open.spotify.com/album/5zJe6jrZxxyz19NgnKXIom', 'sotdArtist1': 'Class Actress', 'sotdArtistLink1': 'https://open.spotify.com/artist/4nZbOHYEypqHtWwTPQu8Fl', 'sotdExplicit1': '', 'mBrewTickImg': ['https://img.createsend1.com/ei/j/22/063/D9D/csimport/green_arrow.png', 'https://img.createsend1.com/ei/j/22/063/D9D/csimport/green_arrow.png', 'https://img.createsend1.com/ei/j/22/063/D9D/csimport/green_arrow.png', 'https://img.createsend1.com/ei/j/22/063/D9D/csimport/red_arrow.png', 'https://img.createsend1.com/ei/j/22/063/D9D/csimport/red_arrow.png', 'https://img.createsend1.com/ei/j/22/063/D9D/csimport/green_arrow.png'], 'mBrewTickTxt': ['S&P;', '2,666.94', '+1.04%', 'NASDAQ', '7,118.68', '+1.64%', 'DJIA', '24,322.27', '+0.99%', '10-YR', '2.987%', '-1.29%', 'GOLD', '1,318.90', '-0.38%', 'OIL', '68.19', '+0.21%'], 'mBrewTickClr': ['green', 'green', 'green', 'red', 'red', 'green']}
otdDict = {}
otdDict.update(wotd)
otdDict.update(apod)
otdDict.update(sotd)
otdDict.update(mornBrew)
otdDict.update(btcPrc)
otdDict.update(manhPrc)
print('otd Run Complete')
#print(otdDict)

html = create_index_html(otdDict)

# sendNewsletter(html)









