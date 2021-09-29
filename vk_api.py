from urllib.request import Request, urlopen
import json
import webbrowser
import os


def get_friends(user_id, token, version):
    if not user_id.isdigit():
        try:
            user_id = get_right_id(user_id, token, version)
        except KeyError:
            raise ValueError("user does not exist")

    friends = f"https://api.vk.com/method/friends.get?user_id={user_id}" \
              + f"&order=name&fields=nickname,domain&access_token={token}&v={version}"
    try:
         return request(friends)['response']
    except KeyError:
        raise KeyError(f"{request(friends)['error']['error_msg']}")


def request(req_message):
    req_obj = Request(req_message,
                      headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req_obj)
    return json.loads(page.read())


def get_right_id(screen_name, token, version):
    id = f"https://api.vk.com/method/utils.resolveScreenName?screen_name={screen_name}" \
         + f"&access_token={token}&v={version}"
    response = request(id)
    return response["response"]["object_id"]


def build_page(st, name):
    html = """<!DOCTYPE html>
                        <html lang="ru">
                        <head>
                        <title>Друзья ВКонтакте</title>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1">
                        <style>
                        body {
                          font-family: Times New Roman;
                          margin: 0;
                        }
                        .header {
                          padding: 30px;
                          text-align: center;
                          background: #0066CC;
                          color: white;
                          font-size: 20px;
                        }
                        .content {
                          padding:20px;
                          text-align: center;
                          background: #EEEEEE;
                        }
                        </style>
                        </head>
                        <body>
                        <div class="header">
                          <h2>Друзья ВКонтакте пользователя с id: """ + name + """</h2>
                        </div>
                        <div class="content">
                          %s
                        </div>
                        </body>
                        </html>
                        """ % st
    with open("friends.html", 'w', encoding="utf-8") as f:
        f.write(html)


if __name__ == '__main__':
    version = "5.131"
    tkn = input("Enter the token of the app: ")
    user_id = input("Enter user id: ")
    rep = get_friends(user_id, tkn, version)['items']
    res = "\n".join(["<p>" + f'<a href="https://vk.com/id{r["id"]}">'
                     + r['first_name'] + " " + r['last_name']
                     + "</a>" + "</p>" for r in rep])
    build_page(res, user_id)
    url = os.getcwd() + "\\friends.html"
    webbrowser.open_new(url)

