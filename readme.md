# wordpress-auto-blog

The wordpress-auto-blog is a PyQt5-based application that automatically generates and publishes blog posts on user-specified topics.

## Usage

1. **Enter Topics**: Input topics for blog posts in the "Topic" field, separated by commas.
2. **Enter API Key**: Provide your OpenAI API key in the "API Key" field.
3. **WordPress Account Info**: Fill in your WordPress username, password, and site URL.
4. **Select Number of Posts**: Choose the number of posts to publish using the spin box.
5. **Enable Auto Posting (Optional)**: Set the interval for automatic posting.
6. **Run**: Click "Run" to start generating and publishing posts.

## Notes

- Ensure correct OpenAI API key and WordPress account info.
- Dependencies: requests, PyQt5, openai.
- Install dependencies: `pip install requests PyQt5 openai`.

## WordPress Plugin & Settings

1. **Install Plugins**: WordPress REST API Authentication.
2. **Configure Settings**: Set unique address structure to post name.

## .htaccess Settings

Add the following to your .htaccess file:
```apacheconf
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]
RewriteBase /wp/
RewriteRule ^index\.php$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /wp/index.php [L]
CheckURL On
ServerEncoding UTF-8 
ClientEncoding EUC-KR 
</IfModule>
```
