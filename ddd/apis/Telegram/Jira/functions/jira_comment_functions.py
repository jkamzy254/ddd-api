from datetime import datetime
import json

def process_data(data, author):
        
        def format_date(dt):
            day = dt.strftime('%d')  # Extract the day part
            day_ordinal = int(day)
            if 10 <= day_ordinal % 100 <= 20:
                suffix = 'th'
            else:
                suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day_ordinal % 10, 'th')
            return dt.strftime(f'%d{suffix} %b, %Y')

        # Format the time
        def format_time(dt):
            return dt.strftime('%I:%M%p').lower()
        
        today = datetime.now()
        intro = f'JIRA UPDATES\n\n📆 {format_date(today)}\n\n'
        output_lines = []
    
        for user in data:
            name = user["Name"]
            comments = user.get('Comments')
            
            if comments:
                if comments == 'None':
                    issues = "None"
                else:
                    try:
                        comments_list = json.loads(comments)
                        issues = set(comment['IssueName'] for comment in comments_list)
                    except (json.JSONDecodeError, TypeError):
                        issues = set()
            else:
                issues = set()
            
            # Format the output
            if issues:
                if issues == 'None':
                    output_lines.append(f"▪️{name}:\n- None")                    
                else:
                    issues_str = '\n- '.join(issues)
                    output_lines.append(f"▪️{name}:\n- {issues_str}")
            else:
                output_lines.append(f"{name}:")
        
        return intro+'\n\n'.join(output_lines) + f"\n\n---------------------\nLast Edited by {author} ({format_time(today)})"
