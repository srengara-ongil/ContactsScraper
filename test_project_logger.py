import pandas as pd
from datetime import datetime
import os
from mailer import MailTrap

class ProjectLogger:
    """
    A class to log project names with timestamps to a CSV file.
    """
    def __init__(self, log_file='project_log.csv'):
        """
        Initialize ProjectLogger with a log file path.
        
        Args:
            log_file: Path to the CSV file (default: 'project_log.csv')
        """
        self.log_file = log_file
        self._initialize_log_file()
        # Initialize MailTrap with SMTP credentials
        self.mailer = MailTrap(
            smtp_user='api',  # Replace with your Mailtrap SMTP username
            smtp_password='1fe7f989c04615e797eb0a4379fafd11'  # Replace with your Mailtrap SMTP password
        )
        self.sender_email = 'hello@demomailtrap.co'
        self.recipient_email = 'srini.rengara@ongil.ai'

    def _initialize_log_file(self):
        """Create the log file with headers if it doesn't exist."""
        if not os.path.exists(self.log_file):
            df = pd.DataFrame(columns=['timestamp', 'project_name'])
            df.to_csv(self.log_file, index=False)
    
    def send_email(self, project_name: str) -> bool:
        """Send email notification about new project log."""
        try:
            email_sent = self.mailer.send_email(
                from_email=self.sender_email,
                to_email=self.recipient_email,
                subject='New Project Search Alert',
                text_content=f'New project search logged: {project_name}',
                sender_name='Project Logger'
            )
            return email_sent
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def log_project(self, project_name: str) -> bool:
        """
        Log a project name and send email notification.
        
        Args:
            project_name: Name of the project to log
            
        Returns:
            bool: True if logging successful, False otherwise
        """
        try:
            # Get current timestamp
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Create new row
            new_row = pd.DataFrame({
                'timestamp': [current_time],
                'project_name': [project_name]
            })
            
            # Append to CSV
            new_row.to_csv(self.log_file, mode='a', header=False, index=False)
            
            # Send email notification using MailTrap
            email_sent = self.send_email(project_name)
            if not email_sent:
                print("Warning: Email notification failed")
                
            return True
            
        except Exception as e:
            print(f"Error logging project: {e}")
            return False
    
    def get_logs(self) -> pd.DataFrame:
        """
        Retrieve all logged projects.
        
        Returns:
            pandas.DataFrame: DataFrame containing all logs
        """
        try:
            return pd.read_csv(self.log_file)
        except Exception as e:
            print(f"Error reading logs: {e}")
            return pd.DataFrame()

# Example usage
if __name__ == "__main__":
    logger = ProjectLogger()
    
    # Log a project
    logger.log_project("Test Project")
    
    # Display all logs
    print(logger.get_logs())