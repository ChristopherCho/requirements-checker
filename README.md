# requirements-checker
Integrated requirements management for multi-repository environment 

## Usage
### Data preparation
1. For each requirements file for each repository, list them in `./data/requirements.json` in following format:
```
{
    "repository1": {
        "git": "{OWNER}/{REPOSITORY}",
        "branch": "main",
        "requirements": [
            "requirements/all.txt",
            "requirements/core.txt",
            "requirements/extra.txt"
        ]
    },
    "repository2": {
        "git": "{OWNER}/{REPOSITORY}",
        "branch": "main",
        "requirements": [
            "requirements.txt"
        ]
    }
}
```

2. (Optional) To update github issue comments with generated report, write comment information in `./data/github_comment_info.json` in following format:
```
{
    "repo_path": "{OWNER}/{REPOSITORY}",
    "comment_id": {INTEGER_COMMENT_ID}
}
```
You can get comment id from github issue comment url. For example, if the comment url is `https://github.com/{OWNER}/{REPOSITORY}/issues/1#issuecomment-1234567890` then the comment id is `1234567890`.

3. Acquire Github token from `https://github.com/settings/tokens`. You need to grant `repo` scope to the token.

4. Run `python3 main.py` to generate report.
```
usage: main.py [-h] --token TOKEN [--output OUTPUT] [--write_github_comment]

optional arguments:
  -h, --help            show this help message and exit
  --token TOKEN, -t TOKEN
                        GitHub token
  --output OUTPUT, -o OUTPUT
                        Output file path
  --write_github_comment
                        Write the output to a GitHub comment
```