const newsData = [
    { image: "/static/main/images/image.png", title: "International Yoga Day Celebrated by UDAAN Society", newspaper: "Amar Ujala", date: "June 2024", summary: "UDAAN Society organized a large-scale yoga program to promote physical and mental well-being among citizens, with participation from students, volunteers, and local officials." },
    { image: "/static/main/images/image1.png", title: "Missing Child Reunited with Family", newspaper: "Dainik Jagran", date: "January 2024", summary: "Through timely intervention and coordination with authorities, UDAAN Society helped trace and reunite a missing child safely with their family." },
    { image: "/static/main/images/image2.png", title: "Free Eye Checkup Camp for Senior Citizens", newspaper: "Hindustan", date: "December 2023", summary: "A free eye camp was organized for elderly citizens, providing consultations, medicines, and referrals for cataract surgery." },
    { image: "/static/main/images/image3.png", title: "Child Trafficking Racket Busted", newspaper: "Amar Ujala", date: "March 2024", summary: "UDAAN Society assisted police and childline teams in rescuing multiple children from trafficking and ensured their rehabilitation." },
    { image: "/static/main/images/image4.png", title: "Child Marriage Prevented in Rural Area", newspaper: "Dainik Jagran", date: "May 2024", summary: "An illegal child marriage was stopped due to alert action by UDAAN Society volunteers and local authorities." },
    { image: "/static/main/images/image5.png", title: "Awareness Drive Against Child Marriage", newspaper: "Amar Ujala", date: "May 2024", summary: "UDAAN Society conducted an awareness campaign educating families about the legal and social consequences of child marriage." },
    { image: "/static/main/images/image6.png", title: "Education Awareness Campaign Launched", newspaper: "Amar Ujala", date: "October 2023", summary: "The organization encouraged school enrollment among underprivileged children through door-to-door counseling." },
    { image: "/static/main/images/image7.png", title: "Women Skill Development Workshop", newspaper: "Dainik Jagran", date: "November 2023", summary: "Women were trained in tailoring and handicrafts to support self-employment and financial independence." },
    { image: "/static/main/images/image8.png", title: "Free Health Camp Benefits Hundreds", newspaper: "Hindustan", date: "December 2023", summary: "Doctors provided free checkups and medicines to families in need as part of a community health initiative." },
    { image: "/static/main/images/image9.png", title: "Winter Relief Drive for Homeless", newspaper: "Rashtriya Sahara", date: "January 2024", summary: "Blankets and warm clothes were distributed to protect homeless individuals during extreme cold conditions." },
    { image: "/static/main/images/image10.png", title: "Cleanliness Drive Conducted", newspaper: "Rajasthan Patrika", date: "February 2024", summary: "Volunteers cleaned public spaces and spread awareness about hygiene and environmental responsibility." },
    { image: "/static/main/images/image11.png", title: "Youth Leadership Summit Held", newspaper: "Local Daily", date: "March 2024", summary: "Students from various colleges participated in discussions on leadership, civic duties, and social service." },
    { image: "/static/main/images/image12.png", title: "Blood Donation Camp Organized", newspaper: "Amar Ujala", date: "June 2024", summary: "More than 200 units of blood were collected to support emergency medical needs in hospitals." },
    { image: "/static/main/images/image13.png", title: "Tree Plantation Drive on Environment Day", newspaper: "Dainik Jagran", date: "June 2024", summary: "UDAAN Society planted hundreds of saplings to promote environmental conservation." },
    { image: "/static/main/images/image14.png", title: "Computer Training Program for Rural Youth", newspaper: "Hindustan", date: "July 2024", summary: "Rural students received basic computer training to enhance digital literacy and job readiness." },
    { image: "/static/main/images/image15.png", title: "COVID Relief Work Continues", newspaper: "Amar Ujala", date: "April 2023", summary: "Essential ration kits and safety supplies were distributed to families affected by the pandemic." },
    { image: "/static/main/images/image16.png", title: "Legal Awareness Program for Women", newspaper: "Dainik Jagran", date: "March 2024", summary: "Women were informed about legal rights, domestic violence laws, and available support services." },
    { image: "/static/main/images/image17.png", title: "Monthly Ration Distribution Drive", newspaper: "Rashtriya Sahara", date: "April 2024", summary: "UDAAN Society provided food supplies to economically weaker families to ensure food security." },
    { image: "/static/main/images/image18.png", title: "Support Extended to Differently-Abled", newspaper: "Amar Ujala", date: "December 2023", summary: "Assistive devices were distributed to improve mobility and quality of life." },
    { image: "/static/main/images/image19.png", title: "Senior Citizen Welfare Program Launched", newspaper: "Hindustan", date: "October 2023", summary: "Elderly individuals received health checkups and emotional support through dedicated programs." },
    { image: "/static/main/images/image20.png", title: "Adult Literacy Classes Started", newspaper: "Dainik Jagran", date: "September 2023", summary: "Adults were enrolled in literacy programs to improve reading and writing skills." },
    { image: "/static/main/images/image21.png", title: "Anti-Drug Awareness Rally", newspaper: "Amar Ujala", date: "June 2024", summary: "Students participated in rallies and street plays highlighting the dangers of drug abuse." },
    { image: "/static/main/images/image22.png", title: "Sanitation Facilities Built in Villages", newspaper: "Hindustan", date: "August 2023", summary: "Toilets were constructed in rural homes to improve hygiene and dignity." },
    { image: "/static/main/images/image23.png", title: "Scholarships Awarded to Meritorious Students", newspaper: "Dainik Jagran", date: "April 2024", summary: "Financial assistance was provided to students from low-income families for higher education." },
    { image: "/static/main/images/image24.png", title: "Mental Health Awareness Session", newspaper: "Amar Ujala", date: "October 2023", summary: "Psychologists addressed stress, anxiety, and mental health stigma in the community." },
    { image: "/static/main/images/image25.png", title: "Road Safety Awareness Program", newspaper: "Rashtriya Sahara", date: "April 2024", summary: "Students were educated on traffic rules, helmet usage, and pedestrian safety." },
    { image: "/static/main/images/image26.png", title: "Children’s Day Celebrated at Orphanage", newspaper: "Dainik Jagran", date: "November 2023", summary: "UDAAN Society celebrated Children’s Day with games, gifts, and educational support." }
];

const grid = document.getElementById("news-grid");
const modal = document.getElementById("imageModal");
const modalImg = document.getElementById("modalImage");
const modalCaption = document.getElementById("modalCaption");
const closeBtn = document.getElementById("closeModal");

newsData.forEach(item => {
    const card = document.createElement("div");
    card.className = "news-card";

    card.innerHTML = `
        <img src="${item.image}" alt="${item.title}">
        <div class="news-content">
            <h4>${item.title}</h4>
            <p>${item.newspaper} | ${item.date}</p>
        </div>
    `;

    card.addEventListener("click", () => {
        modal.classList.add("active");
        modalImg.src = item.image;
        modalCaption.innerHTML = `
            <h3>${item.title}</h3>
            <p>${item.summary}</p>
        `;
    });

    grid.appendChild(card);
});

closeBtn.addEventListener("click", () => modal.classList.remove("active"));

modal.addEventListener("click", e => {
    if (e.target === modal) modal.classList.remove("active");
});
