"""Seed the database with sample data for development."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from app.extensions import db
from app.models import (
    User, Hackathon, HackathonRegistration, Team, TeamMember,
    Submission, JudgingCriteria, Score, Opportunity, OpportunityBookmark,
)


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Users
        organizer = User(username="organizer", email="organizer@hackforge.dev", role="organizer")
        organizer.set_password("password123")
        db.session.add(organizer)

        builder1 = User(
            username="ada_lovelace", email="ada@hackforge.dev", role="participant",
            bio="Passionate about AI and education tech from Lagos.",
            skills="Python, Machine Learning, TensorFlow",
            interests="AI, EdTech, Climate",
            experience_level="Intermediate",
            location="Lagos, Nigeria",
            github_url="https://github.com/ada-lovelace",
        )
        builder1.set_password("password123")
        db.session.add(builder1)

        builder2 = User(
            username="kwame_mensah", email="kwame@hackforge.dev", role="participant",
            bio="Full-stack developer from Accra. Love building for Africa.",
            skills="JavaScript, React, Node.js, Python",
            interests="Fintech, Open Source, Web3",
            experience_level="Advanced",
            location="Accra, Ghana",
            github_url="https://github.com/kwame-mensah",
            portfolio_url="https://kwame.dev",
        )
        builder2.set_password("password123")
        db.session.add(builder2)

        builder3 = User(
            username="fatima_hassan", email="fatima@hackforge.dev", role="participant",
            bio="UX designer and front-end developer from Nairobi.",
            skills="UI Design, Figma, HTML, CSS, JavaScript",
            interests="Design Systems, Accessibility, Mobile",
            experience_level="Intermediate",
            location="Nairobi, Kenya",
        )
        builder3.set_password("password123")
        db.session.add(builder3)

        judge = User(username="judge_alpha", email="judge@hackforge.dev", role="judge")
        judge.set_password("password123")
        db.session.add(judge)

        admin = User(username="admin", email="admin@hackforge.dev", role="admin")
        admin.set_password("password123")
        db.session.add(admin)

        db.session.flush()

        # Hackathons
        h1 = Hackathon(
            title="HackForge Africa 2026",
            description="The flagship HACKFORGE hackathon bringing together builders from across Africa. Build solutions for education, healthcare, agriculture, or fintech challenges facing the continent.",
            rules="Teams of 2-5. 48-hour build period. Open-source encouraged. All code must be committed during the event.",
            eligibility="Open to all students and young professionals in Africa. Ages 16-30.",
            prize_info="1st: $3,000 + Incubation. 2nd: $1,500. 3rd: $750. Best Design: $500.",
            max_team_size=5,
            location="Online (Africa)",
            status="active",
            start_date="2026-09-01",
            end_date="2026-09-03",
            created_by=organizer.id,
        )
        db.session.add(h1)

        h2 = Hackathon(
            title="Lagos Fintech Sprint",
            description="A weekend hackathon focused on financial technology solutions for the unbanked and underbanked populations in West Africa.",
            rules="Teams of 1-3. Must use at least one African payment API. 36-hour sprint.",
            eligibility="Open to developers, designers, and fintech enthusiasts in West Africa.",
            prize_info="$5,000 total prize pool. Top 2 teams get mentorship sessions with leading fintech founders.",
            max_team_size=3,
            location="Lagos, Nigeria (Hybrid)",
            status="active",
            start_date="2026-10-15",
            end_date="2026-10-17",
            created_by=organizer.id,
        )
        db.session.add(h2)

        h3 = Hackathon(
            title="Climate Tech Challenge 2026",
            description="Build technology solutions addressing climate change impacts in Africa. Focus on adaptation, mitigation, or awareness.",
            rules="Teams of 2-5. Must include a working prototype. Demo day presentations required.",
            eligibility="Open globally. Priority for African-based teams.",
            prize_info="$10,000 in prizes. Winners get featured at Africa Climate Summit.",
            max_team_size=5,
            location="Online (Global)",
            status="active",
            start_date="2026-11-10",
            end_date="2026-11-12",
            created_by=organizer.id,
        )
        db.session.add(h3)

        h4 = Hackathon(
            title="UniCode Campus Hack",
            description="University-focused hackathon. Build tools, apps, or platforms that improve student life on campus.",
            rules="Teams of 2-4. Must be current university students. 24-hour build.",
            eligibility="Currently enrolled university students in Nigeria.",
            prize_info="Laptops, coding bootcamp scholarships, and internship opportunities.",
            max_team_size=4,
            location="University of Lagos, Nigeria",
            status="completed",
            start_date="2026-06-01",
            end_date="2026-06-02",
            created_by=organizer.id,
        )
        db.session.add(h4)

        db.session.flush()

        # Hackathon registrations
        for user in [builder1, builder2, builder3]:
            for hack in [h1, h2, h3]:
                reg = HackathonRegistration(user_id=user.id, hackathon_id=hack.id)
                db.session.add(reg)

        reg4 = HackathonRegistration(user_id=builder1.id, hackathon_id=h4.id)
        db.session.add(reg4)
        reg5 = HackathonRegistration(user_id=builder2.id, hackathon_id=h4.id)
        db.session.add(reg5)

        db.session.flush()

        # Teams
        t1 = Team(
            name="Solar Scholars",
            description="Building a solar energy marketplace connecting rural communities with affordable solar solutions.",
            hackathon_id=h1.id,
            created_by=builder1.id,
        )
        db.session.add(t1)
        db.session.flush()

        tm1 = TeamMember(team_id=t1.id, user_id=builder1.id, role="leader")
        tm2 = TeamMember(team_id=t1.id, user_id=builder2.id, role="member")
        tm3 = TeamMember(team_id=t1.id, user_id=builder3.id, role="member")
        db.session.add_all([tm1, tm2, tm3])

        t2 = Team(
            name="CropGuard AI",
            description="AI-powered crop disease detection using mobile phone cameras.",
            hackathon_id=h2.id,
            created_by=builder2.id,
        )
        db.session.add(t2)
        db.session.flush()

        tm4 = TeamMember(team_id=t2.id, user_id=builder2.id, role="leader")
        db.session.add(tm4)

        db.session.flush()

        # Judging criteria for h1
        c1 = JudgingCriteria(hackathon_id=h1.id, name="Innovation", description="Originality and creativity of the solution", max_score=10)
        c2 = JudgingCriteria(hackathon_id=h1.id, name="Impact", description="Potential real-world impact in Africa", max_score=10)
        c3 = JudgingCriteria(hackathon_id=h1.id, name="Technical Execution", description="Code quality, architecture, and functionality", max_score=10)
        c4 = JudgingCriteria(hackathon_id=h1.id, name="Design", description="UI/UX quality and user experience", max_score=10)
        db.session.add_all([c1, c2, c3, c4])

        # Judging criteria for h4
        c5 = JudgingCriteria(hackathon_id=h4.id, name="Usefulness", description="How useful is the tool for students", max_score=10)
        c6 = JudgingCriteria(hackathon_id=h4.id, name="Execution", description="Working state and quality", max_score=10)
        db.session.add_all([c5, c6])

        db.session.flush()

        # Submissions for h1
        s1 = Submission(
            title="SolarConnect",
            description="A marketplace platform connecting rural African communities with affordable solar energy providers. Users can browse solar products, compare prices, and arrange installations through verified local technicians.",
            problem="Over 600 million Africans lack access to reliable electricity. Solar solutions exist but are hard to find and afford in rural areas.",
            solution="SolarConnect creates a digital marketplace that aggregates solar providers, enables price comparison, and connects buyers with certified local installers. Includes mobile money payment support.",
            technologies="Python, Flask, React, PostgreSQL, Mobile Money API",
            github_url="https://github.com/solar-scholars/solarconnect",
            demo_url="https://solarconnect.demo.dev",
            hackathon_id=h1.id,
            team_id=t1.id,
            author_id=builder1.id,
        )
        db.session.add(s1)

        s2 = Submission(
            title="FarmWatch",
            description="Real-time agricultural monitoring dashboard for smallholder farmers. Uses satellite data and weather APIs to provide actionable insights.",
            problem="Smallholder farmers in Africa lose up to 40% of crops due to lack of timely information about weather, soil conditions, and pest threats.",
            solution="FarmWatch aggregates satellite imagery, weather data, and soil information into a simple mobile-friendly dashboard with local language support and SMS alerts.",
            technologies="Python, FastAPI, React, Satellite API, Twilio",
            hackathon_id=h1.id,
            team_id=None,
            author_id=builder3.id,
        )
        db.session.add(s2)

        db.session.flush()

        # Scores for submissions
        for judge_user in [judge]:
            for sub, scores in [(s1, [(c1, 8), (c2, 9), (c3, 7), (c4, 8)]), (s2, [(c1, 9), (c2, 8), (c3, 6), (c4, 7)])]:
                for crit, score_val in scores:
                    sc = Score(
                        submission_id=sub.id,
                        criteria_id=crit.id,
                        judge_id=judge_user.id,
                        score=score_val,
                        feedback="Good work" if score_val >= 7 else "Needs improvement",
                    )
                    db.session.add(sc)

        # Submissions for h4 (completed hackathon)
        s3 = Submission(
            title="CampusPlate",
            description="A food-sharing platform for university campuses. Students can share excess meals, reducing food waste and helping those in need.",
            problem="University cafeterias waste significant amounts of food daily while many students struggle to afford meals.",
            solution="CampusPlate allows students to list surplus food, which others can claim for free. Includes rating system, pickup scheduling, and nutrition tracking.",
            technologies="Flutter, Firebase, Python",
            hackathon_id=h4.id,
            team_id=None,
            author_id=builder1.id,
        )
        db.session.add(s3)

        s4 = Submission(
            title="StudyBuddy",
            description="AI-powered study scheduling app that creates personalized study plans based on exam dates, course difficulty, and individual learning patterns.",
            problem="Students struggle to manage study time across multiple courses, leading to poor exam performance and stress.",
            solution="StudyBuddy analyzes course syllabi, creates optimized study schedules, sends reminders, and adapts plans based on self-reported comprehension levels.",
            technologies="Python, Django, React Native, OpenAI API",
            hackathon_id=h4.id,
            team_id=None,
            author_id=builder2.id,
        )
        db.session.add(s4)

        db.session.flush()

        # Scores for h4
        for sub, scores in [(s3, [(c5, 8), (c6, 7)]), (s4, [(c5, 9), (c6, 8)])]:
            for crit, score_val in scores:
                sc = Score(
                    submission_id=sub.id,
                    criteria_id=crit.id,
                    judge_id=judge.id,
                    score=score_val,
                )
                db.session.add(sc)

        # Opportunities
        opps = [
            Opportunity(
                title="Google Africa Developer Scholarship",
                description="The Google Africa Developer Scholarship provides free training and certification in mobile and web development for African developers. Participants get access to Udacity courses, mentorship, and networking opportunities.",
                category="Scholarships",
                organization="Google / Andela",
                location="Africa (All countries)",
                url="https://buildwithgrove.com",
                deadline="2026-12-01",
                eligibility="African nationals or residents. Must be 18-35 years old. Basic programming knowledge recommended.",
            ),
            Opportunity(
                title="Africa Code Week 2026",
                description="Join the largest coding event in Africa. Free workshops, hackathons, and coding bootcamps across 54 countries. Learn to code and build your first project.",
                category="Events",
                organization="SAP / UNESCO",
                location="Africa (54 countries)",
                url="https://africacodeweek.net",
                deadline="2026-10-15",
                eligibility="Open to everyone. Special tracks for beginners, women, and youth.",
            ),
            Opportunity(
                title="Flutterwave Internship Program",
                description="Paid internship at Flutterwave, Africa's leading payment technology company. Work on real products serving millions of users across Africa.",
                category="Internships",
                organization="Flutterwave",
                location="Lagos, Nigeria / Remote",
                url="https://flutterwave.com/careers",
                deadline="2026-09-30",
                eligibility="Students and recent graduates. Proficiency in Python, JavaScript, or Go preferred.",
            ),
            Opportunity(
                title="Build Africa Fellowship",
                description="A 6-month fellowship for young African tech leaders. Includes stipend, mentorship from top tech executives, and project funding up to $5,000.",
                category="Fellowships",
                organization="Build Africa Foundation",
                location="Pan-Africa",
                url="https://buildafrica.org/fellowship",
                deadline="2026-11-30",
                eligibility="African nationals aged 21-30. Must have a tech project idea or early-stage startup.",
            ),
            Opportunity(
                title="Coursera Africa Free Courses",
                description="Access hundreds of free tech courses on Coursera sponsored by Meta. Includes data science, web development, and AI/ML tracks with certificates.",
                category="Free Courses",
                organization="Meta / Coursera",
                location="Online (Global)",
                url="https://coursera.org/africa",
                deadline="2026-12-31",
                eligibility="Open to all Africans. Free certificates available for course completions.",
            ),
            Opportunity(
                title="Tony Elumelu Foundation Entrepreneurship Programme",
                description="$5,000 seed capital, mentorship, and training for young African entrepreneurs. Build your startup with support from Africa's leading entrepreneurs.",
                category="Grants",
                organization="Tony Elumelu Foundation",
                location="Africa (All countries)",
                url="https://tonyelumelufoundation.org",
                deadline="2026-03-01",
                eligibility="African entrepreneurs aged 18-40 with early-stage business ideas or ventures.",
            ),
            Opportunity(
                title="HackMIT 2026",
                description="One of the world's largest student hackathons. Build innovative projects in 24 hours with 1,000+ hackers from around the world.",
                category="Hackathons",
                organization="MIT",
                location="Cambridge, MA / Online",
                url="https://hackmit.org",
                deadline="2026-09-20",
                eligibility="Currently enrolled university students. Travel reimbursement available for selected international participants.",
            ),
            Opportunity(
                title="Peace Corps Digital Service Volunteer",
                description="Use your tech skills for good. Volunteer to support digital transformation projects in developing communities across Africa.",
                category="Volunteering",
                organization="Peace Corps",
                location="Various African Countries",
                url="https://peacecorps.gov/digital",
                deadline="2026-08-01",
                eligibility="US citizens aged 18-50. Tech professionals and students welcome.",
            ),
            Opportunity(
                title="Ghana Tech Summit",
                description="Annual technology conference bringing together Africa's top tech innovators, investors, and policy makers. Network, learn, and showcase your work.",
                category="Events",
                organization="Ghana Tech Alliance",
                location="Accra, Ghana",
                url="https://ghanaTechsummit.com",
                deadline="2026-11-20",
                eligibility="Open to all tech enthusiasts. Student discounts available. Virtual attendance option.",
            ),
        ]
        db.session.add_all(opps)
        db.session.commit()
        print("Database seeded successfully!")
        print(f"  Users: {User.query.count()}")
        print(f"  Hackathons: {Hackathon.query.count()}")
        print(f"  Teams: {Team.query.count()}")
        print(f"  Submissions: {Submission.query.count()}")
        print(f"  Opportunities: {Opportunity.query.count()}")
        print(f"  Judging Criteria: {JudgingCriteria.query.count()}")
        print(f"  Scores: {Score.query.count()}")


if __name__ == "__main__":
    seed()
