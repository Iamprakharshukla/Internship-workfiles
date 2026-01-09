import json
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import BloodDonor, BloodRequest
from .schemas import DonorSchema
from pydantic import ValidationError

@ensure_csrf_cookie
def index(request):
    """
    Renders the main page. CSRF cookie is ensured for AJAX requests.
    """
    return render(request, 'blood_request/index.html')

def register_donor(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # 1. Validate with Pydantic
            donor_data = DonorSchema(**data)
            
            # 2. Check logic unique phone (Pydantic doesn't check DB)
            if BloodDonor.objects.filter(phone=donor_data.phone).exists():
                return JsonResponse({'success': False, 'error': 'Phone number already registered.'}, status=400)

            # 3. Create Model Instance
            donor = BloodDonor.objects.create(
                name=donor_data.name,
                blood_group=donor_data.blood_group,
                phone=donor_data.phone,
                email=donor_data.email,
                city=donor_data.city,
                state=donor_data.state,
                pin_code=donor_data.pin_code,
                consent_given=donor_data.consent_given
            )
            return JsonResponse({'success': True, 'message': 'Registration successful!'})

        except ValidationError as e:
            return JsonResponse({'success': False, 'error': e.errors()}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    
    return JsonResponse({'success': False, 'error': 'Invalid method'}, status=405)

def search_donors(request):
    blood_group = request.GET.get('blood_group')
    city = request.GET.get('city')

    donors = BloodDonor.objects.all()

    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    
    if city:
        donors = donors.filter(city__icontains=city)
    
    results = []
    for donor in donors:
        results.append({
            'name': donor.name,
            'blood_group': donor.blood_group,
            'phone': donor.phone, # In a real app, might want to mask this or show only on request
            'email': donor.email,
            'city': donor.city,
            'state': donor.state
        })

    return JsonResponse({'results': results})

def blood_request_create(request):
    if request.method == "POST":
        try:
            # Handle standard form data
            data = json.loads(request.body)
            
            # Simple validation for required fields
            required_fields = ['city', 'pin_code', 'blood_group', 'units', 'address_line_2', 'contact_person', 'contact_phone']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({"success": False, "error": f"{field.replace('_', ' ').title()} is required."}, status=400)

            blood_request = BloodRequest.objects.create(
                city=data.get('city'),
                pin_code=data.get('pin_code'),
                blood_group=data.get('blood_group'),
                units=int(data.get('units')),
                address_line_1=data.get('address_line_1', ''),
                address_line_2=data.get('address_line_2'),
                contact_person=data.get('contact_person'),
                contact_phone=data.get('contact_phone'),
                # File handling omitted for JSON payload simplicity in this step
            )
            return JsonResponse({"success": True, "message": "Blood request submitted successfully!"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)
    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)
    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

from .models import Campaign, Report

def home_view(request):
    """
    Renders the homepage with dynamic content.
    """
    campaigns = Campaign.objects.all().order_by('-created_at')[:3]
    # Assuming 'Reports' map to 'Projects' section or similar
    reports = Report.objects.all().order_by('-published_date')[:3]
    
    context = {
        'campaigns': campaigns,
        'reports': reports
    }
    return render(request, 'home.html', context)
