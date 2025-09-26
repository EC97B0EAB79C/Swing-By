# Swing-By

Swing-By is an Obsidian plugin that helps you process and connect relations of papers.

## Features

- Extracts BibTeX entry in a Markdown file and creates Markdown metadata.
- Creates keywords from the Markdown file using AI.
- Adds metadata and keywords to the given Markdown file.

## For Developers

This plugin is currently in development. To install it for testing and development, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/EC97B0EAB79C/Swing-By.git
    ```
2.  **Navigate to the project directory:**
    ```bash
    cd Swing-By
    ```
3.  **Install dependencies:**
    ```bash
    npm install
    ```
4.  **Build the plugin:**
    - For development (watches for changes):
      ```bash
      npm run dev
      ```
    - For production:
      ```bash
      npm run build
      ```
5.  **Install the plugin in Obsidian:**
    - Copy the `main.js`, `manifest.json` files to your Obsidian vault's `.obsidian/plugins/swing-by/` directory.
    - Reload Obsidian.
    - Enable the "Swing-By" plugin in the Obsidian settings.

## Acknowledgement

- Thank you to arXiv and Crossref for use of their open access interoperability.
