## 플러그인 설치목록
	
WordPress REST API Authentication

## 환경 세팅 절차

- wp-admin 으로 접속 후 설정 -> 고유주소 설정 -> 고유주소 구조를 글 이름 으로 설정

## .htaccess setting : 아래의 내용을 .htaccess에 붙여넣으세요.
```
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteRule .* - [E=HTTP_AUTHORIZATION:%{HTTP:Authorization}]
RewriteBase /wp/
RewriteRule ^index\.php$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /wp/index.php [L]
CheckURL On  # 14 , 15 , 16 줄 추가
ServerEncoding UTF-8 
ClientEncoding EUC-KR 
</IfModule>
```
