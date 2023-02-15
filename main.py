import argparse

from utils import read_requirements, postprocess_requirements, prettify_table, update_comment

def main(token, output_path, write_github_comment=False):
    requirements_dict = read_requirements(token)
    processed_requirements = postprocess_requirements(requirements_dict)
    table_str, inverted_tabel_str = prettify_table(processed_requirements)
    
    comment = "## Requirements for all repositories\n\n" \
              f"{table_str}\n\n" \
              "## Repositories required by\n\n" \
              f"{inverted_tabel_str}"
    
    with open(output_path, "w") as f:
        f.write(comment)
        
    if write_github_comment:
        update_comment(comment, token)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", "-t", help="GitHub token", required=True)
    parser.add_argument("--output", "-o", help="Output file path", default="requirements.md")
    parser.add_argument("--write_github_comment", help="Write the output to a GitHub comment", action="store_true")
    args = parser.parse_args()
    
    main(args.token, args.output, args.write_github_comment)