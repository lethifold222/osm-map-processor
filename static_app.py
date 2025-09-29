#!/usr/bin/env python3
"""
Static version of OSM Map Processor for GitHub Pages.
This version works without server-side processing.
"""

import json
import os
import sys
from pathlib import Path

def create_static_app():
    """Create a static version of the app for GitHub Pages."""
    
    # Create static directory structure
    static_dir = Path("static_version")
    static_dir.mkdir(exist_ok=True)
    
    # Copy templates to static version
    templates_dir = static_dir / "templates"
    templates_dir.mkdir(exist_ok=True)
    
    # Create index.html for static version
    index_content = """<!DOCTYPE html>
<html lang="hy">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSM Քարտեզի Մշակիչ</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        .hero-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 100px 0;
        }
        .feature-card {
            transition: transform 0.3s;
            border: none;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .feature-card:hover {
            transform: translateY(-5px);
        }
        .upload-area {
            border: 2px dashed #dee2e6;
            border-radius: 10px;
            padding: 60px 20px;
            text-align: center;
            transition: border-color 0.3s;
            cursor: pointer;
        }
        .upload-area:hover {
            border-color: #007bff;
        }
        .upload-area.dragover {
            border-color: #007bff;
            background-color: #f8f9fa;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-map-marked-alt"></i> OSM Քարտեզի Մշակիչ
            </a>
            <div class="navbar-nav ms-auto">
                <a class="nav-link" href="#home">Գլխավոր</a>
                <a class="nav-link" href="#features">Հնարավորություններ</a>
                <a class="nav-link" href="#upload">Վերբեռնում</a>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero-section" id="home">
        <div class="container text-center">
            <h1 class="display-4 mb-4">
                <i class="fas fa-map-marked-alt"></i> OSM Քարտեզի Մշակիչ
            </h1>
            <p class="lead mb-4">
                Վերլուծեք OpenStreetMap տվյալները հեշտությամբ: Վերբեռնեք .osm ֆայլեր և ստացեք մանրամասն տեղեկություններ աշխարհագրական տվյալների մասին:
            </p>
            <p class="mb-0">
                <strong>Ճարտարապետական կախվածություն չկա - աշխատում է ամենուր!</strong>
            </p>
        </div>
    </section>

    <!-- Features Section -->
    <section class="py-5" id="features">
        <div class="container">
            <div class="row text-center mb-5">
                <div class="col-lg-12">
                    <h2 class="mb-4">Հնարավորություններ</h2>
                    <p class="lead">Հզոր OSM տվյալների վերլուծության հնարավորություններ</p>
                </div>
            </div>
            
            <div class="row">
                <div class="col-lg-4 col-md-6 mb-4">
                    <div class="card feature-card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-upload fa-3x text-primary mb-3"></i>
                            <h5 class="card-title">Հեշտ Վերբեռնում</h5>
                            <p class="card-text">Վերբեռնեք .osm ֆայլեր ուղղակիորեն ձեր վեբ բրաուզերի միջոցով: Տեղադրում չի պահանջվում:</p>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-4 col-md-6 mb-4">
                    <div class="card feature-card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-chart-bar fa-3x text-success mb-3"></i>
                            <h5 class="card-title">Մանրամասն Վերլուծություն</h5>
                            <p class="card-text">Ստացեք համապարփակ վիճակագրություն nodes, ways, relations և աշխարհագրական հատկանիշների մասին:</p>
                        </div>
                    </div>
                </div>
                
                <div class="col-lg-4 col-md-6 mb-4">
                    <div class="card feature-card h-100">
                        <div class="card-body text-center">
                            <i class="fas fa-download fa-3x text-warning mb-3"></i>
                            <h5 class="card-title">Արդյունքների Էքսպորտ</h5>
                            <p class="card-text">Էքսպորտեք ձեր վերլուծության արդյունքները JSON կամ CSV ֆորմատով հետագա մշակման համար:</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Upload Section -->
    <section class="py-5 bg-light" id="upload">
        <div class="container">
            <div class="row justify-content-center">
                <div class="col-lg-8">
                    <div class="text-center mb-5">
                        <h2>Վերբեռնել OSM Ֆայլ</h2>
                        <p class="lead">Ընտրեք .osm ֆայլ վերլուծության համար</p>
                    </div>
                    
                    <div class="upload-area" id="uploadArea">
                        <i class="fas fa-cloud-upload-alt fa-4x text-muted mb-3"></i>
                        <h4>Քաշեք և գցեք ձեր OSM ֆայլը այստեղ</h4>
                        <p class="text-muted mb-4">կամ կտտացրեք ընտրելու համար</p>
                        
                        <input type="file" id="fileInput" accept=".osm,.xml" style="display: none;">
                        
                        <button type="button" class="btn btn-primary btn-lg" onclick="document.getElementById('fileInput').click()">
                            <i class="fas fa-folder-open"></i> Ընտրել Ֆայլ
                        </button>
                        
                        <div class="mt-3">
                            <small class="text-muted">
                                Աջակցվող ֆորմատներ: .osm, .xml<br>
                                Առավելագույն ֆայլի չափս: 100MB
                            </small>
                        </div>
                        
                        <div id="fileInfo" class="mt-3" style="display: none;">
                            <div class="alert alert-info">
                                <i class="fas fa-file"></i> <span id="fileName"></span>
                                <button type="button" class="btn btn-success btn-sm ms-3" onclick="analyzeFile()">
                                    <i class="fas fa-play"></i> Վերլուծել Ֆայլը
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Results Section -->
    <section class="py-5" id="results" style="display: none;">
        <div class="container">
            <div class="row">
                <div class="col-lg-12">
                    <h2 class="text-center mb-4">Վերլուծության Արդյունքներ</h2>
                    <div id="analysisResults"></div>
                </div>
            </div>
        </div>
    </section>

    <!-- Map Section -->
    <section class="py-5 bg-light" id="mapSection" style="display: none;">
        <div class="container">
            <div class="row">
                <div class="col-lg-12">
                    <h2 class="text-center mb-4">Ինտերակտիվ Քարտեզ</h2>
                    <div id="map" style="height: 500px; border-radius: 10px;"></div>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="bg-dark text-white py-4">
        <div class="container text-center">
            <p>&copy; 2024 OSM Քարտեզի Մշակիչ. Բոլոր իրավունքները պաշտպանված են:</p>
        </div>
    </footer>

    <!-- Scripts -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/leaflet@1.7.1/dist/leaflet.js"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/leaflet@1.7.1/dist/leaflet.css" />
    
    <script>
        let currentFile = null;
        let analysisData = null;

        // File upload handling
        document.getElementById('fileInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                currentFile = file;
                document.getElementById('fileName').textContent = file.name + ' (' + (file.size / 1024 / 1024).toFixed(2) + ' MB)';
                document.getElementById('fileInfo').style.display = 'block';
            }
        });

        // Drag and drop handling
        const uploadArea = document.getElementById('uploadArea');
        
        uploadArea.addEventListener('dragover', function(e) {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', function(e) {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.name.endsWith('.osm') || file.name.endsWith('.xml')) {
                    currentFile = file;
                    document.getElementById('fileName').textContent = file.name + ' (' + (file.size / 1024 / 1024).toFixed(2) + ' MB)';
                    document.getElementById('fileInfo').style.display = 'block';
                } else {
                    alert('Խնդրում ենք ընտրել .osm կամ .xml ֆայլ:');
                }
            }
        });

        // Click to upload
        uploadArea.addEventListener('click', function() {
            document.getElementById('fileInput').click();
        });

        // Analyze file function
        function analyzeFile() {
            if (!currentFile) {
                alert('Խնդրում ենք ընտրել ֆայլ:');
                return;
            }

            const reader = new FileReader();
            reader.onload = function(e) {
                try {
                    // Parse OSM XML
                    const parser = new DOMParser();
                    const xmlDoc = parser.parseFromString(e.target.result, 'text/xml');
                    
                    // Basic analysis
                    const nodes = xmlDoc.getElementsByTagName('node');
                    const ways = xmlDoc.getElementsByTagName('way');
                    const relations = xmlDoc.getElementsByTagName('relation');
                    
                    analysisData = {
                        nodes: nodes.length,
                        ways: ways.length,
                        relations: relations.length,
                        total: nodes.length + ways.length + relations.length
                    };
                    
                    displayResults();
                    
                } catch (error) {
                    alert('Սխալ ֆայլի վերլուծման ժամանակ: ' + error.message);
                }
            };
            
            reader.readAsText(currentFile);
        }

        // Display results
        function displayResults() {
            const resultsSection = document.getElementById('results');
            const mapSection = document.getElementById('mapSection');
            
            resultsSection.style.display = 'block';
            mapSection.style.display = 'block';
            
            const resultsHtml = `
                <div class="row mb-4">
                    <div class="col-lg-3 col-md-6 mb-3">
                        <div class="card stats-card">
                            <div class="card-body text-center">
                                <i class="fas fa-dot-circle fa-2x mb-2 text-primary"></i>
                                <h4>${analysisData.nodes.toLocaleString()}</h4>
                                <p class="mb-0">Nodes</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-3 col-md-6 mb-3">
                        <div class="card stats-card">
                            <div class="card-body text-center">
                                <i class="fas fa-route fa-2x mb-2 text-info"></i>
                                <h4>${analysisData.ways.toLocaleString()}</h4>
                                <p class="mb-0">Ways</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-3 col-md-6 mb-3">
                        <div class="card stats-card">
                            <div class="card-body text-center">
                                <i class="fas fa-sitemap fa-2x mb-2 text-success"></i>
                                <h4>${analysisData.relations.toLocaleString()}</h4>
                                <p class="mb-0">Relations</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-lg-3 col-md-6 mb-3">
                        <div class="card stats-card">
                            <div class="card-body text-center">
                                <i class="fas fa-layer-group fa-2x mb-2 text-warning"></i>
                                <h4>${analysisData.total.toLocaleString()}</h4>
                                <p class="mb-0">Ընդհանուր Տարրեր</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            document.getElementById('analysisResults').innerHTML = resultsHtml;
            
            // Initialize map
            initializeMap();
            
            // Scroll to results
            document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
        }

        // Initialize map
        function initializeMap() {
            const map = L.map('map').setView([40.1776, 44.5126], 10); // Yerevan coordinates
            
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(map);
            
            // Add a marker for demonstration
            L.marker([40.1776, 44.5126]).addTo(map)
                .bindPopup('Օրինակի համար: Երևան, Հայաստան')
                .openPopup();
        }
    </script>
</body>
</html>"""
    
    # Write static index.html
    with open(static_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(index_content)
    
    print(f"✅ Static version created in {static_dir}/index.html")
    print("📁 This file can be uploaded to GitHub Pages or any static hosting service")
    print("🌐 To use on GitHub Pages:")
    print("   1. Push this repository to GitHub")
    print("   2. Enable GitHub Pages in repository settings")
    print("   3. Select 'Deploy from a branch' and choose 'main'")
    print("   4. The app will be available at: https://lethifold222.github.io/osm-map-processor")

if __name__ == "__main__":
    create_static_app()
