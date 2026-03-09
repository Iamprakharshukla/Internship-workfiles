import os
from datetime import date
from django.core.files import File
from django.utils import timezone
from blood_request.models import NewsClipping, Project, Campaign, Activity

# Clear existing to avoid duplicates if any
NewsClipping.objects.all().delete()
Project.objects.all().delete()
Campaign.objects.all().delete()
Activity.objects.all().delete()

# Populate News Clippings
nc_dir = 'media/news_clippings'
if os.path.exists(nc_dir):
    for i, filename in enumerate(os.listdir(nc_dir)):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            NewsClipping.objects.create(
                title=f"News Coverage {i+1}",
                newspaper="Local Daily",
                date_display="Recent",
                summary="UDAAN Society making an impact in the community as covered by the media.",
                image=f"news_clippings/{filename}"
            )
            print(f"Added News Clipping: {filename}")

# Populate Projects
proj_dir = 'media/projects'
if os.path.exists(proj_dir):
    for i, filename in enumerate(os.listdir(proj_dir)):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            Project.objects.create(
                title=f"Community Project {i+1}",
                slug=f"community-project-{i+1}",
                description="An initiative by UDAAN Society to empower sections of society.",
                content="<p>Full details about this project and its lasting impact on the community.</p>",
                image=f"projects/{filename}",
                date=timezone.now().date()
            )
            print(f"Added Project: {filename}")

# Populate Campaigns
camp_dir = 'media/campaigns'
if os.path.exists(camp_dir):
    for i, filename in enumerate(os.listdir(camp_dir)):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            Campaign.objects.create(
                title=f"Fundraising Campaign {i+1}",
                description="Help us reach our goal to support those in need.",
                goal_amount=50000,
                raised_amount=15000,
                image=f"campaigns/{filename}"
            )
            print(f"Added Campaign: {filename}")

# Populate Activities
act_dir = 'media/activities'
if os.path.exists(act_dir):
    for i, filename in enumerate(os.listdir(act_dir)):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            Activity.objects.create(
                title=f"Recent Activity {i+1}",
                description="UDAAN Society hosts various activities year-round ranging from environmental protection, health camps, and educational awareness programs. We strive to empower our community in every step we take.",
                image=f"activities/{filename}",
                date=timezone.now().date()
            )
            print(f"Added Activity: {filename}")

print("Database populated successfully.")
