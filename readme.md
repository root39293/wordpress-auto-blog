# wp-ap

The Auto Posting program is a PyQt5-based application that automatically generates and publishes blog posts on user-specified topics.

## Usage

1. **Login**: When the program is executed, a login dialog will be displayed. Enter your username and password to log in. Currently, the example accepts "root" as the username and "password@" as the password.

2. **Enter Topics**: Enter the topics for which you want to generate blog posts in the "Topic" field. Separate multiple topics with commas. Example: Topic 1, Topic 2, Topic 3

3. **Enter API Key**: Enter your OpenAI API key in the "API Key" field. This key is required to use the OpenAI GPT-3.5 model.

4. **Enter WordPress Account Information**: Enter your WordPress username and password in the "WordPress Username" and "WordPress Password" fields, respectively. This information is used to publish the posts.

5. **Enter WordPress URL**: Enter the URL of your WordPress site in the "WordPress URL" field. The URL should not end with a '/'.

6. **Select Number of Postings**: Use the "Number of Posting" spin box to select the number of posts you want to publish. The default value is 2.

7. **Enable Auto Posting (Optional)**: Check the "Enable Auto Posting" checkbox and set the auto posting interval to automatically publish posts at regular intervals.

8. **Execution**: Click the "Run" button to start the process of generating and publishing the posts.

## Notes

- Make sure to enter the correct OpenAI API key and WordPress account information before using the program.
- User authentication is currently implemented by comparing the provided username and password with a simple example. You need to implement a real user authentication logic.
- This program has the following dependencies: requests, PyQt5, openai, googletrans.
- To install the dependencies, use the pip command. For example, you can install the dependencies with the following command:


## Plugin installation list

- Install WordPress REST API Authentication
- Setting up ID/PW Authentication

## Environment setting procedure

1. Connect to wp-admin and go to Settings -> Set unique address -> Set unique address structure to post name.

## .htaccess setting

Paste the following content into the server path .htaccess:

```apacheconf
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]
RewriteBase /wp/
RewriteRule ^index\.php$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /wp/index.php [L]
CheckURL On # 14 , 15 , 16 Add lines 14 , 15 , 16
ServerEncoding UTF-8 
ClientEncoding EUC-KR 
</IfModule>
