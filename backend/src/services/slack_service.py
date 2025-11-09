"""Slack integration service."""
import json
import requests
from typing import Dict, Any, Optional
from ..models.standup import TeamStandup
from ..models.review import CodeReview
from ..utils.config import settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SlackService:
    """Service for Slack integration."""
    
    def __init__(self):
        self.webhook_url = settings.slack_webhook_url
    
    def post_standup_summary(self, standup: TeamStandup) -> bool:
        """Post standup summary to Slack channel."""
        try:
            # Format standup message
            blocks = self._format_standup_message(standup)
            
            payload = {
                "text": "Daily Standup Summary",
                "blocks": blocks
            }
            
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info("Posted standup to Slack via webhook")
            return True
            
        except Exception as e:
            logger.error("Failed to post standup to Slack", error=str(e))
            return False
    
    def post_pr_review(self, review: CodeReview) -> bool:
        """Post PR review summary to Slack channel."""
        try:
            blocks = self._format_review_message(review)
            
            payload = {
                "text": f"PR Review: {review.pr_title}",
                "blocks": blocks
            }
            
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            
            logger.info("Posted PR review to Slack via webhook", pr_number=review.pr_number)
            return True
            
        except Exception as e:
            logger.error("Failed to post PR review to Slack", error=str(e))
            return False
    
    def _format_standup_message(self, standup: TeamStandup) -> list:
        """Format standup data as Slack blocks."""
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚀 Daily Standup - {standup.date.strftime('%B %d, %Y')}"
                }
            }
        ]
        
        if standup.summary:
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Team Summary:* {standup.summary}"
                }
            })
        
        # Add team highlights
        if standup.key_highlights:
            highlights_text = "\n".join([f"• {highlight}" for highlight in standup.key_highlights])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🎯 Key Highlights:*\n{highlights_text}"
                }
            })
        
        # Add individual developer updates
        for item in standup.team_items:
            developer_blocks = self._format_developer_standup(item)
            blocks.extend(developer_blocks)
        
        # Add team blockers
        if standup.team_blockers:
            blockers_text = "\n".join([f"• {blocker}" for blocker in standup.team_blockers])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🚧 Team Blockers:*\n{blockers_text}"
                }
            })
        
        return blocks
    
    def _format_developer_standup(self, item) -> list:
        """Format individual developer standup."""
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*👤 {item.developer}*"
                }
            }
        ]
        
        # Yesterday's work
        if item.yesterday:
            yesterday_text = "\n".join([f"• {work}" for work in item.yesterday])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Yesterday:*\n{yesterday_text}"
                }
            })
        
        # Today's plan
        if item.today:
            today_text = "\n".join([f"• {work}" for work in item.today])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Today:*\n{today_text}"
                }
            })
        
        # Blockers
        if item.blockers:
            blockers_text = "\n".join([f"• {blocker}" for blocker in item.blockers])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🚧 Blockers:*\n{blockers_text}"
                }
            })
        
        # Add divider
        blocks.append({"type": "divider"})
        
        return blocks
    
    def _format_review_message(self, review: CodeReview) -> list:
        """Format PR review as Slack blocks."""
        # Determine emoji based on score
        score_emoji = "🟢" if review.overall_score >= 8 else "🟡" if review.overall_score >= 6 else "🔴"
        
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"📝 PR Review: {review.pr_title}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Summary:* {review.summary}\n*Score:* {score_emoji} {review.overall_score}/10"
                }
            }
        ]
        
        # Add critical/high issues
        critical_issues = review.critical_issues
        high_issues = review.high_issues
        
        if critical_issues > 0 or high_issues > 0:
            issues_text = []
            if critical_issues > 0:
                issues_text.append(f"🔴 {critical_issues} Critical")
            if high_issues > 0:
                issues_text.append(f"🟠 {high_issues} High")
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Issues Found:* {', '.join(issues_text)}"
                }
            })
        
        # Add suggestions
        if review.suggestions:
            suggestions_text = "\n".join([f"• {suggestion}" for suggestion in review.suggestions[:3]])  # Limit to 3
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*💡 Suggestions:*\n{suggestions_text}"
                }
            })
        
        return blocks
    
    def handle_slash_command(self, command: str, text: str, user_id: str) -> Dict[str, Any]:
        """Handle Slack slash commands."""
        if command == "/standup":
            return {
                "response_type": "ephemeral",
                "text": "Generating standup summary... This may take a moment.",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "⏳ Generating your team's standup summary...\nI'll post it to the channel once ready!"
                        }
                    }
                ]
            }
        elif command == "/review":
            return {
                "response_type": "ephemeral",
                "text": "Starting PR review process...",
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "🔍 Analyzing recent pull requests...\nReviews will be posted shortly!"
                        }
                    }
                ]
            }
        else:
            return {
                "response_type": "ephemeral",
                "text": "Unknown command. Available commands: /standup, /review"
            }