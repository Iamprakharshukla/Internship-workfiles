import os
from django.utils import timezone
from blood_request.models import Blog, Testimonial

Blog.objects.all().delete()
Testimonial.objects.all().delete()

# Populate Blogs
blog_dir = 'media/blogs'
unique_blogs = set()
if os.path.exists(blog_dir):
    for i, filename in enumerate(os.listdir(blog_dir)):
        # avoiding those duplicated names that end in random strings like _Bkz9AqQ.webp
        if filename.endswith(('.png', '.jpg', '.jpeg', '.webp')) and '_' not in filename[-12:-4]:
            if filename not in unique_blogs:
                unique_blogs.add(filename)
                Blog.objects.create(
                    title=f"Insightful Blog Post {len(unique_blogs)}",
                    content="<p>This is a detailed blog post discussing the impact of our latest initiatives.</p>",
                    description="A brief summary of what this blog discusses.",
                    image=f"blogs/{filename}"
                )
                print(f"Added Blog: {filename}")

# Populate Testimonials
test_dir = 'media/testimonials'
if os.path.exists(test_dir):
    for i, filename in enumerate(os.listdir(test_dir)):
        if filename.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            Testimonial.objects.create(
                author=f"Community Member {i+1}",
                role="Volunteer",
                text="UDAAN Society has completely changed my life for the better.",
                detailed_text="When I first joined, I was unsure how I could help, but UDAAN provided the structure and support necessary for me to grow.",
                image=f"testimonials/{filename}"
            )
            print(f"Added Testimonial: {filename}")

# In case there are no testimonial images, create some dummy ones without images
if Testimonial.objects.count() == 0:
    for i in range(3):
        Testimonial.objects.create(
            author=f"Partner {i+1}",
            role="Sponsor",
            text="An incredible organization doing amazing work.",
            detailed_text="They consistently deliver on their promises and help the community immensely."
        )

print("Blogs and Testimonials populated successfully.")
