"""
Resend Sender - Resend 邮件发送
使用 Resend API 发送 HTML 邮件
"""
import resend
from typing import Dict, Optional


class ResendSender:
    """Resend 邮件发送"""

    def __init__(self, api_key: str):
        """
        初始化

        Args:
            api_key: Resend API Key
        """
        self.api_key = api_key
        resend.api_key = api_key

    def send_email(
        self,
        to: str,
        subject: str,
        html_content: str,
        from_email: str = "onboarding@resend.dev"
    ) -> Dict:
        """
        发送邮件

        Args:
            to: 收件人邮箱
            subject: 邮件标题
            html_content: HTML 内容
            from_email: 发件人邮箱

        Returns:
            {"success": bool, "message": str, "id": str}
        """
        if not to:
            return {"success": False, "message": "收件人邮箱为空"}

        try:
            print(f"📧 正在发送邮件到: {to}")

            params = {
                "from": from_email,
                "to": [to],
                "subject": subject,
                "html": html_content,
            }

            response = resend.Emails.send(params)

            print(f"✅ 邮件发送成功! ID: {response.get('id')}")

            return {
                "success": True,
                "message": "邮件发送成功",
                "id": response.get("id"),
                "response": response
            }

        except Exception as e:
            error_msg = str(e)
            print(f"❌ 邮件发送失败: {error_msg}")

            return {
                "success": False,
                "message": error_msg,
                "id": None
            }

    def send_with_text(
        self,
        to: str,
        subject: str,
        html_content: str,
        text_content: str = "",
        from_email: str = "onboarding@resend.dev"
    ) -> Dict:
        """
        发送带纯文本备用的邮件

        Args:
            to: 收件人邮箱
            subject: 邮件标题
            html_content: HTML 内容
            text_content: 纯文本内容（备用）
            from_email: 发件人邮箱

        Returns:
            {"success": bool, "message": str, "id": str}
        """
        if not to:
            return {"success": False, "message": "收件人邮箱为空"}

        try:
            print(f"📧 正在发送邮件到: {to}")

            params = {
                "from": from_email,
                "to": [to],
                "subject": subject,
                "html": html_content,
            }

            if text_content:
                params["text"] = text_content

            response = resend.Emails.send(params)

            print(f"✅ 邮件发送成功! ID: {response.get('id')}")

            return {
                "success": True,
                "message": "邮件发送成功",
                "id": response.get("id"),
                "response": response
            }

        except Exception as e:
            error_msg = str(e)
            print(f"❌ 邮件发送失败: {error_msg}")

            return {
                "success": False,
                "message": error_msg,
                "id": None
            }


def send_email(
    api_key: str,
    to: str,
    subject: str,
    html_content: str,
    from_email: str = "onboarding@resend.dev"
) -> Dict:
    """便捷函数：发送邮件"""
    sender = ResendSender(api_key)
    return sender.send_email(to, subject, html_content, from_email)
