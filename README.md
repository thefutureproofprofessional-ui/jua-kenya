# 🇰🇪 Jua Kenya - Service Information Platform

A modern, responsive web application providing easy access to Kenyan service information including government services, banking, utilities, and more.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Features

- 🔍 **Smart Search** - Find services quickly with intelligent search
- 📱 **Responsive Design** - Works perfectly on mobile, tablet, and desktop
- 🔄 **Auto-Updates** - Information updated twice weekly via N8N
- 🎨 **Modern UI** - Clean, intuitive interface with smooth animations
- ⚡ **Fast Performance** - Optimized for speed and efficiency

## 📁 Project Structure
```
jua-kenya/
├── app.py                    # Flask application
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── .env.example             # Environment variables template
├── templates/
│   └── index.html           # Main HTML template
└── README.md               # This file
```

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/YOUR_USERNAME/jua-kenya.git
cd jua-kenya
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run the application**
```bash
python app.py
```

5. **Visit** `http://localhost:5000` 🎉

### Docker Deployment
```bash
# Build the image
docker build -t jua-kenya .

# Run the container
docker run -p 5000:5000 jua-kenya
```

### Deploy on Coolify

1. Create new service in Coolify
2. Select "Git Repository"
3. Connect your GitHub repo
4. Set environment variables from `.env.example`
5. Deploy! 🚀

## 🔧 N8N Workflow Setup

1. In N8N, go to **Workflows** → **Import from File**
2. Upload `n8n-workflow.json`
3. Set environment variable: `WEBSITE_API_URL=https://your-domain.com`
4. Configure schedule (default: Monday & Thursday at 9 AM)
5. Activate the workflow ✅

## 📡 API Endpoints

### `GET /api/services`
Get all services with optional filtering

**Query Parameters:**
- `category` - Filter by category (Government, Banking, etc.)
- `search` - Search in service names and requirements

**Example:**
```bash
curl https://your-domain.com/api/services?category=Government
```

### `POST /api/services`
Update services (called by N8N automation)

**Body:**
```json
{
  "services": [
    {
      "service_name": "Passport Application",
      "category": "Government",
      "paybill_number": "222222",
      "cost": "Ksh 7,550"
    }
  ]
}
```

### `GET /api/categories`
Get list of all available categories

## 🛠️ Technologies Used

- **Backend**: Flask (Python 3.11)
- **Frontend**: HTML5, Tailwind CSS, Vanilla JavaScript
- **Automation**: N8N
- **Deployment**: Docker, Coolify
- **Version Control**: Git, GitHub

## 📊 Service Categories

- 🏛️ Government Services
- 🏦 Banking & Mobile Money
- 💧 Utilities (Water, Electricity)
- 📺 Entertainment (TV subscriptions)
- 💰 Finance (SACCOs, Loans)
- 🎓 Education

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

For issues or questions, please open an issue on GitHub.

---

**Built with ❤️ for Kenyans**
```

4. Commit message: `Update README with full documentation`
5. Click **"Commit changes"**

---

### **Step 3: Final Repository Structure**

Your GitHub repo should now look like this:
```
jua-kenya/
├── .gitignore
├── README.md
├── app.py
├── requirements.txt
├── Dockerfile
├── .env.example
└── templates/
    └── index.html
