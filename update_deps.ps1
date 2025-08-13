# Update Python dependencies
pip install --upgrade -r requirements.txt

# Update frontend dependencies
Set-Location copilotkit-frontend
yarn upgrade
Set-Location ..
