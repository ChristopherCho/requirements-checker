import json
import requests
import re
import pprint
from pathlib import Path

REQ_DATA_PATH = Path(__file__).parent / "data" / "requirements.json"
COMMNET_INFO_PATH = Path(__file__).parent / "data" / "github_comment_info.json"


def prettify_table(dict_data):
    table_str = "Repository|Requirements File|Library|Version|Source\n" \
                "-|-|-|-|-\n"
                
    prev_repo = ""
    for repo, req_per_file in dict_data.items():
        prev_file = ""
        for req_file, libs in req_per_file.items():
            for lib, version, source in libs:
                if source.startswith("https://") or source.startswith("http://"):
                    source = f"[Link]({source})"
                elif source.startswith("git+ssh://"):
                    link = source.replace('git+ssh://git@', 'https://').replace('.git', '')
                    link_with_hash_or_version = link.rsplit('@', 1)
                    if len(link_with_hash_or_version) == 2:
                        link, hash_or_version = link_with_hash_or_version
                        link = link + '/tree/' + hash_or_version
                    else:
                        link = link_with_hash_or_version[0]
                    source = f"[Link]({link})"
                table_str += f"{repo if prev_repo != repo else '&nbsp;'}|{req_file if prev_file != req_file else '&nbsp;'}|{lib}|{version}|{source}\n"
                prev_repo = repo
                prev_file = req_file
                
    inverted_dict = {k: [] for k in dict_data.keys()}
    for repo, req_per_file in dict_data.items():
        for req_file, libs in req_per_file.items():
            for lib, version, source in libs:
                if lib in inverted_dict:
                    inverted_dict[lib].append((repo, req_file))
                    
    inverted_table_str = "Library|Repositories|Requirements Files\n" \
                            "-|-|-\n"
    prev_lib = ""
    for lib, repo_and_files in inverted_dict.items():
        for repo, req_file in repo_and_files:
            inverted_table_str += f"{lib if prev_lib != lib else '&nbsp;'}|{repo}|{req_file}\n"
            prev_lib = lib
        
    return table_str, inverted_table_str


def update_comment(text, token):
    comment_info = json.load(open(COMMNET_INFO_PATH, "r"))
    
    repo = comment_info["repo_path"]
    comment_id = comment_info["comment_id"]
    
    request_path = f"https://api.github.com/repos/{repo}/issues/comments/{comment_id}"
    headers = {
        'accept': 'application/vnd.github.v3.raw',
        'authorization': f'token {token}'
    }
    
    res = requests.patch(request_path, headers=headers, json={"body": text})
    if res.status_code == 200:
        print("Comment updated successfully")


def read_requirements(token):
    repos = json.load(open(REQ_DATA_PATH, "r"))
    
    requirements_dict = {}
    
    for repo_name, repo_data in repos.items():
        github_path = repo_data["git"]
        branch = repo_data["branch"]
        requirements = repo_data["requirements"]
        
        per_file_requirements = {}
        for req in requirements:
            request_path = f"https://api.github.com/repos/{github_path}/contents/{req}?ref={branch}"
            headers = {
                'accept': 'application/vnd.github.v3.raw',
                'authorization': f'token {token}'
            }
            
            res = requests.get(request_path, headers=headers)
            if res.status_code == 200:
                per_file_requirements[req] = res.text
                
        requirements_dict[repo_name] = per_file_requirements
        
    return requirements_dict


def detect_version_from_source(library, source):
    if "github.com" in source:
        # Detect version from git
        if library not in source:
            return ""
        postfix = source.split(library)[1]
        
        if "@" not in postfix:
            return ""
        postfix = postfix.split("@", 1)[1]
        version = postfix.split("#")[0]
        
        if not version.startswith("v"):
            version = version[:7]
            
        return version
    elif source.startswith("https://") or source.startswith("http://"):
        # Detect version from URL    
        if library + "-" not in source:
            return ""
        
        post_library = source.split(library + "-")[1]
        pre_metadata = post_library.split("%2B")[0]
        
        if all([re.match(r"[0-9a-zA-Z\.\-]", _) for _ in pre_metadata]):
            return pre_metadata
        else:
            return ""
    else:
        return ""


def postprocess_requirements(requirements_dict):
    processed_requirements = {}
    
    for repo_name, per_file_requirements in requirements_dict.items():
        processed_per_file_requirements = {}
        for req_file, req_text in per_file_requirements.items():
            lines = [_.strip() for _ in req_text.splitlines() if _] # remove empty lines
            lines = [_.split("#")[0].strip() for _ in lines] # remove comments
            lines = [_ for _ in lines if not _.startswith("-r")] # remove recursive requirements
            lib_with_version = []
            for line in lines:
                if "@" in line:
                    lib, source = line.split("@", 1)
                    version = detect_version_from_source(lib, source)
                    lib_with_version.append((lib, version, source))
                elif "==" in line:
                    lib, version = line.split("==", 1)
                    lib_with_version.append((lib, version, "PyPi"))
                    
            processed_per_file_requirements[req_file] = lib_with_version
        processed_requirements[repo_name] = processed_per_file_requirements
        
    return processed_requirements
