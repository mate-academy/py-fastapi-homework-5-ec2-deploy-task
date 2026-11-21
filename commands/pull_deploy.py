import argparse
import json
import subprocess
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def workflow_runs(repository, revision):
    query = urlencode({
        "branch": "main",
        "head_sha": revision,
        "status": "success",
        "per_page": 1,
    })
    url = f"https://api.github.com/repos/{repository}/actions/workflows/cd-pipeline.yml/runs?{query}"
    request = Request(url, headers={"Accept": "application/vnd.github+json"})
    with urlopen(request, timeout=15) as response:
        return json.load(response)["workflow_runs"]


def deploy_if_verified(repository, revision, marker, deploy):
    if marker.exists() and marker.read_text().strip() == revision:
        return

    verified = any(
        run["head_sha"] == revision and run["head_branch"] == "main"
        and run["conclusion"] == "success" and run["event"] in {"push", "workflow_dispatch"}
        for run in workflow_runs(repository, revision)
    )
    if not verified:
        print("Waiting for successful GitHub checks for the current main revision.")
        return

    deploy(revision)
    pending_marker = marker.with_suffix(".tmp")
    pending_marker.write_text(revision + "\n")
    pending_marker.replace(marker)


def main():
    parser = argparse.ArgumentParser(description="Deploy the verified main revision on EC2.")
    parser.add_argument("repository", help="Public GitHub repository in owner/name format")
    parser.add_argument("checkout", type=Path)
    args = parser.parse_args()
    checkout = args.checkout.resolve()

    subprocess.run(["git", "fetch", "origin", "refs/heads/main"], cwd=checkout, check=True)
    revision = subprocess.check_output(["git", "rev-parse", "FETCH_HEAD"], cwd=checkout, text=True).strip()
    git_dir = subprocess.check_output(
        ["git", "rev-parse", "--absolute-git-dir"], cwd=checkout, text=True
    ).strip()

    def deploy(verified_revision):
        subprocess.run(["bash", "commands/deploy.sh", verified_revision], cwd=checkout, check=True)

    deploy_if_verified(args.repository, revision, Path(git_dir) / "ec2-deployed-revision", deploy)


if __name__ == "__main__":
    main()
