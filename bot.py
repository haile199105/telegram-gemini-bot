import os
import tempfile
from datetime import datetime
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, CommandHandler, ContextTypes, CallbackQueryHandler
from fpdf import FPDF
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
    'experience': '1+ year teaching, 6+ months field experience',
    'skills': {
        'networking': ['Cisco IOS', 'Routing', 'Switching', 'Firewalls', 'TCP/IP'],
        'programming': ['Python', 'Java', 'C++', 'JavaScript', 'TypeScript'],
        'mobile': ['Flutter', 'Firebase', 'Dart'],
        'devops': ['Docker', 'Linux'],
        'it_support': ['Hardware', 'OS Support', 'Diagnostics']
    },
    'projects': [
        'Network Configuration Lab Setup',
        'Flutter-Based Mobile Application',
        'GPS Installation & Tracking Workflow'
    ]
}

# ==================== AUTHORIZATION ====================
def is_authorized(user_id):
    return user_id == YOUR_ID

# ==================== PDF GENERATOR ====================
class PDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, f'Job Application - {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_cv_pdf(job_title, company, requirements):
    pdf = PDF()
    pdf.add_page()
    
    # ===== HEADER =====
    pdf.set_font('Helvetica', 'B', 24)
    pdf.cell(0, 15, f"{portfolio_data['name']}", 0, 1, 'C')
    
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, f"{portfolio_data['title']}", 0, 1, 'C')
    pdf.ln(5)
    
    # ===== SUMMARY =====
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, "SUMMARY", 0, 1)
    pdf.set_font('Helvetica', '', 11)
    summary = f"A dedicated and passionate {job_title} with experience in {portfolio_data['experience']}. Skilled in {', '.join(portfolio_data['skills']['programming'][:3])} and dedicated to delivering high-quality results. Committed to continuous learning and teamwork to achieve organizational goals."
    pdf.multi_cell(0, 6, summary)
    pdf.ln(5)
    
    # ===== TWO COLUMN LAYOUT =====
    # Set starting positions for columns
    col1_x = pdf.get_x()
    col1_y = pdf.get_y()
    col2_x = 110  # Right column starting position
    col2_y = col1_y
    
    # ===== LEFT COLUMN =====
    pdf.set_xy(col1_x, col1_y)
    
    # PERSONAL DETAILS
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "PERSONAL DETAILS", 0, 1)
    pdf.set_font('Helvetica', '', 10)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(25, 6, "Phone", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, "+251 975 101 559", 0, 1)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(25, 6, "Email", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, "haileyesusshibru19@gmail.com", 0, 1)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(25, 6, "Location", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 6, portfolio_data['location'], 0, 1)
    pdf.ln(5)
    
    # SKILLS
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "SKILLS", 0, 1)
    pdf.set_font('Helvetica', '', 10)
    
    # Programming Skills
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(30, 5, "Programming", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, f": {', '.join(portfolio_data['skills']['programming'][:4])}", 0, 1)
    
    # Networking
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(30, 5, "Networking", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, f": {', '.join(portfolio_data['skills']['networking'][:4])}", 0, 1)
    
    # Mobile Dev
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(30, 5, "Mobile Dev", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, f": {', '.join(portfolio_data['skills']['mobile'][:3])}", 0, 1)
    
    # DevOps
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(30, 5, "DevOps", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, f": {', '.join(portfolio_data['skills']['devops'][:2])}", 0, 1)
    pdf.ln(5)
    
    # LANGUAGES
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, "LANGUAGES", 0, 1)
    pdf.set_font('Helvetica', '', 10)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(30, 5, "Amharic", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, ": Native", 0, 1)
    
    pdf.set_font('Helvetica', 'B', 10)
    pdf.cell(30, 5, "English", 0, 0)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 5, ": Proficient", 0, 1)
    pdf.ln(5)
    
    # ===== RIGHT COLUMN =====
    pdf.set_xy(col2_x, col2_y)
    
    # EXPERIENCE
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, "EXPERIENCE", 0, 1)
    
    # IT Instructor
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 6, "IT Instructor", 0, 1)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.cell(0, 5, "Higher Education Institution | Present", 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(5)
    pdf.cell(0, 5, "- Deliver networking and programming courses", 0, 1)
    pdf.cell(5)
    pdf.cell(0, 5, "- Guide practical lab sessions for technical skill development", 0, 1)
    pdf.cell(5)
    pdf.cell(0, 5, "- Prepare comprehensive training materials and assessments", 0, 1)
    pdf.ln(3)
    
    # IT Intern
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 6, "IT Intern", 0, 1)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.cell(0, 5, "Koye Feche Sub-city Science & Technology Bureau | 6 Months", 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(5)
    pdf.cell(0, 5, "- Configured routers and switches for local network infrastructure", 0, 1)
    pdf.cell(5)
    pdf.cell(0, 5, "- Implemented firewall setups to ensure network security", 0, 1)
    pdf.cell(5)
    pdf.cell(0, 5, "- Provided server and database support", 0, 1)
    pdf.ln(3)
    
    # GPS Technician
    pdf.set_font('Helvetica', 'B', 11)
    pdf.cell(0, 6, "GPS Technician", 0, 1)
    pdf.set_font('Helvetica', 'I', 9)
    pdf.cell(0, 5, "Technical Services | 6+ Months", 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(5)
    pdf.cell(0, 5, "- Installed vehicle tracking systems in diverse fleet environments", 0, 1)
    pdf.cell(5)
    pdf.cell(0, 5, "- Diagnosed connectivity and hardware issues in the field", 0, 1)
    pdf.ln(5)
    
    # PROJECTS
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, "PROJECTS", 0, 1)
    
    for i, project in enumerate(portfolio_data['projects']):
        pdf.set_font('Helvetica', 'B', 11)
        pdf.cell(0, 6, project, 0, 1)
        pdf.set_font('Helvetica', 'I', 9)
        pdf.cell(0, 5, "Personal Project", 0, 1)
        pdf.set_font('Helvetica', '', 10)
        pdf.cell(5)
        pdf.cell(0, 5, "- Designed and implemented using modern technologies", 0, 1)
        pdf.cell(5)
        pdf.cell(0, 5, "- Demonstrated problem-solving and technical skills", 0, 1)
        pdf.ln(3)
    
    # ===== JOB SPECIFIC SECTION =====
    pdf.ln(5)
    pdf.set_font('Helvetica', 'B', 12)
    pdf.cell(0, 8, f"APPLICATION FOR {company.upper()}", 0, 1)
    pdf.set_font('Helvetica', '', 10)
    pdf.multi_cell(0, 5, f"This CV is tailored for the {job_title} position. Key requirements addressed: {requirements}")
    
    # Save to temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    pdf.output(temp_file.name)
    return temp_file.name

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
        f"I'm your AI job assistant. What would you like help with?",
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
**Experience:** {portfolio_data['experience']}

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
    
    text = """
📬 **Contact Information**

📧 **Email:** haileyesusshibru19@gmail.com
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
        text += f"{i}. {project}\n"
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
            await update.message.reply_text("⏳ **Generating your CV PDF...**")
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
                        caption="📄 Your customized CV"
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
**Experience:** {portfolio_data['experience']}

I'm passionate about teaching IT and building reliable systems.
        """
        await query.message.reply_text(text)
        
    elif query.data == "contact":
        text = """
📬 **Contact Information**

📧 **Email:** haileyesusshibru19@gmail.com
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
            text += f"{i}. {project}\n"
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
    print("Starting bot with ALL features...")
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
    
    print("✅ Bot is running with ALL features!")
    print("Commands: /start, /help, /about, /portfolio, /contact, /job, /projects, /skills, /createcv, /createcover")
    print("✅ All buttons working!")
    print("✅ CV template fixed - using dashes instead of bullets")
    app.run_polling()
