#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// Create a simple SVG icon
const iconSvg = `<svg width="1024" height="1024" viewBox="0 0 1024 1024" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect width="1024" height="1024" rx="200" fill="#2196F3"/>
<path d="M300 300 L724 300 L724 724 L300 724 Z" fill="white" opacity="0.9"/>
<circle cx="512" cy="400" r="60" fill="#2196F3"/>
<rect x="400" y="500" width="224" height="20" rx="10" fill="#2196F3"/>
<rect x="400" y="540" width="180" height="20" rx="10" fill="#2196F3"/>
<rect x="400" y="580" width="200" height="20" rx="10" fill="#2196F3"/>
<rect x="400" y="620" width="160" height="20" rx="10" fill="#2196F3"/>
</svg>`;

// Create a simple splash screen SVG
const splashSvg = `<svg width="1024" height="1024" viewBox="0 0 1024 1024" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect width="1024" height="1024" fill="#2196F3"/>
<text x="512" y="400" text-anchor="middle" font-family="Arial, sans-serif" font-size="80" font-weight="bold" fill="white">SENTINEL</text>
<text x="512" y="500" text-anchor="middle" font-family="Arial, sans-serif" font-size="40" fill="white" opacity="0.8">AI Agent Command Center</text>
</svg>`;

// Create a simple favicon SVG
const faviconSvg = `<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
<rect width="32" height="32" rx="6" fill="#2196F3"/>
<path d="M8 8 L24 8 L24 24 L8 24 Z" fill="white" opacity="0.9"/>
<circle cx="16" cy="12" r="2" fill="#2196F3"/>
<rect x="12" y="16" width="8" height="1" rx="0.5" fill="#2196F3"/>
<rect x="12" y="18" width="6" height="1" rx="0.5" fill="#2196F3"/>
<rect x="12" y="20" width="7" height="1" rx="0.5" fill="#2196F3"/>
</svg>`;

function createPlaceholderAssets() {
  const assetsDir = path.join(__dirname, 'assets');
  
  // Create assets directory if it doesn't exist
  if (!fs.existsSync(assetsDir)) {
    fs.mkdirSync(assetsDir, { recursive: true });
  }

  // Create placeholder files
  const assets = [
    { name: 'icon.png', content: 'Placeholder icon - replace with actual PNG' },
    { name: 'splash.png', content: 'Placeholder splash - replace with actual PNG' },
    { name: 'adaptive-icon.png', content: 'Placeholder adaptive icon - replace with actual PNG' },
    { name: 'favicon.png', content: 'Placeholder favicon - replace with actual PNG' },
    { name: 'icon.svg', content: iconSvg },
    { name: 'splash.svg', content: splashSvg },
    { name: 'favicon.svg', content: faviconSvg },
  ];

  assets.forEach(asset => {
    const filePath = path.join(assetsDir, asset.name);
    fs.writeFileSync(filePath, asset.content);
    console.log(`✅ Created ${asset.name}`);
  });

  console.log('\n📝 Note: PNG files are placeholders. Replace them with actual images:');
  console.log('   - icon.png: 1024x1024 app icon');
  console.log('   - splash.png: 1024x1024 splash screen');
  console.log('   - adaptive-icon.png: 1024x1024 Android adaptive icon');
  console.log('   - favicon.png: 32x32 web favicon');
  console.log('\nSVG files are provided as templates for creating PNG assets.');
}

createPlaceholderAssets(); 