from django.db.models import Q
from blood_request.models import BloodDonor, BloodRequest, Task

def get_donor_response(message):
    message = message.lower()
    # Simple logic to extract blood group
    blood_groups = ['a+', 'a-', 'b+', 'b-', 'ab+', 'ab-', 'o+', 'o-']
    found_bg = None
    for bg in blood_groups:
        if bg in message:
            found_bg = bg.upper()
            break
            
    if found_bg:
        donors = BloodDonor.objects.filter(blood_group=found_bg)
        if "city" in message:
             # Very basic city extraction (assuming city names are single words for now or user says "in CityName")
             # Ideally we would use more complex NLP
             pass
        
        count = donors.count()
        if count > 0:
            return f"We found {count} donor(s) with blood group {found_bg}. You can search for them in the 'Find Donors' section."
        else:
            return f"Sorry, we currently have no donors registered with blood group {found_bg}."
    
    return "To find donors, please specify the blood group (e.g., 'A+ donors')."

def get_task_summary(user):
    if not user.is_authenticated:
        return "Please log in to view your tasks."
    
    # Check if staff or manager
    if user.is_superuser or user.groups.filter(name='Managers').exists():
         pending_tasks = Task.objects.filter(status__in=['To Do', 'In Progress', 'Review']).count()
         high_prio = Task.objects.filter(priority__in=['High', 'Critical']).count()
         return f"Manager Summary: There are {pending_tasks} pending tasks across the team. {high_prio} are High/Critical priority."
    else:
        my_tasks = Task.objects.filter(assigned_to=user, status__in=['To Do', 'In Progress']).count()
        return f"Hello {user.username}, you have {my_tasks} pending tasks assigned to you."

def generate_response(message, user):
    msg = message.lower()
    
    if "donor" in msg or "blood" in msg:
        if "request" in msg:
             return "To request blood, please visit the 'Request Blood' page and fill out the form."
        return get_donor_response(msg)
        
    if "task" in msg or "work" in msg:
        return get_task_summary(user)
        
    if "80g" in msg or "tax" in msg:
        return "Yes, all donations to Udaan Society are 50% tax exempt under Section 80G of the Income Tax Act."
        
    if "mission" in msg or "about" in msg:
        return "Udaan Society is dedicated to empowering the underprivileged through education, healthcare, and women's empowerment initiatives."

    return "I'm Udaan Mitra. I can help you find donors, check tax info, or view tasks (if you are staff). How can I assist?"
