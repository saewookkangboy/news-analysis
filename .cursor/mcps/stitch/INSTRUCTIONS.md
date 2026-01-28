# Stitch MCP Server

Universal MCP Server for Google Stitch. Connect AI agents to your UI designs.

## Overview

Stitch is an experimental AI-powered design tool from Google Labs that helps you:
- Generate UI from natural language
- Generate UI from images/wireframes
- Rapid iteration with multiple design variants
- Export to development (React and Tailwind code)

## Available Tools

### Design Context & Generation
- `extract_design_context`: Scans a screen to extract "Design DNA" (Fonts, Colors, Layouts)
- `generate_screen_from_text`: Generates a NEW screen based on your prompt (and context)
- `fetch_screen_code`: Downloads the raw HTML/Frontend code of a screen
- `fetch_screen_image`: Downloads the high-res screenshot of a screen

### Project Management
- `create_project`: Creates a new workspace/project folder
- `list_projects`: Lists all your available Stitch projects
- `get_project`: Retrieves details of a specific project

### Screen Management
- `list_screens`: Lists all screens within a specific project
- `get_screen`: Gets metadata for a specific screen

## Pro Tip: The "Designer Flow"

To generate consistent UI, use this 2-step flow:
1. Extract: "Get design context from the Home Screen..."
2. Generate: "Using that context, generate a Chat Screen..."

This ensures your new screen matches your existing design system perfectly.

## Setup Requirements

1. Google Cloud project with Stitch API enabled
2. Application Default Credentials configured
3. GOOGLE_CLOUD_PROJECT environment variable set
