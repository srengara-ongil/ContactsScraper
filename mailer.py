import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class MailTrap:
    """
    A class to send emails using Mailtrap's SMTP server.
    """
    def __init__(self, smtp_user: str, smtp_password: str, smtp_host: str = 'live.smtp.mailtrap.io', smtp_port: int = 587):
        """
        Initialize MailTrap with SMTP credentials.

        Args:
            smtp_user: SMTP username (API token or user ID).
            smtp_password: SMTP password.
            smtp_host: SMTP server host (default: 'live.smtp.mailtrap.io').
            smtp_port: SMTP server port (default: 587).
        """
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port

    def send_email(self, from_email: str, to_email: str, subject: str, text_content: str, sender_name: str) -> bool:
        """
        Send an email using Mailtrap's SMTP server.

        Args:
            from_email: Sender's email address.
            to_email: Recipient's email address.
            subject: Subject of the email.
            text_content: Text content of the email.
            sender_name: Name of the sender.

        Returns:
            bool: True if the email was sent successfully, False otherwise.
        """
        try:
            # Create the email message
            msg = MIMEMultipart()
            msg['From'] = f"{sender_name} <{from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add text content
            msg.attach(MIMEText(text_content, 'plain'))

            # Connect to the SMTP server and send the email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()  # Upgrade the connection to secure
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False