# How to Get a Hugging Face API Key

Follow these simple steps to generate your API key for accessing Hugging Face's models and services:

## Step 1: Create or Log into Your Hugging Face Account
- Visit [huggingface.co](https://huggingface.co/)
- Sign up for a new account or log in to your existing account

## Step 2: Navigate to Settings
- Click on your profile picture in the top-right corner
- Click on "Access Tokens" from the dropdown menu

## Step 4: Generate a New Token
- Click on the "Create new token" button
- Enter a name for your token (e.g., "My API Project")
- Select the appropriate role/permissions:
  - "Read" for read-only access
  - "Write" for read and write access
  - "Admin" for full access to your account

## Step 5: Copy and Secure Your Token
- After clicking "Generate token," your new API key will be displayed
- Copy this token immediately as it will only be fully shown once
- Store it securely in an environment variable or password manager

---
## Setting Up Your API Key

For enhanced security and ease of use, it's recommended to set up your API key as an environment variable:

1. Create a `.env` file in the root directory of your project.
2. Add the following line to your `.env` file:

    ```bash
    HF_API_TOKEN=your_hf_api_key_here
    ```

3. Save the file.


Alternatively, you could also export the variable:
   ```bash
   export HF_API_TOKEN=your_hf_api_key_here
   ```
