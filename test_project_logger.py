from project_logger import ProjectLogger
import os

def main():
    # Get current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Create log file path in current directory
    log_file = os.path.join(current_dir, 'project_log.csv')
    
    # Initialize ProjectLogger
    logger = ProjectLogger(log_file)
    
    # Test logging some projects
    test_projects = [
        "Project Alpha",
        "Project Beta",
        "Project Gamma"
    ]
    
    print("Logging test projects...")
    for project in test_projects:
        success = logger.log_project(project)
        if success:
            print(f"Successfully logged: {project}")
        else:
            print(f"Failed to log: {project}")
    
    # Display all logs
    print("\nRetrieving all logs:")
    all_logs = logger.get_logs()
    print(all_logs)
    
    print(f"\nLog file created at: {log_file}")

if __name__ == "__main__":
    main()
