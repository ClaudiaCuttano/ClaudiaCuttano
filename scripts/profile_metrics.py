import html
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path

USERNAME = "ClaudiaCuttano"

ADDITIONAL_REPOSITORIES = [
    ("visinf", "INSID3"),
    ("visinf", "MARCO"),
]

TOKEN = os.environ["GITHUB_TOKEN"]


def github_request(url: str):
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {TOKEN}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ClaudiaCuttano-profile",
        },
    )

    with urllib.request.urlopen(request) as response:
        return json.load(response)


def get_owned_repositories(username: str):
    repositories = []
    page = 1

    while True:
        batch = github_request(
            f"https://api.github.com/users/{username}/repos"
            f"?type=owner&per_page=100&page={page}"
        )

        if not batch:
            break

        repositories.extend(batch)

        if len(batch) < 100:
            break

        page += 1

    return repositories


def get_search_count(endpoint: str, query: str):
    encoded_query = urllib.parse.quote(query)

    result = github_request(
        f"https://api.github.com/search/{endpoint}"
        f"?q={encoded_query}&per_page=1"
    )

    return result["total_count"]


repositories = get_owned_repositories(USERNAME)

counted_repositories = set()
total_stars = 0
total_forks = 0

for repository in repositories:
    full_name = repository["full_name"].lower()

    if full_name in counted_repositories:
        continue

    counted_repositories.add(full_name)
    total_stars += repository["stargazers_count"]
    total_forks += repository["forks_count"]

for owner, repository_name in ADDITIONAL_REPOSITORIES:
    repository = github_request(
        f"https://api.github.com/repos/{owner}/{repository_name}"
    )

    full_name = repository["full_name"].lower()

    if full_name in counted_repositories:
        continue

    counted_repositories.add(full_name)
    total_stars += repository["stargazers_count"]
    total_forks += repository["forks_count"]

total_commits = get_search_count(
    "commits",
    f"author:{USERNAME}",
)

profile = github_request(
    f"https://api.github.com/users/{USERNAME}"
)

followers = profile["followers"]

metrics = {
    "stars": total_stars,
    "commits": total_commits,
    "forks": total_forks,
    "followers": followers,
}

output_directory = Path("profile")
output_directory.mkdir(exist_ok=True)

(output_directory / "stats.json").write_text(
    json.dumps(metrics, indent=2) + "\n",
    encoding="utf-8",
)


def star_icon(x: int, y: int):
    return f"""
    <polygon
      points="{x + 8},{y}
              {x + 10.5},{y + 5.2}
              {x + 16},{y + 6}
              {x + 12},{y + 10}
              {x + 13},{y + 16}
              {x + 8},{y + 13}
              {x + 3},{y + 16}
              {x + 4},{y + 10}
              {x},{y + 6}
              {x + 5.5},{y + 5.2}"
      class="icon"
    />
    """


def commit_icon(x: int, y: int):
    return f"""
    <g class="icon-stroke">
      <line
        x1="{x}"
        y1="{y + 8}"
        x2="{x + 5}"
        y2="{y + 8}"
      />
      <circle
        cx="{x + 8}"
        cy="{y + 8}"
        r="3"
      />
      <line
        x1="{x + 11}"
        y1="{y + 8}"
        x2="{x + 16}"
        y2="{y + 8}"
      />
    </g>
    """


def fork_icon(x: int, y: int):
    return f"""
    <g class="icon-stroke">
      <circle
        cx="{x + 3}"
        cy="{y + 3}"
        r="2"
      />
      <circle
        cx="{x + 13}"
        cy="{y + 3}"
        r="2"
      />
      <circle
        cx="{x + 8}"
        cy="{y + 14}"
        r="2"
      />

      <path
        d="M {x + 3} {y + 5}
           V {y + 7}
           C {x + 3} {y + 10},
             {x + 8} {y + 9},
             {x + 8} {y + 12}"
      />

      <path
        d="M {x + 13} {y + 5}
           V {y + 7}
           C {x + 13} {y + 10},
             {x + 8} {y + 9},
             {x + 8} {y + 12}"
      />
    </g>
    """


def followers_icon(x: int, y: int):
    return f"""
    <g class="icon-stroke">
      <circle
        cx="{x + 6}"
        cy="{y + 5}"
        r="3"
      />

      <path
        d="M {x + 1} {y + 16}
           C {x + 1} {y + 11},
             {x + 11} {y + 11},
             {x + 11} {y + 16}"
      />

      <circle
        cx="{x + 13}"
        cy="{y + 6}"
        r="2"
      />

      <path
        d="M {x + 12} {y + 11}
           C {x + 16} {y + 11},
             {x + 17} {y + 13},
             {x + 17} {y + 16}"
      />
    </g>
    """


def statistic(icon, x, y, label, value):
    return f"""
    <g>
      {icon(x, y - 13)}

      <text
        x="{x + 27}"
        y="{y}"
        class="label"
      >
        {html.escape(label)}
      </text>

      <text
        x="{x + 165}"
        y="{y}"
        class="value"
      >
        {html.escape(str(value))}
      </text>
    </g>
    """


card_width = 520
card_height = 150

svg = f"""<svg
  xmlns="http://www.w3.org/2000/svg"
  width="{card_width}"
  height="{card_height}"
  viewBox="0 0 {card_width} {card_height}"
  role="img"
  aria-label="Claudia's GitHub statistics"
>
  <style>
    .title {{
      font: 600 18px -apple-system, BlinkMacSystemFont,
            "Segoe UI", Helvetica, Arial, sans-serif;
      fill: #8250df;
    }}

    .label {{
      font: 400 14px -apple-system, BlinkMacSystemFont,
            "Segoe UI", Helvetica, Arial, sans-serif;
      fill: #57606a;
    }}

    .value {{
      font: 600 14px -apple-system, BlinkMacSystemFont,
            "Segoe UI", Helvetica, Arial, sans-serif;
      fill: #24292f;
    }}

    .icon {{
      fill: #8250df;
    }}

    .icon-stroke {{
      fill: none;
      stroke: #8250df;
      stroke-width: 1.7;
      stroke-linecap: round;
      stroke-linejoin: round;
    }}
  </style>

  <rect
    x="0.5"
    y="0.5"
    width="{card_width - 1}"
    height="{card_height - 1}"
    rx="7"
    fill="#ffffff"
    stroke="#d0d7de"
  />

  <text
    x="25"
    y="38"
    class="title"
  >
    Claudia's GitHub Stats
  </text>

  {statistic(
      star_icon,
      25,
      78,
      "Total Stars",
      total_stars,
  )}

  {statistic(
      commit_icon,
      280,
      78,
      "Total Commits",
      total_commits,
  )}

  {statistic(
      fork_icon,
      25,
      118,
      "Total Forks",
      total_forks,
  )}

  {statistic(
      followers_icon,
      280,
      118,
      "Followers",
      followers,
  )}
</svg>
"""

(output_directory / "stats.svg").write_text(
    svg,
    encoding="utf-8",
)

print("Created profile/stats.svg")
print(json.dumps(metrics, indent=2))
