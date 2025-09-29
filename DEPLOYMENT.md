# Deployment Instructions / Քայլարկման Հրահանգներ

## GitHub Pages Setup / GitHub Pages Կարգավորում

### Option 1: Static Version (Recommended) / Տարբերակ 1: Ստատիկ Տարբերակ (Առաջարկվող)

1. Go to your repository settings: https://github.com/lethifold222/osm-map-processor/settings
2. Scroll down to "Pages" section
3. Under "Source", select "Deploy from a branch"
4. Choose "main" branch and "/ (root)" folder
5. Click "Save"
6. Your app will be available at: https://lethifold222.github.io/osm-map-processor

### Option 2: Heroku Deployment / Տարբերակ 2: Heroku Քայլարկում

1. Create a Heroku account at https://heroku.com
2. Install Heroku CLI
3. Run these commands:
```bash
heroku create your-app-name
git push heroku main
heroku open
```

### Option 3: Other Hosting Services / Տարբերակ 3: Այլ Հոստինգ Ծառայություններ

The application can be deployed on:
- **Vercel**: Connect your GitHub repository
- **Netlify**: Drag and drop the static_version folder
- **Railway**: Connect GitHub repository
- **Render**: Deploy from GitHub

## Features Available / Հասանելի Հնարավորություններ

### Static Version / Ստատիկ Տարբերակ
- ✅ Armenian language interface
- ✅ File upload and basic analysis
- ✅ Interactive map display
- ✅ Responsive design
- ❌ Server-side processing
- ❌ Advanced analysis
- ❌ Export functionality

### Full Version / Լրիվ Տարբերակ
- ✅ All static features
- ✅ Complete OSM data analysis
- ✅ Export to JSON/CSV
- ✅ Interactive filtering
- ✅ PDF report generation
- ✅ Real-time map updates

## Local Development / Տեղական Զարգացում

```bash
# Clone repository
git clone https://github.com/lethifold222/osm-map-processor.git
cd osm-map-processor

# Install dependencies
pip install -r requirements.txt

# Run web application
python web_app.py

# Open browser to http://localhost:8080
```

## Repository Structure / Ռեպոզիտորի Կառուցվածք

```
osm-map-processor/
├── index.html              # Static version for GitHub Pages
├── web_app.py              # Full Flask application
├── static_app.py           # Script to generate static version
├── templates/              # HTML templates
├── app/                    # Core application modules
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
└── static_version/        # Generated static files
```
