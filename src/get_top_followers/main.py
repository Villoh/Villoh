import requests
import sys
import re


def get_followers(handle: str, token: str, max_following: int = 10000, max_pages: int = 1000):
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }
    followers = []

    for page_num in range(1, max_pages + 1):
        url = f"https://api.github.com/users/{handle}/followers?page={page_num}&per_page=100"
        page = requests.get(url, headers=headers).json()
        if not page:
            break

        for follower in page:
            info = requests.get(follower["url"], headers=headers).json()
            if info.get("following", 0) > max_following:
                continue

            followers.append((
                info.get("followers", 0),
                info["login"],
                info["id"],
                info.get("name") or info["login"]
            ))
            print(followers[-1])

    return sorted(followers, reverse=True)


def build_html_table(followers, max_items=14, row_size=7):
    html = "<table>\n"
    for i, (follower_count, login, user_id, name) in enumerate(followers[:max_items]):
        if i % row_size == 0:
            if i != 0:
                html += "  </tr>\n"
            html += "  <tr>\n"
        html += f'''    <td align="center">
      <a href="https://github.com/{login}">
        <img src="https://avatars2.githubusercontent.com/u/{user_id}" width="100px;" alt="{login}"/>
      </a>
      <br />
      <a href="https://github.com/{login}">{name}</a>
    </td>
'''
    html += "  </tr>\n</table>"
    return html


def update_readme_section(readme_path, new_html, start_marker, end_marker):
    with open(readme_path, "r", encoding="utf-8") as readme_file:
        content = readme_file.read()

    new_content = re.sub(
        fr"(?<={start_marker})[\s\S]*(?={end_marker})",
        f"\n{new_html}\n",
        content
    )

    with open(readme_path, "w", encoding="utf-8") as readme_file:
        readme_file.write(new_content)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python script.py <github_handle> <github_token> <readme_path>")
        sys.exit(1)

    github_handle = sys.argv[1]
    github_token = sys.argv[2]
    readme_path = sys.argv[3]

    top_followers = get_followers(github_handle, github_token)
    followers_html = build_html_table(top_followers)
    update_readme_section(
        readme_path,
        followers_html,
        "<!--START_SECTION:top-followers-->",
        "<!--END_SECTION:top-followers-->"
    )
