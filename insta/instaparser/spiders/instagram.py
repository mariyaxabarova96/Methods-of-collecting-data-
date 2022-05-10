import scrapy
from scrapy.http import HtmlResponse
import json
import re
from instaparser.items import InstaparserItem
from urllib.parse import urlencode
from copy import deepcopy


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instgram.com']
    start_urls = ['https://instgram.com/']
    inst_login_link = 'https://instgram.com/accounts/login/ajax/'
    inst_login = 'Onliskill_udm'
    inst_pwd = '#PWD_INSTAGRAM_BROWSER:10:1650388687:AUVQAPLsNiCtdG0b660bL/la/fAfzNJ0AaVNGPhAI7fwS9ANR85sT7Kjag60UVTeviSs34AXFch4cAYMc8Pq56W6i7ntwpu2ucSOa3aIY3LRVrPRqB2XvkxeB+KW6C2TQEPNVbnxpAqk8m4yOJg='
    user_agent = 'Instagram 155.0.0.37.107'
    inst_graphql_link = 'https://www.instagram.com/graphql/query/?'
    posts_hash = '396983faee97f4b49ccbe105b4daf7a0'
    fol_link = 'https://i.instagram.com/api/v1/friendships/'
    fol_hash = '396983faee97f4b49ccbe105b4daf7a0'

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        self.parse_users = kwargs.get('query')

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={'username':self.inst_login, 'enc_password': self.inst_pwd},
            headers={'X-CSRFToken': csrf})

    def login(self, response: HtmlResponse):
        j_body = response.json()
        if j_body.get('authenticated'):
            for parse_user in self.parse_users:
                yield response.follow(
                    f'/{parse_user}',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': parse_user}
                )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'id': user_id,
                     'first': 12}
        url_posts = f'{self.inst_graphql_link}query_hash={self.posts_hash}&{urlencode(variables)}'
        yield response.follow(url_posts,
                              callback=self.user_posts_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': deepcopy(variables)})

        fol_variables = {'count': 12,
                               'search_surface': 'follow_list_page'}
        url_fol = f'{self.fol_link}{user_id}/followers/?{urlencode(fol_variables)}'
        yield response.follow(url_fol,
                              callback=self.user_follow_parser,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'followers_variables': deepcopy(fol_variables),
                                         'following_variables': False},
                              headers={'User-Agent': self.user_agent})

        follow_variables = {'count': 12}
        url_following = f'{self.fol_link}{user_id}/following/?{urlencode(follow_variables)}'
        yield response.follow(url_following,
                              callback=self.user_follow_parser,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'followers_variables': False,
                                         'following_variables': deepcopy(follow_variables)},
                              headers={'User-Agent': self.user_agent})

    def user_posts_parse(self, response: HtmlResponse, username, user_id, variables):
        j_data = response.json()
        page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
        if page_info.get('has_next_page'):
            variables['after'] = page_info.get('end_cursor')
            url_posts = f'{self.inst_graphql_link}query_hash={self.posts_hash}&{urlencode(variables)}'
            yield response.follow(url_posts,
                                  callback=self.user_posts_parse,
                                  cb_kwargs={'username': username,
                                             'user_id': user_id,
                                             'variables': deepcopy(variables)},
                                  headers={'User-Agent': 'Instagram 155.0.0.37.107'})
        posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')
        for post in posts:
            item = InstaparserItem(
                user_id=user_id,
                username=username,
                photo=post.get('node').get('display_url'),
                likes=post.get('node').get('edge_media_preview_like').get('count'),
                post_data=post.get('node'),
                type_info='post'
            )
            yield item

    def user_follow_parser(self, response: HtmlResponse, username, user_id, fol_variables, follow_variables):
        j_data = response.json()
        next_page = j_data.get('next_max_id')
        if fol_variables:
            type_info = 'followers'
        elif follow_variables:
            type_info = 'following'

        if next_page:
            if follow_variables:
                follow_variables['max_id'] = int(next_page)
                url_following = f'{self.fol_link}{user_id}/{type_info}/?{urlencode(follow_variables)}'
                yield response.follow(url_following,
                                      callback=self.user_follow_parser,
                                      cb_kwargs={'username': username,
                                                 'user_id': user_id,
                                                 'followers_variables': False,
                                                 'following_variables': deepcopy(follow_variables)},
                                      headers={'User-Agent': self.user_agent})
            elif fol_variables:
                fol_variables['max_id'] = next_page
                url_followers = f'{self.fol_link}{user_id}/followers/?{urlencode(fol_variables)}'
                yield response.follow(url_followers,
                                      callback=self.user_follow_parser,
                                      cb_kwargs={'username': username,
                                                 'user_id': user_id,
                                                 'followers_variables': deepcopy(fol_variables),
                                                 'following_variables': False},
                                      headers={'User-Agent': self.user_agent})

        users = j_data.get('users')
        for user in users:
            item = InstaparserItem(
                user_id=user_id,
                username=username,
                type_info=type_info,
                fol_u_id=user.get('pk'),
                fol_u_name=user.get('username'),
                profile_photo=user.get('profile_pic_url'),
            )
            yield item

    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        try:
            matched = re.search(
                '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
            ).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('\"id\":\"\\d+\"', text)[-1].split('"')[-2]
