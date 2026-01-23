#!/bin/bash

# Set terminal colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Transcript Analysis API Setup ===${NC}"
echo -e "${YELLOW}This script will help you set up your environment variables.${NC}"
echo

# Check if .env file exists
if [ -f .env ]; then
    echo -e "${YELLOW}An existing .env file was found.${NC}"
    read -p "Do you want to replace it? (y/n): " replace_env
    if [[ $replace_env != "y" && $replace_env != "Y" ]]; then
        echo -e "${BLUE}Setup cancelled. Using existing .env file.${NC}"
        exit 0
    fi
fi

# Copy template env file
cp env.example .env

# Get OpenAI API Key
echo
echo -e "${YELLOW}Please enter your OpenAI API Key:${NC}"
read -p "OPENAI_API_KEY: " openai_api_key

# Update .env file with the API key
if [ -n "$openai_api_key" ]; then
    # Check if OPENAI_API_KEY already exists in .env
    if grep -q "^OPENAI_API_KEY=" .env; then
        # Replace existing line
        sed -i '' "s/^OPENAI_API_KEY=.*/OPENAI_API_KEY=$openai_api_key/" .env
    else
        # Append to file
        echo "OPENAI_API_KEY=$openai_api_key" >> .env
    fi
else
    echo -e "${YELLOW}Warning: No API key provided. You'll need to add it manually to .env${NC}"
fi

# Optional: Customize other settings
echo
echo -e "${YELLOW}Would you like to customize other settings? (Default values will be used if you skip)${NC}"
read -p "Customize (y/n): " customize

if [[ $customize == "y" || $customize == "Y" ]]; then
    # OpenAI Model
    echo -e "${YELLOW}OpenAI model (default: gpt-4o-2024-08-06):${NC}"
    read -p "OPENAI_MODEL: " openai_model
    if [ -n "$openai_model" ]; then
        sed -i '' "s/^OPENAI_MODEL=.*/OPENAI_MODEL=$openai_model/" .env
    fi
    
    # Port
    echo -e "${YELLOW}API port (default: 8000):${NC}"
    read -p "PORT: " port
    if [ -n "$port" ]; then
        sed -i '' "s/^PORT=.*/PORT=$port/" .env
    fi
fi

echo
echo -e "${GREEN}Setup complete! Environment variables have been saved to .env${NC}"
echo -e "${BLUE}You can now run the API using:${NC}"
echo -e "  docker-compose up -d"
echo 