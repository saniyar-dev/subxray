# Xray Subscription Parser & Config Generator

<p align="center"> <img src="https://www.google.com/search?q=https://raw.githubusercontent.com/XTLS/Xray-core/main/assets/xray.png" alt="Xray Logo" width="150"/> </p>

<p align="center"> A simple, powerful command-line tool to fetch proxy configurations from subscription links and convert them into individual JSON files for Xray-core. </p>

## What is this?

This project was born out of the frustration of manually converting proxy share links (like those for VLESS, VMess, Trojan, etc.) into the JSON format required by command-line clients and servers.

This tool automates the entire process. It takes a subscription URL, fetches all the share links, intelligently parses each one, and saves it as a properly formatted `outbound` JSON configuration file. It's designed to be a universal tool that supports a wide variety of protocols and transport settings, including `REALITY`.

## How to Use

You have two options: use the pre-compiled executable for simplicity, or run the script directly with Python for more flexibility.

### Option 1: Download the Executable (Recommended for most users)

This is the easiest way. No need to install Python or any dependencies.

1.  Go to the [**Releases**](https://www.google.com/search?q=https://github.com/YOUR_USERNAME/YOUR_REPO/releases "null") page of this repository.
    
2.  Download the executable for your operating system (e.g., `xray-parser-win.exe`, `xray-parser-linux`, `xray-parser-macos`).
    
3.  Open your terminal or command prompt, navigate to where you downloaded the file, and run it.
    

**Basic Usage:**

    ./xray-parser-linux "YOUR_SUBSCRIPTION_URL"
    

**To omit the first link** (often a usage stats link):

    ./xray-parser-win.exe --omit-first "YOUR_SUBSCRIPTION_URL"
    

_(Use_ `-o` for _the short version)_

### Option 2: Run with Python (For developers)

1.  Make sure you have Python 3.6+ installed.
    
2.  Clone this repository:
    
        git clone [https://github.com/YOUR_USERNAME/YOUR_REPO.git](https://github.com/YOUR_USERNAME/YOUR_REPO.git)
        cd YOUR_REPO
        
    
3.  Install the required dependency:
    
        pip install -r requirements.txt
        
    
4.  Run the script:
    
        python fetch_and_parse.py "YOUR_SUBSCRIPTION_URL"
        
    

## Use Cases

This tool is useful for anyone who:

-   Runs Xray-core on a server or router and needs to quickly add new configurations.
    
-   Uses command-line clients that require JSON configuration files.
    
-   Wants to automate the process of updating a large number of proxy configurations.
    
-   Needs to inspect or debug the underlying parameters of a share link.
    
-   Wants to batch-test the connectivity of multiple servers from a subscription.
    

## Contribution Guide

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  **Fork the Project:** Click the 'Fork' button at the top right of this page.
    
2.  **Create your Feature Branch:**
    
        git checkout -b feature/AmazingFeature
        
    
3.  **Commit your Changes:**
    
        git commit -m 'Add some AmazingFeature'
        
    
4.  **Push to the Branch:**
    
        git push origin feature/AmazingFeature
        
    
5.  **Open a Pull Request:** Go back to the original repository on GitHub and click the 'New pull request' button.
    

You can also open an [issue](https://www.google.com/search?q=https://github.com/YOUR_USERNAME/YOUR_REPO/issues "null") to report a bug or suggest a new feature.

## A Hope for a Free Internet

<p align="center"> This tool is built on the principle of open access to information. We stand in solidarity with the people of Iran and everyone around the world fighting for digital freedom. </p> <p align="center"> <strong>To a free and unfiltered internet for all. #FreeInternetForIran</strong> </p>



