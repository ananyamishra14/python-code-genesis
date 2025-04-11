
"""
AI utilities for the Job-to-Be-Done Marketplace.

This file provides functions for AI-powered features including task decomposition,
contractor matching, and smart contract generation.
"""

import openai
import json
import os
from datetime import datetime, timedelta

# Configure OpenAI API
openai.api_key = os.environ.get('OPENAI_API_KEY')

def decompose_job(job_description, budget, timeline, success_criteria=None):
    """
    Use AI to break down a job into smaller, manageable tasks.
    
    Args:
        job_description (str): Detailed description of the problem/job
        budget (float): Total budget allocated for the job
        timeline (int): Timeline in days for the job completion
        success_criteria (str, optional): Success criteria specified by the client
        
    Returns:
        list: List of task dictionaries with details for each task
    """
    prompt = f"""
    As an AI project manager, decompose the following job into 3-8 specific tasks:
    
    JOB DESCRIPTION: {job_description}
    TOTAL BUDGET: ${budget}
    TIMELINE: {timeline} days
    {"SUCCESS CRITERIA: " + success_criteria if success_criteria else ""}
    
    For each task, provide:
    1. Task title (clear and specific)
    2. Detailed description of what needs to be done
    3. Estimated budget allocation (sum should not exceed total budget of ${budget})
    4. Timeline in days (all tasks combined should not exceed {timeline} days)
    5. Required skills (comma separated)
    6. Difficulty level (easy, medium, or hard)
    
    Format the response as a JSON array of task objects with properties:
    title, description, budget, timeline, skills, difficulty.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a project management AI that specializes in breaking down complex problems into manageable tasks."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        # Extract and parse the JSON response
        tasks_json = response.choices[0].message.content
        tasks = extract_json_from_response(tasks_json)
        
        # Validate the tasks
        if validate_tasks(tasks, budget, timeline):
            return tasks
        else:
            # If validation fails, try again with more explicit instructions
            return decompose_job_retry(job_description, budget, timeline, success_criteria)
            
    except Exception as e:
        print(f"Error in AI decomposition: {e}")
        # Fallback to a simpler approach
        return generate_fallback_tasks(job_description, budget, timeline)

def decompose_job_retry(job_description, budget, timeline, success_criteria=None):
    """Retry task decomposition with more explicit instructions"""
    prompt = f"""
    Decompose this job into exactly 4 well-defined tasks:
    
    JOB DESCRIPTION: {job_description}
    TOTAL BUDGET: ${budget}
    TIMELINE: {timeline} days
    
    The sum of task budgets MUST EXACTLY EQUAL ${budget}.
    The sum of task timelines MUST NOT EXCEED {timeline} days.
    
    Format as a clean JSON array of objects, each with these properties:
    - title (string)
    - description (string)
    - budget (number, no $ sign)
    - timeline (number, integer days)
    - skills (array of strings)
    - difficulty (string: "easy", "medium", or "hard")
    
    Return ONLY the JSON array and nothing else.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a JSON-generating assistant that produces clean, valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=1500
        )
        
        # Extract and parse the JSON response
        tasks_json = response.choices[0].message.content
        return extract_json_from_response(tasks_json)
        
    except Exception as e:
        print(f"Error in AI decomposition retry: {e}")
        return generate_fallback_tasks(job_description, budget, timeline)

def extract_json_from_response(response_text):
    """Extract JSON from the text response, handling potential formatting issues"""
    try:
        # Try to parse the entire response as JSON
        return json.loads(response_text)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON content from the response
        try:
            # Find content between ```json and ```
            import re
            json_match = re.search(r'```json\n([\s\S]*?)\n```', response_text)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Look for content between [ and ]
            json_match = re.search(r'\[([\s\S]*?)\]', response_text)
            if json_match:
                return json.loads(f'[{json_match.group(1)}]')
                
            return []
        except Exception:
            return []

def validate_tasks(tasks, total_budget, total_timeline):
    """
    Validate that the tasks meet the required constraints
    
    Args:
        tasks (list): List of task dictionaries
        total_budget (float): Total budget for the job
        total_timeline (int): Total timeline in days
        
    Returns:
        bool: True if tasks are valid, False otherwise
    """
    if not tasks or not isinstance(tasks, list):
        return False
    
    # Check required fields
    required_fields = ['title', 'description', 'budget', 'timeline', 'skills', 'difficulty']
    for task in tasks:
        if not all(field in task for field in required_fields):
            return False
    
    # Check budget and timeline constraints
    budget_sum = sum(task['budget'] for task in tasks)
    timeline_max = max(task['timeline'] for task in tasks)
    
    # Allow for small floating point differences in budget
    budget_valid = abs(budget_sum - total_budget) < (total_budget * 0.05)
    timeline_valid = timeline_max <= total_timeline
    
    return budget_valid and timeline_valid

def generate_fallback_tasks(job_description, budget, timeline):
    """
    Generate fallback tasks when AI decomposition fails
    
    Args:
        job_description (str): Description of the job
        budget (float): Total budget
        timeline (int): Timeline in days
        
    Returns:
        list: List of simplified task dictionaries
    """
    # Generate 3 generic tasks
    num_tasks = 3
    task_budget = budget / num_tasks
    task_timeline = timeline / 3
    
    base_skills = ["Research", "Content Creation", "Web Development", "Marketing"]
    difficulties = ["easy", "medium", "hard"]
    
    tasks = []
    
    # Planning task
    tasks.append({
        'title': "Planning and Research",
        'description': f"Research and create a detailed plan for: {job_description}",
        'budget': task_budget * 0.2,
        'timeline': max(1, int(task_timeline * 0.2)),
        'skills': ["Research", "Planning", "Analysis"],
        'difficulty': "medium"
    })
    
    # Implementation task
    tasks.append({
        'title': "Implementation and Development",
        'description': f"Execute the core development work for: {job_description}",
        'budget': task_budget * 0.6,
        'timeline': max(1, int(task_timeline * 0.6)),
        'skills': ["Development", "Implementation", "Technical Skills"],
        'difficulty': "hard"
    })
    
    # Testing and refinement
    tasks.append({
        'title': "Testing and Refinement",
        'description': f"Test, validate and refine the work completed for: {job_description}",
        'budget': task_budget * 0.2,
        'timeline': max(1, int(task_timeline * 0.2)),
        'skills': ["Testing", "Quality Assurance", "Refinement"],
        'difficulty': "medium"
    })
    
    return tasks

def match_contractors(task, contractors):
    """
    Use AI to match the most suitable contractors for a given task
    
    Args:
        task (dict): Task details
        contractors (list): List of available contractors
        
    Returns:
        list: Ranked list of contractor IDs
    """
    # Implementation would use natural language processing to match skill requirements
    # For now, this is a simplified version
    
    required_skills = task['skills_required'].lower().split(',')
    required_skills = [skill.strip() for skill in required_skills]
    
    matches = []
    for contractor in contractors:
        if not contractor.skills:
            continue
            
        contractor_skills = contractor.skills.lower().split(',')
        contractor_skills = [skill.strip() for skill in contractor_skills]
        
        # Calculate skills match score (0-100)
        matching_skills = set(required_skills) & set(contractor_skills)
        if not matching_skills:
            continue
            
        match_score = (len(matching_skills) / len(required_skills)) * 100
        
        matches.append({
            'contractor_id': contractor.id,
            'score': match_score
        })
    
    # Sort by match score (descending)
    matches.sort(key=lambda x: x['score'], reverse=True)
    
    # Return contractor IDs in ranked order
    return [match['contractor_id'] for match in matches]

def generate_smart_contract(task, contractor, client):
    """
    Generate a smart contract for a task
    
    Args:
        task (dict): Task details
        contractor (dict): Contractor details
        client (dict): Client details
        
    Returns:
        str: Smart contract text
    """
    today = datetime.now()
    deadline = today + timedelta(days=task['timeline'])
    
    contract = f"""
    SMART CONTRACT AGREEMENT
    
    This agreement is made on {today.strftime('%Y-%m-%d')} between:
    CLIENT: {client['name']} (ID: {client['id']})
    CONTRACTOR: {contractor['name']} (ID: {contractor['id']})
    
    TASK DETAILS:
    Title: {task['title']}
    ID: {task['id']}
    Description: {task['description']}
    
    TERMS:
    1. The Contractor agrees to complete the Task as described above.
    2. The Client agrees to pay ${task['budget']} upon successful completion.
    3. The deadline for completion is {deadline.strftime('%Y-%m-%d')}.
    4. Payment will be automatically released when deliverables are approved.
    5. If the deadline is not met, a penalty of 5% per day will be applied.
    
    APPROVAL CRITERIA:
    The task will be considered complete when:
    - All deliverables are submitted as specified in the task description
    - The Client approves the work, or 7 days have passed with no feedback
    
    DISPUTE RESOLUTION:
    Any disputes will be resolved through the platform's arbitration process.
    
    CONTRACT ID: SC-{task['id']}-{today.strftime('%Y%m%d')}
    """
    
    return contract
