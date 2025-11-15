"""GitHub API integration service."""
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from ..models.activity import GitHubCommit, GitHubPullRequest, GitHubIssue, DeveloperActivity
from ..utils.config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class GitHubService:
    """Service for interacting with GitHub API."""
    
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {settings.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.repo_owner = settings.github_repo_owner
        self.repo_name = settings.github_repo_name
    
    async def get_recent_commits(self, since: datetime) -> List[GitHubCommit]:
        """Fetch recent commits from the repository."""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/commits"
        params = {
            "since": since.isoformat(),
            "per_page": 100
        }
        
        try:
            logger.info("Fetching commits", url=url, params=params)
            response = requests.get(url, headers=self.headers, params=params)
            logger.info("GitHub API response", status_code=response.status_code)
            response.raise_for_status()
            commits_data = response.json()
            
            commits = []
            for commit_data in commits_data:
                commit = GitHubCommit(
                    sha=commit_data["sha"],
                    message=commit_data["commit"]["message"],
                    author=commit_data["commit"]["author"]["name"],
                    timestamp=datetime.fromisoformat(
                        commit_data["commit"]["author"]["date"].replace("Z", "+00:00")
                    ),
                    url=commit_data["html_url"],
                    files_changed=await self._get_commit_files(commit_data["sha"])
                )
                commits.append(commit)
            
            logger.info("Fetched commits", count=len(commits))
            return commits
            
        except requests.RequestException as e:
            logger.error("Failed to fetch commits", error=str(e))
            return []
    
    async def get_recent_pull_requests(self, since: datetime) -> List[GitHubPullRequest]:
        """Fetch recent pull requests from the repository."""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls"
        params = {
            "state": "all",
            "sort": "updated",
            "direction": "desc",
            "per_page": 50
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            prs_data = response.json()
            
            prs = []
            for pr_data in prs_data:
                updated_at = datetime.fromisoformat(
                    pr_data["updated_at"].replace("Z", "+00:00")
                )
                if updated_at < since:
                    continue
                
                pr = GitHubPullRequest(
                    number=pr_data["number"],
                    title=pr_data["title"],
                    body=pr_data["body"],
                    author=pr_data["user"]["login"],
                    state=pr_data["state"],
                    created_at=datetime.fromisoformat(
                        pr_data["created_at"].replace("Z", "+00:00")
                    ),
                    updated_at=updated_at,
                    url=pr_data["html_url"],
                    diff_url=pr_data["diff_url"],
                    additions=pr_data.get("additions", 0),
                    deletions=pr_data.get("deletions", 0)
                )
                prs.append(pr)
            
            logger.info("Fetched pull requests", count=len(prs))
            return prs
            
        except requests.RequestException as e:
            logger.error("Failed to fetch pull requests", error=str(e))
            return []
    
    async def get_recent_issues(self, since: datetime) -> List[GitHubIssue]:
        """Fetch recent issues from the repository."""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/issues"
        params = {
            "state": "all",
            "sort": "updated",
            "direction": "desc",
            "per_page": 50
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            issues_data = response.json()
            
            issues = []
            for issue_data in issues_data:
                # Skip pull requests (they appear in issues endpoint)
                if "pull_request" in issue_data:
                    continue
                
                updated_at = datetime.fromisoformat(
                    issue_data["updated_at"].replace("Z", "+00:00")
                )
                if updated_at < since:
                    continue
                
                issue = GitHubIssue(
                    number=issue_data["number"],
                    title=issue_data["title"],
                    body=issue_data["body"],
                    author=issue_data["user"]["login"],
                    state=issue_data["state"],
                    created_at=datetime.fromisoformat(
                        issue_data["created_at"].replace("Z", "+00:00")
                    ),
                    updated_at=updated_at,
                    url=issue_data["html_url"],
                    labels=[label["name"] for label in issue_data["labels"]]
                )
                issues.append(issue)
            
            logger.info("Fetched issues", count=len(issues))
            return issues
            
        except requests.RequestException as e:
            logger.error("Failed to fetch issues", error=str(e))
            return []
    
    async def get_pull_request(self, pr_number: int) -> Optional[GitHubPullRequest]:
        """Fetch a specific pull request."""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            pr_data = response.json()
            
            return GitHubPullRequest(
                number=pr_data["number"],
                title=pr_data["title"],
                body=pr_data["body"],
                author=pr_data["user"]["login"],
                state=pr_data["state"],
                created_at=datetime.fromisoformat(
                    pr_data["created_at"].replace("Z", "+00:00")
                ),
                updated_at=datetime.fromisoformat(
                    pr_data["updated_at"].replace("Z", "+00:00")
                ),
                url=pr_data["html_url"],
                diff_url=pr_data["diff_url"],
                additions=pr_data.get("additions", 0),
                deletions=pr_data.get("deletions", 0)
            )
        except requests.RequestException as e:
            logger.error("Failed to fetch pull request", pr_number=pr_number, error=str(e))
            return None
    
    async def get_pr_diff(self, pr_number: int) -> Optional[str]:
        """Fetch the diff for a specific pull request."""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/pulls/{pr_number}"
        headers = {**self.headers, "Accept": "application/vnd.github.v3.diff"}
        
        try:
            logger.info("Fetching PR diff", pr_number=pr_number, url=url)
            response = requests.get(url, headers=headers)
            logger.info("PR diff response", pr_number=pr_number, status_code=response.status_code, content_length=len(response.text))
            response.raise_for_status()
            
            diff_content = response.text
            if not diff_content or not diff_content.strip():
                logger.warning("Empty diff content received", pr_number=pr_number)
                return None
            
            logger.info("Successfully fetched PR diff", pr_number=pr_number, diff_preview=diff_content[:200])
            return diff_content
        except requests.RequestException as e:
            logger.error("Failed to fetch PR diff", pr_number=pr_number, error=str(e), status_code=getattr(e.response, 'status_code', None))
            return None
    
    async def get_file_content(self, file_path: str, branch: str = "main") -> Optional[str]:
        """Fetch file content from GitHub repository."""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}"
        params = {"ref": branch}
        
        try:
            logger.info("Fetching file content", url=url, file_path=file_path, branch=branch)
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code == 404:
                logger.error("File not found", file_path=file_path, branch=branch, repo=f"{self.repo_owner}/{self.repo_name}")
                return None
            
            response.raise_for_status()
            file_data = response.json()
            
            if file_data.get("encoding") == "base64":
                import base64
                content = base64.b64decode(file_data["content"]).decode('utf-8')
                logger.info("Successfully fetched file content", file_path=file_path, content_length=len(content))
                return content
            else:
                content = file_data.get("content", "")
                logger.info("Successfully fetched file content (non-base64)", file_path=file_path, content_length=len(content))
                return content
                
        except requests.RequestException as e:
            logger.error("Failed to fetch file content", file_path=file_path, branch=branch, error=str(e), status_code=getattr(e.response, 'status_code', None))
            return None
    
    async def _get_commit_files(self, sha: str) -> List[str]:
        """Get list of files changed in a commit."""
        url = f"{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/commits/{sha}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            commit_data = response.json()
            
            return [file_data["filename"] for file_data in commit_data.get("files", [])]
        except requests.RequestException:
            return []
    
    async def aggregate_developer_activity(self, hours: int) -> List[DeveloperActivity]:
        """Aggregate all activity by developer."""
        since = datetime.now(timezone.utc) - timedelta(hours=hours)
        logger.info("Aggregating activity", since=since.isoformat(), hours=hours)
        
        commits = await self.get_recent_commits(since)
        prs = await self.get_recent_pull_requests(since)
        issues = await self.get_recent_issues(since)
        
        logger.info("Fetched GitHub data", commits=len(commits), prs=len(prs), issues=len(issues))
        
        # Group by developer
        developers = {}
        
        for commit in commits:
            if commit.author not in developers:
                developers[commit.author] = DeveloperActivity(
                    developer=commit.author,
                    date=since
                )
            developers[commit.author].commits.append(commit)
        
        for pr in prs:
            if pr.author not in developers:
                developers[pr.author] = DeveloperActivity(
                    developer=pr.author,
                    date=since
                )
            developers[pr.author].pull_requests.append(pr)
        
        for issue in issues:
            if issue.author not in developers:
                developers[issue.author] = DeveloperActivity(
                    developer=issue.author,
                    date=since
                )
            developers[issue.author].issues.append(issue)
        
        return list(developers.values())