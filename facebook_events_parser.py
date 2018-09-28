import requests
from bs4 import BeautifulSoup
import re
import urllib

events_url = 'https://www.facebook.com/events/'
example = 'id'

ans_dict = {'id': int(), 'tags': list(),
                'organizators': {'id': 0, 'alias': '', 'name': '', 'url': ''},
                'title': '',
                'date': '',
                'description': '',
                'going_count': 0, 'interested_count': 0,
                'location': '', 'tickets_url': '', 'image': '', 'is_public': True}


def uncomment(c):
    h = '<div>'
    for m in re.finditer('<div\\sclass="hidden_elem"><code\\sid="[^"]+"><\\!--(.*?)--></code>', c):
        h += m.group(1)
    h += '</div>'
    return h


def get_title(soup):
    if soup.title.string is not None:
        return soup.title.string
    else:
        return ''


def get_date(soup_comments):
    div = soup_comments.select('#event_time_info ._2ycp')
    if len(div) > 0:
        try:
            if div[0].text:
                return div[0].text
        except:
            return ''


def get_location(soup_comments):
    location = soup_comments.select('._3xd0 ._5xhk')
    if len(location) > 0 and location[0].text is not None:
        return location[0].text
    return ''


def get_going_and_interested_count(soup_comments):
    ans = {'going_count': '', 'interested_count': ''}
    span = soup_comments.select('span._5z74')
    if len(span) > 0 and span[0].text is not None:
        going_and_interested_count = span[0].text
        l = re.findall('([0-9\\.]+)(K|M)?', going_and_interested_count)
        if len(l) == 2:
            if l[0][1] == '':
                ans['going_count'] = int(l[0][0])
            if l[0][1] == 'K':
                ans['going_count'] = int(float(l[0][0]) * 1000)
            if l[0][1] == 'M':
                ans['going_count'] = int(float(l[0][0]) * 1000000)
            if l[1][1] == '':
                ans['interested_count'] = int(l[1][0])
            if l[1][1] == 'K':
                ans['interested_count'] = int(float(l[1][0]) * 1000)
            if l[1][1] == 'M':
                ans['interested_count'] = int(float(l[1][0]) * 1000000)
        if len(l) == 1:
            if 'nterested' in going_and_interested_count:
                if l[0][1] == '':
                    ans['interested_count'] = int(l[0][0])
                if l[0][1] == 'K':
                    ans['interested_count'] = int(float(l[0][0]) * 1000)
                if l[0][1] == 'M':
                    ans['interested_count'] = int(float(l[0][0]) * 1000000)
            if 'oing' in going_and_interested_count:
                if l[0][1] == '':
                    ans['going_count'] = int(l[0][0])
                if l[0][1] == 'K':
                    ans['going_count'] = int(float(l[0][0]) * 1000)
                if l[0][1] == 'M':
                    ans['going_count'] = int(float(l[0][0]) * 1000000)
    return ans['going_count'], ans['interested_count']


def get_tickets_url(soup_comments):
    a = soup_comments.select('li._3xd0')
    tickets_url = ''
    for i in a:
        if i.has_attr('data-testid'):
            if i.get('data-testid') == 'event_ticket_link':
                m = re.findall('/l\\.php\\?u=(.+?)&', str(i))
                if m is not None:
                    for j in m:
                        tickets_url = urllib.parse.unquote(j)
    return tickets_url


def get_organizators(soup):
    selector_ = soup.select('._b9- a')
    list_organizators = []
    if len(selector_) > 0:
        for s in selector_:
            organizator = dict()
            if s.has_attr('data-tooltip-content'):
                nams = s.get('data-tooltip-content').split('\n')
                for n in nams:
                    list_organizators.append({'name': n})
            if s.has_attr('href') and s.has_attr('data-tooltip-content') is not True:
                url = s.get('href')
                organizator['url'] = url
                splited_url = url.split('/')
                organizator['alias'] = splited_url[len(splited_url) - 2]
                if s.text is not None:
                    organizator['name'] = s.text
                list_organizators.append(organizator)
    return list_organizators


def get_image_url(soup):
    im = ''
    img_selector = soup.select('img.scaledImageFitWidth')
    if len(img_selector) == 0:
        img_selector = soup.select('img.scaledImageFitHeight')
    if len(img_selector) > 0:
        if img_selector[0].has_attr('src'):
            im = img_selector[0].get('src')
    return im


def get_tags(soup):
    keywords = ''
    if soup.text is not None:
        keywords = re.findall('\\{name:"([^"]+)",token:"\\{', soup.text)
    return keywords


def is_public(soup):
    span_ = soup.find_all('span')
    is_p = True
    if len(span_) > 0:
        for item in span_:
            if item.has_attr('data-testid'):
                if item.text == 'Public':
                    is_p = True
                else:
                    is_p = False
    return is_p


def get_description(html, id_):
    headers = {
        'accept': '*/*',
        'accept-encoding': 'identity',
        'accept-language': 'en-US',
        'origin': 'https://www.facebook.com',
        'referer': 'https://www.facebook.com/events/' + str(id_),
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/' + \
                      '69.0.3497.92 Safari/537.36'
    }
    cc = html.content.decode('utf-8')
    rev = ''
    m = re.search('"client_revision":([0-9]+),', cc, re.S | re.I)
    if m is not None:
        rev = m.group(1)
    lsd = ''
    m = re.search('\\{"token":"([^"]+)"\\}', cc, re.S | re.I)
    if m is not None:
        lsd = m.group(1)
    form_data = {
        'av': 0,
        '__user': 0,
        '__a': 1,
        '__req': 1,
        '__be': -1,
        '__pc': 'PHASED:DEFAULT',
        '__rev': rev,
        'lsd': lsd,
        'fb_api_caller_class': 'RelayModern',
        'variables': '{"eventID":"' + str(id_) + '"}',
        'doc_id': '1640160956043533'
    }
    qraphql_url = 'https://www.facebook.com/api/graphql/'
    proxies = None
    try:
        response = requests.post(qraphql_url, headers=headers, data=form_data, proxies=proxies)
        return response.json()['data']['event']['details']['text']
    except:
        return ''


def facebook_event_details(id):
    try:
        html = requests.get(events_url + id, headers={"Accept-Language": "en-US"}, timeout=(3, 10))
    except:
        print("Error")

    content = html.content.decode('utf-8')
    content = uncomment(content)

    soup_comments = BeautifulSoup(content, 'html.parser')
    soup = BeautifulSoup(html.content, 'html.parser')

    ans_dict['id'] = id
    ans_dict['title'] = get_title(soup)
    ans_dict['date'] = get_date(soup_comments)
    ans_dict['location'] = get_location(soup_comments)
    ans_dict['going_count'], ans_dict['interested_count'] = get_going_and_interested_count(soup_comments)
    ans_dict['tickets_url'] = get_tickets_url(soup_comments)
    ans_dict['image'] = get_image_url(soup)
    ans_dict['organizators'] = get_organizators(soup)
    ans_dict['tags'] = get_tags(soup)
    ans_dict['is_public'] = is_public(soup)
    ans_dict['description'] = get_description(html, id)

    return ans_dict


ans = facebook_event_details(example)
for k, v in ans.items():
    print('\n' + str(k) + '  ' + str(v))
