#!/bin/python3

import json
import os
import sys

import cfscrape

email = 'mail'
password = 'password'
downloadDir = '/home/rondie/patreon'
cookieFile = '/home/rondie/.scripts/patreon_cookies.json'
baseUrl = 'https://www.patreon.com'

# test if download directory exists
if not os.path.isdir(downloadDir):
    sys.exit('Path', downloadDir, 'does not exist')

# make sure we have a trailing slash for the domain
if not baseUrl.endswith('/'):
    baseUrl += '/'

s = cfscrape.CloudflareScraper()

# see if we already have a cookie file...
if os.path.isfile(cookieFile):
    cookieFileContents = open(cookieFile, 'r')
    cookies = json.load(cookieFileContents)
else:
    cookies = {}

# and if not, fill it
if 'session_id' not in cookies:
    logindata = \
        {"data": {"type": "user", "attributes": {"email": email, "password": password}}}
    loginpage = \
        s.post(baseUrl + 'api/login', json=logindata, cookies=dict(cookies))
    if loginpage.status_code == 401:
        cookieFileContents = open(cookieFile, 'w')
        cookie_dict = loginpage.cookies.get_dict()
        json.dump(cookie_dict, cookieFileContents, indent=6)
        print('you should have received a mail from patreon with a link')
        print('click the link there before running script again')
        sys.exit()
    elif loginpage.status_code == 200:
        cookieFileContents = open(cookieFile, 'w')
        cookie_dict = loginpage.cookies.get_dict()
        json.dump(cookie_dict, cookieFileContents, indent=6)
    else:
        sys.exit('could not get cookie...')

# get campaigns...
listpatreonpage = \
    s.get(baseUrl + 'api/current_user?include=pledges.creator.campaign.null,pledges.campaign.null,follows.followed.campaign.null&type=campaign&fields%5Bcampaign%5D=url', cookies=dict(cookies))
listpatreonpageJson = json.loads(listpatreonpage.text)

# and per campaign, get creator data
for creator in listpatreonpageJson['included']:
    if creator['type'] == 'campaign':
        creatorUrl = creator['attributes']['url']
        creatorId = creator['id']
        creatorName = creatorUrl.replace(baseUrl, '')
        # per creator, list if attachments present
        creatorIdUrl = \
            baseUrl + 'api/posts?include=campaign%2Caccess_rules%2Cattachments%2Cname%2Curl&fields[post]=post_file%2Cdownload_url%2Cmetadata%2Cfile_name&filter[campaign_id]=' + creatorId + '&filter[contains_exclusive_posts]=true&filter[is_draft]=false&sort=-published_at&json-api-version=1.0'
        creatorPostsContent = json.loads(s.get(creatorIdUrl, cookies=dict(cookies)).text)
        for post in creatorPostsContent['included']:
            if 'attachment' in str(post['type']):
                downloadFile = (downloadDir + "/" + creatorName + "/" + str(post['attributes']['name']))
                if not os.path.isfile(downloadFile):
                    print(" ", downloadFile, " not present, downloading...")
                    # test if download directory exists
                    if not os.path.isdir(downloadDir + "/" + creatorName):
                        os.makedirs(downloadDir + "/" + creatorName)
                    creatorUrlContent = s.get(creatorUrl, cookies=dict(cookies))
                    # and download file(s)
                    with open(downloadFile, 'wb') as File:
                        File.write(creatorUrlContent.content)
                        File.close()
