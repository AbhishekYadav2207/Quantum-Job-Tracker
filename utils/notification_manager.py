# [file name]: utils/notification_manager.py
# [file content begin]
import json
import os
import logging
from datetime import datetime
import requests


class NotificationManager:
    def __init__(self, email=None, slack_webhook=None):
        self.email = email
        self.slack_webhook = slack_webhook
        self.notifications_file = "notifications.json"
        self.notifications = self.load_notifications()
        self.logger = logging.getLogger(__name__)

    def load_notifications(self):
        """Load notification history"""
        if os.path.exists(self.notifications_file):
            try:
                with open(self.notifications_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_notifications(self):
        """Save notification history"""
        try:
            with open(self.notifications_file, 'w') as f:
                json.dump(self.notifications, f)
        except Exception as e:
            self.logger.error(f"Error saving notifications: {e}")

    def send_notification(self, user_id, title, message, job_info=None):
        """Send a notification to a user"""
        notification = {
            'user_id': user_id,
            'title': title,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'job_info': job_info,
            'read': False
        }

        # Store notification
        if user_id not in self.notifications:
            self.notifications[user_id] = []

        self.notifications[user_id].append(notification)

        # Keep only last 100 notifications per user
        if len(self.notifications[user_id]) > 100:
            self.notifications[user_id] = self.notifications[user_id][-100:]

        self.save_notifications()

        # Send via Slack if configured
        if self.slack_webhook and job_info:
            self.send_slack_notification(title, message, job_info)

        self.logger.info(f"Notification sent to user {user_id}: {title}")

    def send_slack_notification(self, title, message, job_info):
        """Send notification to Slack"""
        try:
            payload = {
                "text": title,
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": title
                        }
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": message
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Job ID:*\n{job_info.get('job_id', 'Unknown')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Backend:*\n{job_info.get('backend', 'Unknown')}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Status:*\n{job_info.get('status', 'Unknown')}"
                            }
                        ]
                    }
                ]
            }

            response = requests.post(self.slack_webhook, json=payload)
            if response.status_code != 200:
                self.logger.error(f"Slack notification failed: {response.text}")

        except Exception as e:
            self.logger.error(f"Error sending Slack notification: {e}")

    def get_user_notifications(self, user_id, unread_only=False):
        """Get notifications for a user"""
        user_notifications = self.notifications.get(user_id, [])

        if unread_only:
            return [n for n in user_notifications if not n.get('read', False)]

        return user_notifications

    def mark_as_read(self, user_id, notification_index=None):
        """Mark notifications as read"""
        if user_id in self.notifications:
            if notification_index is not None:
                # Mark specific notification as read
                if 0 <= notification_index < len(self.notifications[user_id]):
                    self.notifications[user_id][notification_index]['read'] = True
            else:
                # Mark all notifications as read
                for notification in self.notifications[user_id]:
                    notification['read'] = True

            self.save_notifications()
# [file content end]