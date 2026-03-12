import os
import tempfile
from datetime import datetime
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes, CallbackQueryHandler
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import requests
from bs4 import BeautifulSoup

# ==================== CONFIGURATION ====================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PORTFOLIO_URL = "https://haile-portfolio-theta.vercel.app/"
YOUR_ID = 6673503943  # Your Telegram ID

# Check tokens
if not TELEGRAM_TOKEN or not GEMINI_API_KEY:
    print("ERROR: Missing tokens!")
    exit(1)

# Initialize Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# ==================== PORTFOLIO DATA ====================
portfolio_data = {
    'name': 'Haile',
    'title': 'IT Instructor & Developer',
    'location': 'Addis Ababa',
    'education': 'CS Graduate',
    'email': 'haileyesusshibru19@gmail.com',
    'phone': '+251 975 101 559',
    'experience': [
        {
            'title': 'IT Instructor',
            'company': 'Higher Education Institution',
            'date': 'Present',
            'description': [
                'Deliver networking and programming courses',
                'Guide practical lab sessions for technical skill development',
                'Prepare comprehensive training materials and assessments'
            ]
        },
        {
            'title': 'IT Intern',
            'company': 'Koye Feche Sub-city Science & Technology Bureau',
            'date': '6 Months',
            'description': [
                'Configured routers and switches for local network infrastructure',
                'Implemented firewall setups to ensure network security',
                'Provided server and database support'
            ]
        },
        {
            'title': 'GPS Technician',
            'company': 'Technical Services',
            'date': '6+ Months',
            'description': [
                'Installed vehicle tracking systems in diverse fleet environments',
                'Diagnosed connectivity and hardware issues in the field'
            ]
        }
    ],
    'skills': {
        'networking': ['Cisco IOS', 'Routing', 'Switching', 'Firewalls', 'TCP/IP'],
        'programming': ['Python', 'Java', 'C++', 'JavaScript', 'TypeScript'],
        'mobile': ['Flutter', 'Firebase', 'Dart', 'Android', 'iOS'],
        'devops': ['Docker', 'Linux', 'CI/CD', 'Agile'],
        'it_support': ['Hardware', 'OS Support', 'Diagnostics', 'Maintenance']
    },
    'languages': {
        'Amharic': 'Native',
        'English': 'Proficient'
    },
    'projects': [
        {
            'name': 'Network Configuration Lab Setup',
            'type': 'Personal Project',
            'description': [
                'Designed network lab environment with VLANs and secure routing',
                'Implemented using Cisco equipment and best practices'
            ]
        },
        {
            'name': 'Flutter-Based Mobile Application',
            'type': 'Personal Project',
            'description': [
                'Developed cross-platform mobile app with Firebase integration',
                'Implemented real-time data synchronization and user authentication'
            ]
        },
        {
            'name': 'GPS Installation & Tracking Workflow',
            'type': 'Personal Project',
            'description': [
                'Streamlined GPS installation process for vehicle tracking',
                'Improved data accuracy by 40% through systematic workflow'
            ]
        }
    ]
}

# ==================== SETUP JINJA2 TEMPLATE ====================
# Save the HTML template to a file
template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ data.name }} - CV</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            line-height: 1.5;
            color: #333;
            background: white;
            padding: 40px;
            max-width: 1200px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 20px;
        }
        
        .name {
            font-size: 36px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        
        .title {
            font-size: 18px;
            color: #7f8c8d;
            font-weight: 400;
        }
        
        .contact-info {
            display: flex;
            justify-content: center;
            gap: 30px;
            margin-top: 15px;
            font-size: 14px;
            color: #555;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 2fr;
            gap: 40px;
            margin-top: 20px;
        }
        
        .left-column {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 8px;
        }
        
        .section {
            margin-bottom: 25px;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: 600;
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 8px;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .personal-detail {
            display: flex;
            margin-bottom: 10px;
            font-size: 14px;
        }
        
        .detail-label {
            font-weight: 600;
            width: 80px;
            color: #2c3e50;
        }
        
        .detail-value {
            color: #555;
        }
        
        .skill-category {
            margin-bottom: 15px;
        }
        
        .skill-category h4 {
            font-size: 15px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 8px;
        }
        
        .skill-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .skill-tag {
            background: #e1f5fe;
            color: #0277bd;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: 500;
        }
        
        .language-item {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            font-size: 14px;
        }
        
        .language-name {
            font-weight: 500;
            color: #2c3e50;
        }
        
        .language-level {
            color: #0277bd;
            font-weight: 500;
        }
        
        .right-column {
            padding: 0 10px;
        }
        
        .experience-item {
            margin-bottom: 25px;
        }
        
        .experience-header {
            display: flex;
            justify-content: space-between;
            align-items: baseline;
            margin-bottom: 8px;
        }
        
        .experience-title {
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
        }
        
        .experience-company {
            font-weight: 500;
            color: #3498db;
        }
        
        .experience-date {
            font-size: 13px;
            color: #7f8c8d;
            font-style: italic;
        }
        
        .experience-description {
            font-size: 14px;
            color: #555;
            margin-left: 20px;
            list-style-type: none;
        }
        
        .experience-description li {
            margin-bottom: 5px;
            position: relative;
            padding-left: 15px;
        }
        
        .experience-description li:before {
            content: "•";
            color: #3498db;
            font-weight: bold;
            position: absolute;
            left: 0;
        }
        
        .project-item {
            margin-bottom: 20px;
        }
        
        .project-name {
            font-size: 15px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        
        .project-type {
            font-size: 13px;
            color: #7f8c8d;
            font-style: italic;
            margin-bottom: 8px;
        }
        
        .project-description {
            font-size: 13px;
            color: #555;
            margin-left: 20px;
        }
        
        .project-description li {
            margin-bottom: 3px;
        }
        
        .job-match-section {
            margin-top: 30px;
            padding: 20px;
            background: #e8f4fd;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        
        .job-match-title {
            font-size: 16px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .requirements-list {
            margin-top: 10px;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .requirement-badge {
            background: white;
            color: #0277bd;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            border: 1px solid #3498db;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="name">{{ data.name }}</div>
        <div class="title">{{ data.title }}</div>
        <div class="contact-info">
            <span>📧 {{ data.email }}</span>
            <span>📱 {{ data.phone }}</span>
            <span>📍 {{ data.location }}</span>
        </div>
    </div>
    
    <div class="main-content">
        <div class="left-column">
            <div class="section">
                <div class="section-title">Personal Details</div>
                <div class="personal-detail">
                    <span class="detail-label">Name:</span>
                    <span class="detail-value">{{ data.name }}</span>
                </div>
                <div class="personal-detail">
                    <span class="detail-label">Title:</span>
                    <span class="detail-value">{{ data.title }}</span>
                </div>
                <div class="personal-detail">
                    <span class="detail-label">Education:</span>
                    <span class="detail-value">{{ data.education }}</span>
                </div>
            </div>
            
            <div class="section">
                <div class="section-title">Skills</div>
                {% for category, skills in data.skills.items() %}
                <div class="skill-category">
                    <h4>{{ category|title }}</h4>
                    <div class="skill-tags">
                        {% for skill in skills[:5] %}
                        <span class="skill-tag">{{ skill }}</span>
                        {% endfor %}
                    </div>
                </div>
                {% endfor %}
            </div>
            
            <div class="section">
                <div class="section-title">Languages</div>
                {% for lang, level in data.languages.items() %}
                <div class="language-item">
                    <span class="language-name">{{ lang }}</span>
                    <span class="language-level">{{ level }}</span>
                </div>
                {% endfor %}
            </div>
        </div>
        
        <div class="right-column">
            <div class="section">
                <div class="section-title">Professional Summary</div>
                <p style="font-size: 14px; color: #555; line-height: 1.6;">
                    {{ data.summary }}
                </p>
            </div>
            
            <div class="section">
                <div class="section-title">Experience</div>
                {% for exp in data.experience %}
                <div class="experience-item">
                    <div class="experience-header">
                        <span class="experience-title">{{ exp.title }}</span>
                        <span class="experience-date">{{ exp.date }}</span>
                    </div>
                    <div class="experience-company">{{ exp.company }}</div>
                    <ul class="experience-description">
                        {% for item in exp.description %}
                        <li>{{ item }}</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endfor %}
            </div>
            
            <div class="section">
                <div class="section-title">Projects</div>
                {% for project in data.projects %}
                <div class="project-item">
                    <div class="project-name">{{ project.name }}</div>
                    <div class="project-type">{{ project.type }}</div>
                    <ul class="project-description">
                        {% for item in project.description %}
                        <li>{{ item }}</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endfor %}
            </div>
        </div>
    </div>
    
    <div class="job-match-section">
        <div class="job-match-title">📋 Application for {{ data.job_company }}</div>
        <div class="job-match-text">
            This CV is tailored for the <strong>{{ data.job_title }}</strong> position. 
            Key requirements addressed:
        </div>
        <div class="requirements-list">
            {% for req in data.requirements %}
            <span class="requirement-badge">{{ req }}</span>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

# Save template to file
with open('cv_template.html', 'w') as f:
    f.write(template_content)

# Setup Jinja2 environment
env = Environment(loader=FileSystemLoader('.'))

def create_cv_pdf(job_title, company, requirements_text):
    """Create a professional CV PDF using HTML/CSS template"""
    
    # Parse requirements into list
    requirements_list = [req.strip() for req in requirements_text.split(',')]
    
    # Create summary using job title
    summary = f"A dedicated and passionate {job_title} with experience in {portfolio_data['experience'][0]['title']}. Skilled in {', '.join(portfolio_data['skills']['programming'][:3])} and dedicated to delivering high-quality results. Committed to continuous learning and teamwork to achieve organizational goals."
    
    # Prepare data for template
    cv_data = {
        'name': portfolio_data['name'],
        'title': portfolio_data['title'],
        'email': portfolio_data['email'],
        'phone': portfolio_data['phone'],
        'location': portfolio_data['location'],
        'education': portfolio_data['education'],
        'summary': summary,
        'skills': portfolio_data['skills'],
        'languages': portfolio_data['languages'],
        'experience': portfolio_data['experience'],
        'projects': portfolio_data['projects'],
        'job_title': job_title,
        'job_company': company,
        'requirements': requirements_list
    }
    
    try:
        # Load and render template
        template = env.get_template('cv_template.html')
        html_content = template.render(data=cv_data)
        
        # Convert HTML to PDF
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        HTML(string=html_content).write_pdf(temp_file.name)
        
        return temp_file.name
    except Exception as e:
        print(f"PDF Generation Error: {e}")
        raise e

# ==================== AUTHORIZATION ====================
def is_authorized(user_id):
    return user_id == YOUR_ID

# ==================== COMMAND HANDLERS ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        await update.message.reply_text("🔒 Private bot")
        return
    
    keyboard = [
        [InlineKeyboardButton("📄 Create CV", callback_data="cv")],
        [InlineKeyboardButton("✉️ Cover Letter", callback_data="cover")],
        [InlineKeyboardButton("📁 Portfolio", callback_data="portfolio")],
        [InlineKeyboardButton("ℹ️ About Me", callback_data="about")],
        [InlineKeyboardButton("📞 Contact", callback_data="contact")],
        [InlineKeyboardButton("💼 Job Status", callback_data="job")],
        [InlineKeyboardButton("🚀 Projects", callback_data="projects")],
        [InlineKeyboardButton("🔧 Skills", callback_data="skills")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    
    await update.message.reply_text(
        f"👋 **Hello {update.effective_user.first_name}!**\n\n"
        f"I'm **Haile Career Assistant**. What would you like help with?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    
    help_text = """
📋 **ALL COMMANDS**

**Main Commands:**
/start - Main menu with buttons
/help - Show this help

**Information Commands:**
/about - About Haile
/portfolio - Portfolio link
/contact - Contact info
/job - Job search status
/projects - Featured projects
/skills - Technical skills

**Document Commands:**
/createcv - Create a CV
/createcover - Create cover letter

**AI Chat:**
Just send any message to chat with AI!
    """
    await update.message.reply_text(help_text)

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    
    text = f"""
👨‍💻 **About Haile**

**Role:** {portfolio_data['title']}
**Location:** {portfolio_data['location']}
**Education:** {portfolio_data['education']}
**Experience:** IT Instructor, IT Intern, GPS Technician

I'm passionate about teaching IT and building reliable systems.
    """
    await update.message.reply_text(text)

async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    
    keyboard = [[InlineKeyboardButton("🌐 Visit Portfolio", url=PORTFOLIO_URL)]]
    await update.message.reply_text(
        "Check out my portfolio website:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    
    text = f"""
📬 **Contact Information**

📧 **Email:** {portfolio_data['email']}
💼 **GitHub:** github.com/haile199105
📱 **Telegram:** @haile199105
🌐 **Portfolio:** haile-portfolio-theta.vercel.app

Feel free to reach out!
    """
    await update.message.reply_text(text)

async def job_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    
    text = """
💼 **Job Search Status**

🔍 **Looking for:**
• IT Instructor / Trainer
• Python Developer
• Network Administrator
• Junior Developer

📊 **Status:** Actively looking
⭐ **Open to:** Remote, Hybrid, On-site
📍 **Location:** Addis Ababa / Remote

**Key Skills:** Python, Networking, Flutter, Docker
    """
    await update.message.reply_text(text)

async def projects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    
    text = "🚀 **Featured Projects:**\n\n"
    for i, project in enumerate(portfolio_data['projects'], 1):
        text += f"{i}. {project['name']}\n"
    await update.message.reply_text(text)

async def skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    
    text = "🔧 **Technical Skills:**\n\n"
    for category, skills in portfolio_data['skills'].items():
        text += f"**{category.title()}:** {', '.join(skills[:3])}\n"
    await update.message.reply_text(text)

async def createcv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    
    await update.message.reply_text(
        "📄 **Let's create your CV!**\n\n"
        "Please answer these questions:\n"
        "1. What job title are you applying for?\n"
        "2. What company?\n"
        "3. What are the key requirements?"
    )
    context.user_data['cv_step'] = 'job_title'

async def createcover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    
    await update.message.reply_text(
        "✉️ **Let's create your cover letter!**\n\n"
        "Please answer these questions:\n"
        "1. What job title are you applying for?\n"
        "2. What company?\n"
        "3. What are the key requirements?"
    )
    context.user_data['cover_step'] = 'job_title'

async def handle_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    # Handle CV creation
    if 'cv_step' in context.user_data:
        step = context.user_data['cv_step']
        
        if step == 'job_title':
            context.user_data['cv_job'] = text
            context.user_data['cv_step'] = 'company'
            await update.message.reply_text("🏢 **Company name?**")
        
        elif step == 'company':
            context.user_data['cv_company'] = text
            context.user_data['cv_step'] = 'requirements'
            await update.message.reply_text("📋 **Key requirements?**")
        
        elif step == 'requirements':
            await update.message.reply_text("⏳ **Generating your professional CV PDF...**")
            try:
                pdf_path = create_cv_pdf(
                    context.user_data['cv_job'],
                    context.user_data['cv_company'],
                    text
                )
                with open(pdf_path, 'rb') as f:
                    await update.message.reply_document(
                        document=f,
                        filename=f"CV_{context.user_data['cv_job'].replace(' ', '_')}.pdf",
                        caption="📄 Your professionally designed CV"
                    )
                os.unlink(pdf_path)
            except Exception as e:
                await update.message.reply_text(f"❌ Error: {e}")
            
            # Clean up
            del context.user_data['cv_step']
            if 'cv_job' in context.user_data:
                del context.user_data['cv_job']
            if 'cv_company' in context.user_data:
                del context.user_data['cv_company']
                
            await update.message.reply_text("✅ CV created! Use /start for main menu.")
        return
    
    # Handle cover letter creation
    if 'cover_step' in context.user_data:
        step = context.user_data['cover_step']
        
        if step == 'job_title':
            context.user_data['cover_job'] = text
            context.user_data['cover_step'] = 'company'
            await update.message.reply_text("🏢 **Company name?**")
        
        elif step == 'company':
            context.user_data['cover_company'] = text
            context.user_data['cover_step'] = 'requirements'
            await update.message.reply_text("📋 **Key requirements?**")
        
        elif step == 'requirements':
            await update.message.reply_text("✍️ **Generating cover letter...**")
            
            # Use AI to generate cover letter
            prompt = f"Write a professional cover letter for {context.user_data['cover_job']} position at {context.user_data['cover_company']}. Key requirements: {text}. Use Haile's background: IT Instructor with skills in Python, networking, and Flutter."
            
            response = model.generate_content(prompt)
            await update.message.reply_text(response.text[:4000])
            
            # Clean up
            del context.user_data['cover_step']
            if 'cover_job' in context.user_data:
                del context.user_data['cover_job']
            if 'cover_company' in context.user_data:
                del context.user_data['cover_company']
                
            await update.message.reply_text("✅ Cover letter created! Use /start for main menu.")
        return

# ==================== AI MESSAGE HANDLER ====================
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update.effective_user.id):
        return
    
    # Check if in conversation mode
    if 'cv_step' in context.user_data or 'cover_step' in context.user_data:
        await handle_conversation(update, context)
        return
    
    user_message = update.message.text
    user_name = update.effective_user.first_name
    
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        prompt = f"""
        You are Haile, an IT instructor and developer from Ethiopia.
        
        User's name: {user_name}
        User's message: {user_message}
        
        About Haile:
        - Skills: Python, Networking, Flutter, Docker
        - Experience: IT Instructor, IT Intern, GPS Technician
        - Location: Addis Ababa
        
        Respond helpfully as Haile would. If asked about Haile's background, use the info above.
        Keep answers clear and educational.
        """
        
        response = model.generate_content(prompt)
        await update.message.reply_text(response.text[:4000])

    except Exception as e:
        print(f"AI Error: {e}")
        await update.message.reply_text("❌ Sorry, I encountered an error. Please try again.")

# ==================== BUTTON HANDLER ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # Send a typing indicator
    await context.bot.send_chat_action(chat_id=query.message.chat_id, action="typing")
    
    if query.data == "help":
        help_text = """
📋 **ALL COMMANDS**

**Main Commands:**
/start - Main menu with buttons
/help - Show this help

**Information Commands:**
/about - About Haile
/portfolio - Portfolio link
/contact - Contact info
/job - Job search status
/projects - Featured projects
/skills - Technical skills

**Document Commands:**
/createcv - Create a CV
/createcover - Create cover letter

**AI Chat:**
Just send any message to chat with AI!
        """
        await query.message.reply_text(help_text)
        
    elif query.data == "about":
        text = f"""
👨‍💻 **About Haile**

**Role:** {portfolio_data['title']}
**Location:** {portfolio_data['location']}
**Education:** {portfolio_data['education']}
**Experience:** IT Instructor, IT Intern, GPS Technician

I'm passionate about teaching IT and building reliable systems.
        """
        await query.message.reply_text(text)
        
    elif query.data == "contact":
        text = f"""
📬 **Contact Information**

📧 **Email:** {portfolio_data['email']}
💼 **GitHub:** github.com/haile199105
📱 **Telegram:** @haile199105
🌐 **Portfolio:** haile-portfolio-theta.vercel.app

Feel free to reach out!
        """
        await query.message.reply_text(text)
        
    elif query.data == "job":
        text = """
💼 **Job Search Status**

🔍 **Looking for:**
• IT Instructor / Trainer
• Python Developer
• Network Administrator
• Junior Developer

📊 **Status:** Actively looking
⭐ **Open to:** Remote, Hybrid, On-site
📍 **Location:** Addis Ababa / Remote

**Key Skills:** Python, Networking, Flutter, Docker
        """
        await query.message.reply_text(text)
        
    elif query.data == "projects":
        text = "🚀 **Featured Projects:**\n\n"
        for i, project in enumerate(portfolio_data['projects'], 1):
            text += f"{i}. {project['name']}\n"
        await query.message.reply_text(text)
        
    elif query.data == "skills":
        text = "🔧 **Technical Skills:**\n\n"
        for category, skills in portfolio_data['skills'].items():
            text += f"**{category.title()}:** {', '.join(skills[:3])}\n"
        await query.message.reply_text(text)
        
    elif query.data == "cv":
        await query.message.reply_text(
            "📄 **Let's create your CV!**\n\n"
            "Please answer these questions:\n"
            "1. What job title are you applying for?\n"
            "2. What company?\n"
            "3. What are the key requirements?"
        )
        context.user_data['cv_step'] = 'job_title'
        
    elif query.data == "cover":
        await query.message.reply_text(
            "✉️ **Let's create your cover letter!**\n\n"
            "Please answer these questions:\n"
            "1. What job title are you applying for?\n"
            "2. What company?\n"
            "3. What are the key requirements?"
        )
        context.user_data['cover_step'] = 'job_title'
        
    elif query.data == "portfolio":
        keyboard = [[InlineKeyboardButton("🌐 Visit Portfolio", url=PORTFOLIO_URL)]]
        await query.message.reply_text(
            "Check out my portfolio website:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# ==================== MAIN ====================
if __name__ == "__main__":
    print("Starting bot with HTML/CSS CV generator...")
    print(f"Telegram Token: {TELEGRAM_TOKEN[:5]}...")
    print(f"Gemini API Key: {GEMINI_API_KEY[:5]}...")
    
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("about", about))
    app.add_handler(CommandHandler("portfolio", portfolio_command))
    app.add_handler(CommandHandler("contact", contact))
    app.add_handler(CommandHandler("job", job_status))
    app.add_handler(CommandHandler("projects", projects))
    app.add_handler(CommandHandler("skills", skills))
    app.add_handler(CommandHandler("createcv", createcv))
    app.add_handler(CommandHandler("createcover", createcover))
    
    # Message and button handlers
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("✅ Bot is running with professional HTML/CSS CV generation!")
    print("Commands: /start, /help, /about, /portfolio, /contact, /job, /projects, /skills, /createcv, /createcover")
    print("✅ All buttons working!")
    print("✅ CVs now use modern HTML/CSS templates!")
    app.run_polling()
