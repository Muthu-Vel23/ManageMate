# ManagerMate - Employee Management & Productivity Platform

ManagerMate is a comprehensive web-based employee management and productivity platform built with Flask, HTML, CSS, and SQLite. It provides a complete solution for managing projects, tasks, goals, achievements, and personal productivity with gamification features.

## 🚀 Features

### Core Modules
- **User Authentication** - Secure login, registration, and session management
- **User Profile Management** - Editable profiles with profile picture upload
- **Dashboard** - Central hub with motivational quotes, focus timer, and analytics
- **Project Management** - Create, track, and complete projects with file uploads
- **Task Management** - Organize and manage daily tasks
- **Goals Tracking** - Set and achieve personal goals with sticky-note style display
- **Analytics** - Visual performance statistics and progress tracking
- **Achievements** - Upload and showcase certificates and accomplishments
- **Gamification** - Rewards, badges, and point system for motivation
- **Notes System** - Personal note-taking functionality
- **Settings** - Theme customization and preferences

### Key Features
- 🎯 **Focus Timer** - Pomodoro-style productivity timer
- 📊 **Analytics Dashboard** - Visual charts and performance metrics
- 🏆 **Gamification System** - Points, badges, and level progression
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- 🎨 **Multiple Themes** - Light, dark, blue, and green themes
- 📁 **File Management** - Upload and manage project files and achievements
- 🔔 **Smart Notifications** - Overdue task and project alerts
- 📈 **Progress Tracking** - Visual progress indicators and completion rates

## 🛠️ Tech Stack

- **Backend**: Python Flask with Blueprints architecture
- **Frontend**: HTML5, CSS3 with animations and responsive design
- **Database**: SQLite (easily upgradeable to PostgreSQL/MySQL)
- **File Handling**: Werkzeug for secure file uploads
- **Security**: Password hashing, session management, CSRF protection

## 📦 Installation

1. **Clone the repository**
\`\`\`bash
git clone <repository-url>
cd ManagerMate
\`\`\`

2. **Install dependencies**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. **Run the application**
\`\`\`bash
python app.py
\`\`\`

4. **Access the application**
Open your browser and navigate to `http://localhost:5000`

## 🗄️ Database Schema

The application uses SQLite with the following tables:
- `users` - User account information
- `projects` - Project management data
- `tasks` - Task tracking information
- `goals` - Personal goals and deadlines
- `achievements` - Certificates and accomplishments
- `rewards` - Gamification points and badges
- `notes` - Personal notes and comments

## 🎮 Gamification System

- **Points System**: Earn points for completing tasks (10pts), projects (20pts), and goals (30pts)
- **Level Progression**: Advance through levels based on total points earned
- **Badge System**: Unlock achievements like "First Steps", "Productivity Pro", "Master Achiever"
- **Progress Tracking**: Visual progress bars and completion statistics

## 🎨 Themes

ManagerMate supports multiple themes:
- **Light Theme** - Clean, bright interface
- **Dark Theme** - Easy on the eyes for low-light environments
- **Blue Theme** - Professional blue color scheme
- **Green Theme** - Nature-inspired green palette

## 📱 Responsive Design

The application is fully responsive and optimized for:
- Desktop computers (1200px+)
- Tablets (768px - 1199px)
- Mobile phones (320px - 767px)

## 🔒 Security Features

- Password hashing using Werkzeug
- Session-based authentication
- Secure file upload handling
- SQL injection prevention
- CSRF protection ready

## 🚀 Future Enhancements

- Calendar integration for task scheduling
- Team collaboration features
- Email notifications
- Data export functionality
- Advanced analytics and reporting
- Mobile app development
- Integration with external tools

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For support and questions, please open an issue in the repository.

---

**ManagerMate** - Empowering productivity through intelligent task management and gamification! 🚀
