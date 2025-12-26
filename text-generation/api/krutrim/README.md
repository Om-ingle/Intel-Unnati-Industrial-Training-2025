# How to Access Krutrim Cloud API Key

Follow these steps to generate and retrieve your API key for accessing Krutrim Cloud services:

## Step 1: Register for an Account
- Visit [Krutrim Cloud Platform](https://www.olakrutrim.com/cloud).
- Click on **"Sign Up"** and create a new account using your email address.
- Verify your email address by clicking the link sent to your inbox.

## Step 2: Submit a Request for API Access
- After logging into your account, navigate to the **Developer Platform** section at [Krutrim Developers Platform](https://olakrutrim.com/developers/).
- On the left sidebar, under the "Models" section, click on "API Keys".

## Step 3: Generate New API Key
- Click on the "Create API Key".
- Provide a name for your key (optional) to help you identify it later.
- Confirm by clicking on **"Create API Key"** to generate the API key.
- **Important**: Copy the API key immediately as it will only be shown once.
- Store the key securely in an environment variable or a secure password manager.

## Setting Up Your API Key

For enhanced security and ease of use, it's recommended to set up your API key as an environment variable:

1. Create a `.env` file in the root directory of your project.
2. Add the following line to your `.env` file:

    ```bash
    KRUTRIM_CLOUD_API_KEY=your_krutrim_cloud_api_key_here
    ```

3. Save the file.


Alternatively, you could also export the variable:
   ```bash
   export KRUTRIM_CLOUD_API_KEY=your_krutrim_cloud_api_key_here
   ```
--- 

## Security Best Practices
- Never hardcode your API key directly into your codebase.
- Use environment variables or secure configuration files to store your key.
- Regularly rotate your API keys and delete unused keys.
- Restrict your API key's permissions to only the services you need.

## Additional Resources
- [Krutrim AI Studio](https://www.olakrutrim.com/ai-studio): Explore pre-trained AI models and solutions.
- [Krutrim GitHub Repository](https://github.com/ola-krutrim/ai-cloud): Access developer tools and SDKs.

