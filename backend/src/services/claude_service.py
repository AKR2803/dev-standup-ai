"""Claude API integration service."""
import json
from typing import List, Dict, Any, Optional
from anthropic import Anthropic
import boto3
from ..models.activity import DeveloperActivity
from ..models.standup import StandupItem, TeamStandup
from ..models.review import CodeReview, ReviewFinding, ReviewSeverity, DocstringGeneration, TestGeneration
from ..utils.config import settings
from ..utils.logger import get_logger
from datetime import datetime

logger = get_logger(__name__)


class ClaudeService:
    """Service for interacting with Claude API (Anthropic or Bedrock)."""
    
    def __init__(self):
        self.use_bedrock = settings.use_bedrock
        
        if self.use_bedrock:
            self.bedrock_client = boto3.client(
                'bedrock-runtime',
                region_name=settings.aws_region,
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key
            )
            self.model = settings.bedrock_model_id
        else:
            self.client = Anthropic(api_key=settings.claude_api_key)
            self.model = settings.claude_model
    
    async def _invoke_claude(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000) -> str:
        """Invoke Claude via Anthropic API or Bedrock."""
        if self.use_bedrock:
            return await self._invoke_bedrock(system_prompt, user_prompt, max_tokens)
        else:
            return await self._invoke_anthropic(system_prompt, user_prompt, max_tokens)
    
    async def _invoke_anthropic(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """Invoke Claude via Anthropic API."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return response.content[0].text
    
    async def _invoke_bedrock(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """Invoke Claude via AWS Bedrock."""
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "system": system_prompt,
            "messages": [
                {
                    "role": "user",
                    "content": user_prompt
                }
            ]
        }
        
        response = self.bedrock_client.invoke_model(
            modelId=self.model,
            body=json.dumps(body)
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
    
    async def generate_standup_summary(self, activities: List[DeveloperActivity]) -> TeamStandup:
        """Generate team standup summary from developer activities."""
        system_prompt = """You are an engineering assistant that creates concise, actionable standup summaries.
        
        Analyze the provided developer activity and generate a structured standup in this format:
        - Yesterday: What was accomplished (focus on merged PRs, completed features)
        - Today: What's planned (focus on open PRs, active work)
        - Blockers: Any impediments or issues that need attention
        
        Keep items concise and focus on business value. Group related work together."""
        
        activity_data = []
        for activity in activities:
            activity_summary = {
                "developer": activity.developer,
                "commits": [{"message": c.message, "files": c.files_changed} for c in activity.commits],
                "pull_requests": [{"title": pr.title, "state": pr.state, "url": pr.url} for pr in activity.pull_requests],
                "issues": [{"title": i.title, "state": i.state} for i in activity.issues]
            }
            activity_data.append(activity_summary)
        
        user_prompt = f"""Generate a standup summary for this team activity:

{json.dumps(activity_data, indent=2)}

Return a JSON response with this structure:
{{
    "team_items": [
        {{
            "developer": "name",
            "yesterday": ["item1", "item2"],
            "today": ["item1", "item2"],
            "blockers": ["blocker1"]
        }}
    ],
    "summary": "Brief team overview",
    "key_highlights": ["highlight1", "highlight2"],
    "team_blockers": ["team-wide blocker"]
}}"""
        
        try:
            response_text = await self._invoke_claude(system_prompt, user_prompt, 2000)
            result = json.loads(response_text)
            
            team_items = [StandupItem(**item) for item in result["team_items"]]
            
            standup = TeamStandup(
                date=datetime.utcnow(),
                team_items=team_items,
                summary=result.get("summary"),
                key_highlights=result.get("key_highlights", []),
                team_blockers=result.get("team_blockers", [])
            )
            
            logger.info("Generated standup summary", developers=len(team_items))
            return standup
            
        except Exception as e:
            logger.error("Failed to generate standup summary", error=str(e))
            # Return empty standup on failure
            return TeamStandup(
                date=datetime.utcnow(),
                team_items=[],
                summary="Failed to generate summary"
            )
    
    async def review_pull_request(self, pr_number: int, pr_title: str, diff_content: str) -> CodeReview:
        """Generate AI code review for a pull request."""
        system_prompt = """You are a senior software engineer conducting a thorough code review.
        
        Analyze the provided code diff and provide structured feedback focusing on:
        1. Logic and correctness
        2. Security vulnerabilities
        3. Performance implications
        4. Code style and maintainability
        5. Test coverage gaps
        
        Be constructive and specific. Provide actionable suggestions."""
        
        user_prompt = f"""Review this pull request:

Title: {pr_title}
PR Number: {pr_number}

Diff:
{diff_content}

Return a JSON response with this structure:
{{
    "summary": "Brief review summary",
    "overall_score": 8,
    "findings": [
        {{
            "file_path": "path/to/file.py",
            "line_number": 42,
            "severity": "medium",
            "category": "logic",
            "message": "Potential null pointer exception",
            "suggestion": "Add null check before accessing property",
            "code_snippet": "relevant code"
        }}
    ],
    "suggestions": ["Overall suggestion 1", "Overall suggestion 2"],
    "approved": false
}}

Severity levels: critical, high, medium, low, info
Categories: logic, security, performance, style, testing"""
        
        try:
            response_text = await self._invoke_claude(system_prompt, user_prompt, 3000)
            result = json.loads(response_text)
            
            findings = []
            for finding_data in result.get("findings", []):
                finding = ReviewFinding(
                    file_path=finding_data["file_path"],
                    line_number=finding_data.get("line_number"),
                    severity=ReviewSeverity(finding_data["severity"]),
                    category=finding_data["category"],
                    message=finding_data["message"],
                    suggestion=finding_data.get("suggestion"),
                    code_snippet=finding_data.get("code_snippet")
                )
                findings.append(finding)
            
            review = CodeReview(
                pr_number=pr_number,
                pr_title=pr_title,
                timestamp=datetime.utcnow(),
                summary=result["summary"],
                overall_score=result["overall_score"],
                findings=findings,
                suggestions=result.get("suggestions", []),
                approved=result.get("approved", False)
            )
            
            logger.info("Generated PR review", pr_number=pr_number, findings=len(findings))
            return review
            
        except Exception as e:
            logger.error("Failed to generate PR review", pr_number=pr_number, error=str(e))
            return CodeReview(
                pr_number=pr_number,
                pr_title=pr_title,
                timestamp=datetime.utcnow(),
                summary="Failed to generate review",
                overall_score=5,
                findings=[],
                suggestions=[],
                approved=False
            )
    
    async def generate_docstring(self, file_path: str, function_name: str, code: str) -> DocstringGeneration:
        """Generate docstring for a function."""
        system_prompt = """You are a documentation expert. Generate comprehensive Google-style docstrings for Python functions.
        
        Include:
        - Brief description
        - Args with types and descriptions
        - Returns with type and description
        - Raises for exceptions
        - Example usage if helpful"""
        
        user_prompt = f"""Generate a Google-style docstring for this function:

File: {file_path}
Function: {function_name}

Code:
{code}

Return only the docstring content (without triple quotes)."""
        
        try:
            docstring = await self._invoke_claude(system_prompt, user_prompt, 1000)
            docstring = docstring.strip()
            
            result = DocstringGeneration(
                file_path=file_path,
                function_name=function_name,
                original_code=code,
                generated_docstring=docstring,
                style="google"
            )
            
            logger.info("Generated docstring", function=function_name)
            return result
            
        except Exception as e:
            logger.error("Failed to generate docstring", function=function_name, error=str(e))
            return DocstringGeneration(
                file_path=file_path,
                function_name=function_name,
                original_code=code,
                generated_docstring="Failed to generate docstring",
                style="google"
            )
    
    async def generate_unit_test(self, file_path: str, function_name: str, code: str) -> TestGeneration:
        """Generate unit test for a function."""
        system_prompt = """You are a QA engineer expert in writing comprehensive unit tests.
        
        Generate pytest-compatible unit tests that:
        - Test happy path scenarios
        - Test edge cases and error conditions
        - Use appropriate fixtures and mocks
        - Follow testing best practices
        - Achieve high code coverage"""
        
        user_prompt = f"""Generate comprehensive pytest unit tests for this function:

File: {file_path}
Function: {function_name}

Code:
{code}

Return complete test code including imports and test class/functions."""
        
        try:
            test_code = await self._invoke_claude(system_prompt, user_prompt, 2000)
            test_code = test_code.strip()
            
            result = TestGeneration(
                file_path=file_path,
                function_name=function_name,
                original_code=code,
                generated_test=test_code,
                test_framework="pytest",
                coverage_estimate=85  # Estimated coverage
            )
            
            logger.info("Generated unit test", function=function_name)
            return result
            
        except Exception as e:
            logger.error("Failed to generate unit test", function=function_name, error=str(e))
            return TestGeneration(
                file_path=file_path,
                function_name=function_name,
                original_code=code,
                generated_test="# Failed to generate test",
                test_framework="pytest"
            )